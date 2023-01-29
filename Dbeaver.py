import psycopg2
from psycopg2 import Error


class SQLdb:
    def __init__(self, db, user_db, password):
        """Метод для подключения к БД и создания таблиц"""
        self.db = db
        self.user_db = user_db
        self.password = password
        try:
            self.con = psycopg2.connect(
                database=self.db,
                user=self.user_db,
                password=self.password,
                host="localhost",
                port="5432"
            )

            with self.con.cursor() as cursor:
                cursor.execute("SELECT version();")
                record = cursor.fetchone()[0]
                print("Вы подключены к - ", record, "\n")
                cursor.execute("""SELECT table_name FROM information_schema.tables
                        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                        AND table_schema IN('public', 'myschema');
                        """)
                if not cursor.fetchall():
                    cursor.execute('''CREATE TABLE clients(id_client SERIAL PRIMARY KEY ,
                                           f_name VARCHAR(30) NOT NULL,
                                           s_name VARCHAR(30) NOT NULL,
                                           l_name VARCHAR(30),
                                           email VARCHAR(60));''')

                    cursor.execute('''CREATE TABLE phones(id_phone SERIAL PRIMARY KEY,
                                                   id_client INTEGER NOT NULL REFERENCES clients(id_client),
                                                   phone VARCHAR(15) NOT NULL);
                                                   ''')
                    self.con.commit()
                    print("Таблицы Clients и Phones успешно созданы в PostgreSQL")
                else:
                    print('Подключение к базе данных прошло успешно')
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)

    def insert_client(self):
        """Метод для добавления данных о клиенте"""
        fn, ln, sn, em = input("Введите фамилию, имя, отчество, e-mail клиента через запятую: ").split(',')
        with self.con.cursor() as cursor:
            cursor.execute("""
                    INSERT INTO clients(f_name, s_name, l_name, email) 
                    VALUES(%s, %s, %s, %s);
                    """, (fn, ln, sn, em))
            self.con.commit()
            cursor.execute("Select max(id_client) from clients;")
            idc = cursor.fetchone()[0]

        add_ph = input('Добовить номер телефона клиента? (y/n)')
        if add_ph == 'y':
            self.insert_phone(idc)

    def insert_phone(self, idc):
        """Метод для добавления номера телефона"""
        phone = input(f'Введите номер телефона для клиента {idc}: ')
        with self.con.cursor() as cursor:
            cursor.execute("""
                            INSERT INTO phones(id_client, phone) 
                            VALUES(%s, %s);
                            """, (idc, phone))
            self.con.commit()
        add_ph = input('Добовить ещё один номер телефона клиента? (y/n)')
        if add_ph == 'y':
            self.insert_phone(idc)

    def modify_client(self):
        """Метод для изменения данных о клиентах"""
        idcl = input('Для изменения данных клиента введите его ID: ')
        with self.con.cursor() as cursor:
            cursor.execute("SELECT * FROM clients WHERE id_client=%s;", (idcl,))
            row = cursor.fetchone()
            cursor.execute("SELECT * FROM clients WHERE id_client=%s;", (idcl,))
            if not cursor.fetchall():
                print('Клиента с таким id нет!')
            else:
                print('Данные по клиенту: \n', row)
                column = input("Введите поле, которое хотите изменить(фамилия, имя, отчетсво, email): ").lower()
                fields = {'фамилия': 'f_name',
                          'имя': 's_name',
                          'отчество': 'l_name',
                          'email': 'email',
                          }
                col = fields[column]
                data = input('Введите новое значение: ')
                cursor.execute(f"UPDATE clients SET {col}=%s WHERE id_client=%s;", (data, idcl))
                self.con.commit()
                cursor.execute("SELECT * FROM clients WHERE id_client=%s;", (idcl,))
                print(cursor.fetchone())


    def delPhone(self):
        """Метод позволяющий удалить телефон для существующего клиента"""
        idcl = input('Для удаления телефона клиента введите его ID: ')
        with self.con.cursor() as cursor:
            cursor.execute("SELECT * FROM phones WHERE id_client=%s;", (idcl,))
            print("%10s | %10s | %20s" % ('id_phone', 'id_client', 'phone'))
            for row in cursor.fetchall():
                print("%10s | %10s | %20s" % (row[0], row[1], row[2]))
            idph = input("Введите id телефона, который хотите удалить?")
            cursor.execute("""
                DELETE FROM phones WHERE id_phone = %s;
                """, (idph,))
            print('Данный телефон клиента будет удален!')
            ans = input("Вы уверены, что хотите удалить этот номер? y/n")
            if ans == 'y':
                self.con.commit()
            else:
                self.con.rollback()

    def delClient(self):
        """Метод позволяющий удалить существующего клиента"""
        idcl = input('Для удаления клиента введите его ID: ')
        with self.con.cursor() as cursor:
            cursor.execute("""
                            DELETE FROM phones WHERE id_client = %s;
                            """, (idcl,))
            cursor.execute("""
                            DELETE FROM clients WHERE id_client = %s;
                                        """, (idcl,))
            print('Данный клиент будет удален!')
            ans = input("Вы уверены, что хотите удалить этот номер? y/n")
            if ans == 'y':
                self.con.commit()
            else:
                self.con.rollback()

    def findClient(self):
        """Метод позволяющий найти клиента по его данным (имени, фамилии, email-у или телефону)"""
        collumn = input("Введите поле по которому будет осуществлен поиск \n "
                        "(имя, фамилия, email или телефон): ").lower()
        with self.con.cursor() as cursor:
            fields = {'фамилия':'f_name',
                      'имя': 's_name',
                      'отчество': 'l_name',
                      'email': 'email',
                      'телефон':'phone'}
            col = fields[collumn]
            data = input('Введите значение: ')
            if col != 'phone':
                cursor.execute(f"SELECT * FROM clients WHERE {col}=%s;", (data,))
            else:
                cursor.execute("""SELECT * FROM clients WHERE id_client=
                                                (SELECT id_client FROM phones WHERE phone=%s);
                                               """, (data,))
            row = cursor.fetchone()
            if row:
                print("%10s | %20s | %20s | %20s | %30s" % ('id_client', 'f_name', 's_name', 'l_name', 'email'))
                print("%10s | %20s | %20s | %20s | %30s" %
                      (row[0], row[1], row[2], row[3], row[4]))
            else:
                print("По вашему запросу ничего не найдено!")
    def viewClients(self):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT * FROM clients")
            print("%10s | %20s | %20s | %20s | %30s" % ('id_client', 'f_name', 's_name', 'l_name', 'email'))
            for row_cl in cursor.fetchall():
                print("%10s | %20s | %20s | %20s | %30s" %
                      (row_cl[0], row_cl[1], row_cl[2], row_cl[3], row_cl[4]))
                cursor.execute("SELECT phone FROM phones WHERE id_client=%s", (row_cl[0],))
                phone = ''
                for row_ph in cursor.fetchall():
                    phone += row_ph[0]+', '
                print("Телефоны:", phone[:-2])

    def closeDB(self):
        """Метод для закрытия сеанса с БД"""
        self.con.close()
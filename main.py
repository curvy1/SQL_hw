import DB
import configparser

HELP = """
insertClient - добавить нового клиента
modifyClient - изменить данные клиента
addPhone - добавть номер телефона клиента
deletePhone - удалить номер телефона клиента
deleteClient - удалить клиента
findClient - найти клиента
Clients - выводит информацию по всем клиентам
exit - выход
"""


def read_params(access_obj):
    config = configparser.ConfigParser()
    config.read('setting.ini')
    userdb = config[access_obj]['user']
    pasword = config[access_obj]['password']
    return userdb, pasword


if __name__ == '__main__':
    user, password = read_params('ClientsDB')
    ClientDB = DB.SQLdb('ClientsDB', user, password)
    print("Для получения справки по командам введите help")
    while True:
        print('-'*100)
        com = input('Введите команду для работы с БД Клиенты: ')
        if com == 'insertClient':
            ClientDB.insert_client()
        elif com == 'modifyClient':
            ClientDB.modify_client()
        elif com == 'addPhone':
            idcl = input('Для добавления телефона клиента введите его ID: ')
            ClientDB.insert_phone(idcl)
        elif com == 'deletePhone':
            ClientDB.delPhone()
        elif com == 'deleteClient':
            ClientDB.delClient()
        elif com == 'findClient':
            ClientDB.findClient()
        elif com == 'Clients':
            ClientDB.viewClients()
        elif com == 'help':
            print(HELP)
        elif com == 'exit':
            ClientDB.closeDB()
            break
        else:
            print('Неизвестная команда!')
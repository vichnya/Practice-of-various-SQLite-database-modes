import sqlite3
import functools

log_level = None

def log(decorator):
    """Декоратор настройек декоратора для логирования"""
    @functools.wraps(decorator)
    def inner(*args, **kwargs):
      print("""
            Доступные уровни логирования:
            CRITICAL
            ERROR
            WARNING
            INFO
            DEBUG
            Значение по умолчанию: DEBUG
            """)
      global log_level
      log_level = input("Введите уровнь логирования запросов: ")
      log_level = log_level.upper()
      result = decorator(*args, **kwargs)
      return result

    return inner

@log
def deco(func):
    """Функция - декоратор для запросов, в которой осуществляется их логирование"""

    @functools.wraps(func)
    def inner(*args, **kwargs):
        import logging
        import pendulum


        result = func(*args, **kwargs)
        string_query = args[1]
    
        class CustomFilter(logging.Filter):
            TIME = {
                "DEBUG": None,
                "INFO": None,
                "WARNING": None,
                "ERROR": None,
                "CRITICAL": None
            }

            now = pendulum.now('Europe/Moscow') 
            now = now.format('YYYY/MM/DD HH:mm:ss,SSSSSS')
            TIME["DEBUG"] = now
            TIME["INFO"] = now
            TIME["WARNING"] = now
            TIME["ERROR"] = now
            TIME["CRITICAL"] = now
                        
            def filter(self, record):
                record.time = CustomFilter.TIME[record.levelname]
                return True            
              
        logger = logging.getLogger('CRUD')
        logger.addFilter(CustomFilter())
        
        formatter = '%(time)s  |%(levelname)s| %(name)s - %(message)s'
        global log_level
        print(log_level)
        if log_level == "DEBUG":
          deco_level = logging.DEBUG
        elif log_level == "INFO":
          deco_level = logging.INFO
        elif log_level == "WARNING":
          deco_level = logging.WARNING
        elif log_level == "ERROR":
          deco_level = logging.ERROR
        elif log_level == "CRITICAL":
          deco_level = logging.CRITICAL
        else:
          print('Используется значение по умолчанию')
          deco_level = logging.DEBUG
          
        
        logging.basicConfig(filename='logging.txt',
                            format=formatter,
                            level=deco_level)
        logger.debug('Error: 0')
        logger.info('Warning: 0')
        logger.warning('Function works')
        logger.error('Query: 1')
        logger.critical(string_query + '\n')

        return result

    return inner


def once(func):
    """Функция - декоратор для первого подключения к БД"""

    @functools.wraps(func)
    def inner(*args, **kwargs):

        if not inner.called:

            result = func(*args, **kwargs)
            inner.called = True
            inner.handler = result

            return result
        else:
            return inner.handler

    deque = []
    deque.append(func.__name__)
    print(f"Декоратор вокруг {func.__name__}")
    inner.called = False  
    inner.handler = None
    print(deque)

    return inner


@once
def connect_to_db(path_to_db: str) -> sqlite3.Connection:
    """Функция подключения к БД"""
    print('Подключение к БД')
    try:
        conn = sqlite3.connect(path_to_db)
    except sqlite3.DatabaseError:
        print(f'Не удалось подключиться к БД: {path_to_db}')
    return conn


db_handler = connect_to_db('zhukov.db')


@deco
def read_sql(conn: sqlite3.Connection, query: str):
    """Функция обработки запросов к БД"""
    print('READ FROM DB')
    try:
        crud_read_str = query
        crud_res = conn.execute(crud_read_str)

        for records in crud_res:
            print(records)
    except sqlite3.OperationalError as e:
        print('Такой таблицы нет:', e)
        try:
            create_sql = '''CREATE TABLE user
               (id int, height real, name text, deleted bool, created DATETIME)'''
            conn.execute(create_sql)
        except:
            print('Таблица не создана, ошибка')
        conn.close()


# Работа с CRUD (таблица user)
read_sql(db_handler, "SELECT * FROM user")
read_sql(db_handler, """INSERT INTO user VALUES ('6', 1.85, 'user3', 1, '2019-03-02 11:39:20' ) """)
read_sql(db_handler, "SELECT * FROM user")
read_sql(db_handler, "UPDATE user SET name = 'Виктор' WHERE id == 6")
read_sql(db_handler, "SELECT * FROM user")
read_sql(db_handler, "DELETE FROM user WHERE name == 'Виктор'")
read_sql(db_handler, "SELECT * FROM user")
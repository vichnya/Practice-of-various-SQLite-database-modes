import sqlite3
import functools


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
                "DEBUG": None
            }

            now = pendulum.now('Europe/Moscow') #без параметра не работает в repl.it
            now = now.format('YYYY/MM/DD HH:mm:ss,SSSSSS')
            TIME["DEBUG"] = now
            
            def filter(self, record):
                record.time = CustomFilter.TIME[record.levelname]
                return True            
              
        logger = logging.getLogger('CRUD')
        logger.addFilter(CustomFilter())
        
        formatter = '%(time)s  %(name)s - %(message)s'
        logging.basicConfig(filename='logging.txt',
                            format=formatter,
                            level=logging.DEBUG)
        logger.debug(string_query)

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


read_sql(db_handler, "SELECT * FROM user")
read_sql(db_handler, """INSERT INTO user VALUES ('6', 1.85, 'user3', 1, '2019-03-02 11:39:20' ) """)
read_sql(db_handler, "SELECT * FROM user")
read_sql(db_handler, "UPDATE user SET name = 'Виктор' WHERE id == 6")
read_sql(db_handler, "SELECT * FROM user")
read_sql(db_handler, "DELETE FROM user WHERE name == 'Виктор'")
read_sql(db_handler, "SELECT * FROM user")
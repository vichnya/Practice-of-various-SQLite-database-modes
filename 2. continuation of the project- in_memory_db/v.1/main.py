import sqlite3
import functools
from USER import User

log_level = None

def log(level):
  """Декоратор настройек декоратора для логирования"""
  def log_inner(decorator):
    @functools.wraps(decorator)
    def inner(*args, **kwargs):

      global log_level
      log_level = level
      result = decorator(*args, **kwargs)
      return result
    
    return inner

  return log_inner

@log(level="INFO")
def deco(func):
    """Функция - декоратор для запросов, в которой осуществляется их логирование"""

    @functools.wraps(func)
    def inner(*args, **kwargs):
        import logging
        import pendulum

        result = func(*args, **kwargs)
        string_query = kwargs['queries_read'][0]
    
        class CustomFilter(logging.Filter):
            TIME = {
                "DEBUG": None,
                "INFO": None,
                "WARNING": None,
                "ERROR": None,
                "CRITICAL": None
            }

            now = pendulum.now('Europe/Moscow') #без параметра не работает в repl.it
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
        print(conn)
    except sqlite3.DatabaseError:
        print(f'Не удалось подключиться к БД: {path_to_db}')
    return conn

def db_table_create(conn: sqlite3.Connection, queries):
    """Функция создания таблицы в памяти"""
    try:
        crud_read_str = "SELECT * FROM user"
        conn.execute(crud_read_str)

    except sqlite3.OperationalError as e:
        print('Такой таблицы нет:', e)
        try:
            values = []
            sql_insert = "INSERT INTO user VALUES (?, ?, ?, ?, ?)"
            
            for _q in queries:
                if ("CREATE TABLE" in _q):
                    conn.execute(_q)
                else:
                    values.append(_q)
      
            conn.executemany(sql_insert, values)
        except:
            print('Таблица не создана, ошибка')

db_handler = connect_to_db(':memory:')
db_table_create(db_handler,
                queries=[
                    '''CREATE TABLE user
                 (id int, height real, name text, deleted bool, created DATETIME)''',
                    (1, 1.81, 'user1', 0, '2022-03-02 14:03:21'),
                    (2, 1.82, 'user2', 0, '2022-03-02 14:03:22'),
                    (3, 1.83, 'user3', 0, '2022-03-02 14:03:24'),
                    (4, 1.84, 'user4', 0, '2022-03-02 14:03:25'),
                    (5, 1.85, 'user5', 1, '2022-03-02 14:03:28'),
                    
                ])

@deco
def read_sql(conn: sqlite3.Connection, queries_read: list):
    """Функция обработки запросов к БД"""
    print('READ FROM DB')
    
    values = []
    if ("SELECT" in queries_read):
      sql_read = "SELECT * FROM user"
    elif ("INSERT INTO" in queries_read):
      sql_read = "INSERT INTO user VALUES (?, ?, ?, ?, ?)"
    elif ("UPDATE" in queries_read):
      sql_read = "UPDATE user SET name = ? where id = ?"
    elif ("DELETE" in queries_read):
      sql_read = "DELETE FROM user WHERE name == ?"

    for _qq in queries_read:
        if ("CREATE TABLE" in _qq):
            conn.execute(_qq)
        elif ("SELECT" in _qq):
          crud_res = conn.execute(sql_read)
        elif ("INSERT INTO" not in _qq and
              "UPDATE" not in _qq and
              "DELETE" not in _qq):
            values.append(_qq)
    
    if ("SELECT" not in queries_read):
        crud_res = conn.executemany(sql_read, values)

    for records in crud_res:
        print(records)


# Запросы с параметрами
read_sql(db_handler, queries_read = ["SELECT"])
read_sql(db_handler, queries_read = [
  "INSERT INTO",
  ('6', 1.85, 'user6', 1, '2019-03-02 11:39:20'),
  ('7', 1.86, 'user7', 1, '2019-03-02 11:39:29')
])
read_sql(db_handler, queries_read = ["SELECT"])
read_sql(db_handler, queries_read = [
  "UPDATE", 
  ('Виктор', 6),
  ('Маша', 7)
])
read_sql(db_handler, queries_read = ["SELECT"])
read_sql(db_handler, queries_read = [
  "DELETE", 
  ('Виктор',),
  ('Маша',)
])
read_sql(db_handler, queries_read = ["SELECT"])

# Работа с классом User
u = User(100, 1.65, 'Test', 0, '2022-03-02 14:51:21')

u.name = 'Vika'
#print(u.name)
#u.name = '9kk' #Некорректно введенное имя
#u.name = '  ' #Некорректно введенное имя

del u.name #Удаление имени
#print(u.name)
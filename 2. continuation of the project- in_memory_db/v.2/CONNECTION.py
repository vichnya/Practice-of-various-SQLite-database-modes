import sqlite3
import functools

def Singleton(cls):
    """Декоратор, который делает класс одноэлементным классом"""
    instance = None
    
    @functools.wraps(cls)
    def inner(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance
    
    return inner

@Singleton
class Connection():
  def __init__(self) -> sqlite3.Connection:
    self.__path = ':memory:'

  def connectDB(self):
    print('Подключение к БД')
    try:
        self.__conn = sqlite3.connect(self.__path)
    except sqlite3.DatabaseError:
        print(f'Не удалось подключиться к БД: {self.__path}')
    return self.__conn
    
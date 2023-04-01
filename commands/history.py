from datetime import datetime
import functools
from typing import Callable
import sqlite3

history_list = []

class CommandLog:
    def __init__(self, command, input_time, hotels):
        self.command = command
        self.input_time = input_time
        self.hotels = hotels


def logging_decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped_func(params, history=None):
        if history is None:
            history = history_list

        print('история:', history)
        input_time = datetime.now()
        print(params)
        result = func(params)

        if isinstance(result, type):
            hotels = None
        else:
            hotels = result

        if len(history) == 5:
            history.pop(0)

        history.append(CommandLog(
            command=func.__name__,
            input_time=input_time,
            hotels=hotels))

        return result

    return wrapped_func

def database_decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped_func(params):
        input_time = datetime.now()
        result = func(params)

        if isinstance(result, type):
            hotels = None
            return hotels
        else:
            hotels = result

        try:
            sqlite_connection = sqlite3.connect('hotels-history.db')
            add_command_query = '''INSERT INTO commands (command_name, input_time)
            VALUES ({func_name}, {input_time});'''.format(
                func_name=func.__name__, input_time=input_time)
            get_command_id_query = '''SELECT command_id FROM commands ORDER BY input_time DESC LIMIT 1;'''

            cursor = sqlite_connection.cursor()
            print("База данных подключена к SQLite")

            cursor.execute(add_command_query)
            print('Запрос на добавление команды выполнен успешно')
            sqlite_connection.commit()

            cursor.execute(get_command_id_query)
            print('Запрос на получение id команды выполнен успешно')
            command_id = cursor.fetchone()

            hotels_rows = [(
                command_id, hotel.id, hotel.name, hotel.price, hotel.image, hotel.distance, hotel.description, hotel.address, hotel.total_cost
            ) for hotel in hotels]

            cursor.executemany('''INSERT INTO hotels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', hotels_rows)
            print('Запрос на добавление отелей выполнен успешно')
            sqlite_connection.commit()

            cursor.close()

        except sqlite3.Error as error:
            print("Ошибка при подключении к sqlite", error)
        finally:
            if sqlite_connection:
                sqlite_connection.close()
                print("Соединение с SQLite закрыто")
                return hotels

    return wrapped_func



if __name__ == '__main__':
    try:
        sqlite_connection = sqlite3.connect('hotels-history.db')
        create_table_commands_query = '''CREATE TABLE commands(
                                    id INTEGER PRIMARY KEY,
                                    command_name TEXT NOT NULL,
                                    input_time timestamp);'''

        create_table_hotels_query = '''CREATE TABLE hotels(
                                    id INTEGER PRIMARY KEY,
                                    command_id INTEGER NOT NULL,
                                    hotel_id INTEGER NOT NULL,
                                    hotel_name TEXT NOT NULL,
                                    hotel_price INTEGER,
                                    image TEXT,
                                    distance REAL,
                                    description TEXT,
                                    address TEXT,
                                    total_cost INTEGER);'''

        cursor = sqlite_connection.cursor()
        print("База данных подключена к SQLite")
        cursor.execute(create_table_commands_query)
        cursor.execute(create_table_hotels_query)
        sqlite_connection.commit()
        print("Таблицы SQLite создана")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
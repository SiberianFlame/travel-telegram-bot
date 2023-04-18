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
        input_time = datetime.now().strftime('%m/%d/%Y')
        result = func(params)
        user_id = params['user_id']

        if isinstance(result, type):
            hotels = None
            return hotels
        else:
            hotels = result

        try:
            sqlite_connection = sqlite3.connect('commands/hotels-history.db')

            cursor = sqlite_connection.cursor()
            print("База данных подключена к SQLite")

            cursor.execute('''INSERT INTO commands (user_id, command_name, input_time) VALUES (?, ?, ?);''', (user_id, func.__name__, input_time))
            print('Запрос на добавление команды выполнен успешно')
            sqlite_connection.commit()

            cursor.execute('''SELECT id FROM commands WHERE user_id = (?) ORDER BY input_time DESC LIMIT 1;''', user_id)
            print('Запрос на получение id команды выполнен успешно')
            command_id = cursor.fetchone()
            hotels_rows = []
            images_rows = []

            for hotel in hotels:
                hotels_rows.append((
                command_id, hotel.id, hotel.name, hotel.price, hotel.distance, hotel.description, hotel.address, hotel.total_cost))

                for image in hotel.image:
                    images_rows.append((hotel.id, image))

            # hotels_rows = [(
            #     command_id, hotel.id, hotel.name, hotel.price, hotel.distance, hotel.description, hotel.address, hotel.total_cost
            # ) for hotel in hotels]

            cursor.executemany('''INSERT INTO hotels VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', hotels_rows)
            cursor.executemany('''INSERT INTO imagess VALUES (?, ?)''', images_rows)

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
                                    user_id INTEGER,
                                    command_name TEXT NOT NULL,
                                    input_time TEXT);'''

        create_table_hotels_query = '''CREATE TABLE hotels(
                                    id INTEGER PRIMARY KEY,
                                    command_id INTEGER NOT NULL,
                                    hotel_id INTEGER NOT NULL,
                                    hotel_name TEXT NOT NULL,
                                    hotel_price INTEGER,
                                    distance REAL,
                                    description TEXT,
                                    address TEXT,
                                    total_cost INTEGER);'''

        create_table_images_query = '''CREATE TABLE images(
        id INTEGER PRIMARY KEY,
        hotel_id INTEGER,
        image TEXT);'''

        cursor = sqlite_connection.cursor()
        print("База данных подключена к SQLite")
        cursor.execute(create_table_commands_query)
        cursor.execute(create_table_hotels_query)
        cursor.execute(create_table_images_query)
        sqlite_connection.commit()
        print("Таблицы SQLite создана")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
from datetime import datetime
import functools
from typing import Callable
import sqlite3

# history_list = []
#
# class CommandLog:
#     def __init__(self, command, input_time, hotels):
#         self.command = command
#         self.input_time = input_time
#         self.hotels = hotels


# def logging_decorator(func: Callable) -> Callable:
#     @functools.wraps(func)
#     def wrapped_func(params, history=None):
#         if history is None:
#             history = history_list
#
#         print('история:', history)
#         input_time = datetime.now()
#         print(params)
#         result = func(params)
#
#         if isinstance(result, type):
#             hotels = None
#         else:
#             hotels = result
#
#         if len(history) == 5:
#             history.pop(0)
#
#         history.append(CommandLog(
#             command=func.__name__,
#             input_time=input_time,
#             hotels=hotels))
#
#         return result
#
#     return wrapped_func

def history(user_id):
    try:
        result_dict = dict()
        sqlite_connection = sqlite3.connect('hotels-history.db')
        select_commands_query = '''SELECT * FROM commands WHERE user_id = ?;'''
        select_hotels_query = '''SELECT * FROM hotels WHERE command_id = ?;'''
        select_images_query = '''SELECT * FROM images WHERE hotel_id = ?;'''

        cursor = sqlite_connection.cursor()
        print("База данных подключена к SQLite")

        cursor.execute(select_commands_query, user_id)
        commands_rows = cursor.fetchall()
        for command_row in commands_rows:
            cursor.execute(select_hotels_query, command_row[0])
            result_dict[command_row[0]] = {'name': command_row[2], 'input_time': command_row[3], 'hotels': {}}
            hotels_rows = cursor.fetchall()
            for hotel_row in hotels_rows:
                cursor.execute(select_images_query, hotel_row[2])
                images_rows = cursor.fetchall()
                result_dict[command_row[0]]['hotels'][hotel_row[2]] = {
                    'name': hotel_row[3],
                    'price': hotel_row[4],
                    'distance': hotel_row[5],
                    'description':  hotel_row[6],
                    'address': hotel_row[7],
                    'total_cost': hotel_row[8],
                    'images': []
                }
                for image_row in images_rows:
                    result_dict[command_row[0]]['hotels'][hotel_row[2]]['images'].append(image_row[2])

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
        result_dict = None
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
            return result_dict

def database_decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped_func(params):
        print('Получена функция', func.__name__)
        input_time = datetime.now().strftime('%m/%d/%Y')
        result = func(params)
        user_id = params['user_id']

        if isinstance(result, type):
            hotels = None
            return hotels
        else:
            hotels = result

        print('Отели:', hotels)

        try:
            sqlite_connection = sqlite3.connect('commands/hotels-history.db')

            cursor = sqlite_connection.cursor()
            print("База данных подключена к SQLite")

            cursor.execute('''INSERT INTO commands(user_id, command_name, input_time) VALUES (?, ?, ?);''', (user_id, func.__name__, input_time))
            for row in cursor.execute('''SELECT * FROM commands'''):
                print(row)
            print('Запрос на добавление команды выполнен успешно')
            sqlite_connection.commit()

            # print('Пробую направить select-запрос на получение id команды...')
            # cursor.execute('''SELECT id FROM commands WHERE user_id = ? ORDER BY id DESC LIMIT 1;''', user_id)
            # print('Запрос на получение id команды выполнен успешно')
            command_id = cursor.lastrowid
            print(command_id)
            hotels_rows = []
            images_rows = []

            print('Составляю rows для отелей и изображений...')
            for hotel in hotels:
                print('Добавляю отель...')
                hotels_rows.append((
                command_id, hotel.id, hotel.name, hotel.price, hotel.distance, hotel.description, hotel.address, hotel.total_cost))
                print('Отель добавлен! Добавляю изображения отеля...')

                for image in hotel.image:
                    images_rows.append((hotel.id, image))
                print('Изображения отеля добавлены!')

            # hotels_rows = [(
            #     command_id, hotel.id, hotel.name, hotel.price, hotel.distance, hotel.description, hotel.address, hotel.total_cost
            # ) for hotel in hotels]

            print('Приступаю к добавлению отелей в базу данных...')
            cursor.executemany('''INSERT INTO hotels(
            command_id, hotel_id, hotel_name, hotel_price, distance, description, address, total_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', hotels_rows)
            print('Приступаю к добавлению изображений в базу данных...')
            cursor.executemany('''INSERT INTO images(hotel_id, image) VALUES (?, ?)''', images_rows)

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
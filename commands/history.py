from datetime import datetime
import functools
from typing import Callable
import sqlite3

def history(user_id):
    """
    Command /history, which makes select queries to the DB and returns a dictionary of data
    :param user_id: id of the user.
    """

    try:
        user_id = (user_id)
        result_dict = dict()
        sqlite_connection = sqlite3.connect('commands/hotels-history.db')
        select_commands_query = '''SELECT * FROM commands WHERE user_id = {userid};'''
        select_hotels_query = '''SELECT * FROM hotels WHERE command_id = {commandid};'''
        select_images_query = '''SELECT * FROM images WHERE hotel_id = {hotelid};'''

        cursor = sqlite_connection.cursor()

        cursor.execute(select_commands_query.format(userid=user_id))
        commands_rows = cursor.fetchall()
        for command_row in commands_rows:
            cursor.execute(select_hotels_query.format(commandid=command_row[0]))
            result_dict[command_row[0]] = {'name': command_row[2], 'input_time': command_row[3], 'hotels': {}}
            hotels_rows = cursor.fetchall()
            for hotel_row in hotels_rows:
                try:
                    cursor.execute(select_images_query.format(hotelid=hotel_row[2]))
                    images_rows = cursor.fetchall()
                    images_flag = True
                except sqlite3.Error as error:
                    images_flag = False
                result_dict[command_row[0]]['hotels'][hotel_row[2]] = {
                    'name': hotel_row[3],
                    'price': hotel_row[4],
                    'distance': hotel_row[5],
                    'description':  hotel_row[6],
                    'address': hotel_row[7],
                    'total_cost': hotel_row[8],
                    'images': []
                }
                if images_flag:
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
    """
    Decorator for commands that adds entries to the DB.
    :param func: command
    :return: func
    """

    @functools.wraps(func)
    def wrapped_func(params):
        """
        Wrapped func and addition entries to the DB
        :param params: params dict
        :return: None (if something went wrong), hotels (if everything is OK)
        """

        input_time = datetime.now().strftime('%m/%d/%Y')
        result = func(params)
        user_id = params['user_id']

        if isinstance(result, type) or result is None:
            hotels = None
            return hotels
        else:
            hotels = result

        try:
            sqlite_connection = sqlite3.connect('commands/hotels-history.db')

            cursor = sqlite_connection.cursor()
            print("База данных подключена к SQLite")

            cursor.execute('''INSERT INTO commands(user_id, command_name, input_time) VALUES (?, ?, ?);''', (user_id, func.__name__, input_time))
            sqlite_connection.commit()

            command_id = cursor.lastrowid
            hotels_rows = []
            images_rows = []

            sqlite_connection.close()

            for hotel in hotels:
                hotels_rows.append((
                command_id, hotel.id, hotel.name, hotel.cost, hotel.distance, hotel.description, hotel.address, hotel.total_cost))

                if hotel.image:
                    for image in hotel.image:
                        images_rows.append((hotel.id, image))

            sqlite_connection = sqlite3.connect('commands/hotels-history.db')
            cursor = sqlite_connection.cursor()

            cursor.executemany('''INSERT INTO hotels(
            command_id, hotel_id, hotel_name, hotel_price, distance, description, address, total_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', hotels_rows)

            if images_rows:
                cursor.executemany('''INSERT INTO images(hotel_id, image) VALUES (?, ?)''', images_rows)

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
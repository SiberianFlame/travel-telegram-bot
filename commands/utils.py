import datetime
from datetime import datetime, date
from typing import Union


class Hotel:
    def __init__(self, name, hotel_id, cost, distance, image='', description='', address='', total_cost = 0):
        self.name = name
        self.id = hotel_id
        self.cost = cost
        self.image = image
        self.distance = distance
        self.description = description
        self.address = address
        self.total_cost = total_cost


def is_photos_amount_valid(photos_amount) -> bool:
    """
    Func that checks if photos amount is valid.
    :param photos_amount: Photos amount to be sent.
    :return: True (if everything is OK), False (if something went wrong).
    :rtype: bool
    """

    try:
        photos_amount = int(photos_amount)
        if photos_amount > 3 or photos_amount <= 0:
            raise ValueError
    except ValueError:
        return False
    else:
        return True


def is_photos_flag_valid(photos_flag) -> bool:
    """
    Func that checks if photos flag is valid.
    :param photos_flag: Flag indicating whether photos should be sent.
    :return: True (if everything is OK), False (if something went wrong).
    :rtype: bool
    """

    if not photos_flag.lower() == 'да' and not photos_flag.lower() == 'нет':
        return False
    else:
        return True


def is_city_valid(city) -> bool:
    """
    Func that checks if city is valid.
    :param city: City to search for hotels.
    :return: True (if everything is OK), False (if something went wrong).
    :rtype: bool
    """
    if not isinstance(city, str):
        return False
    else:
        return True


def is_dates_valid(start_date, end_date) -> bool:
    """
    Func that checks if dates are valid.
    :param start_date: Check-in date.
    :param end_date: Check-out date.
    :return: True (if everything is OK), False (if something went wrong).
    :rtype: bool
    """

    try:

        start_date = date_split(start_date)
        end_date = date_split(end_date)

        print('Начальная дата:', start_date)
        print('Конечная дата:', end_date)

        if isinstance(start_date, type) or isinstance(end_date, type):
            raise ValueError
        print('Проверку типов даты прошли')

        if datetime(start_date[2], start_date[1], start_date[0]) > datetime(end_date[2], end_date[1], end_date[0]):
            raise ValueError
        print('Сравнение даты прошли')

        days_amount = (date(end_date[2], end_date[1], end_date[0])
                       - date(start_date[2], start_date[1], start_date[0])).days

        if days_amount <= 0:
            raise ValueError
        print('Проверка количества дней пройдена')

        if not is_data_valid(start_date[0], start_date[1], start_date[2]) or not is_data_valid(
                end_date[0], end_date[1], end_date[2]):
            raise ValueError

        print('Проверка каждой даты пройдена')

    except ValueError:
        return False
    else:
        return True


def is_hotels_amount_valid(hotels_amount) -> bool:
    """
    Func that checks if hotels amount is valid.
    :param hotels_amount: Number of hotels to be found.
    :return: True (if everything is OK), False (if something went wrong).
    :rtype: bool
    """

    try:
        if hotels_amount <= 0 or hotels_amount > 5:
            raise ValueError
    except ValueError:
        return False
    else:
        return True


def data_input() -> dict:
    """
    Func for data entry.
    :return: Dict with entered data.
    :rtype: dict
    """

    search_town = input('Введите город для поиска: ')
    search_hotels_amount = input('Введите количество отелей (не больше 5): ')
    is_photos = input('Нужно ли выводить фотографии? (да/нет): ').lower()
    if is_photos == 'да':
        photos_amount = input('Введите количество фотографий (не больше 3): ')
    else:
        photos_amount = 3
    start_date = input('Введите планируемую дату заселения в отель (в формате дд.мм.гг): ')
    end_date = input('Введите планируемую дату выезда из отеля (в формате дд.мм.гг): ')

    params_dict = {'town': search_town, 'hotelsAmount': search_hotels_amount, 'isPhotos': is_photos,
                   'photosAmount': photos_amount, 'startDate': start_date, 'endDate': end_date}

    return params_dict


def is_data_valid(day: int, month: int, year: int) -> bool:
    """
    Func that checks if the date is valid.
    :param day: Day of the specified date.
    :param month: Month of the specified date.
    :param year: Year of the specified date.
    :return: True (if the date is valid), False (if not).
    :rtype: bool
    """

    days31_month = [1, 3, 5, 7, 8, 10, 12]
    days30_month = [4, 6, 9, 11]

    if year % 400 == 0 or year % 4 == 0:
        is_leap_year = True
    else:
        is_leap_year = False

    if (day > 29 and is_leap_year and month == 2) or \
            (day > 28 and not is_leap_year and month == 2) or \
            (day > 31 and month in days31_month) or \
            (day > 30 and month in days30_month) or \
            (0 <= month > 12) or year < 2023 or day <= 0 or month <= 0:
        return False
    else:
        return True


def date_split(date: str) -> Union[tuple, type[ValueError]]:
    """
    Func that divides two dates into days, months and years.
    :param date: Date to be split.
    :return: Tuple with divided date.
    :rtype: Tuple (if everything is OK), Exception (if something went wrong).
    """

    date = date.split('.')

    try:
        if date[0].startswith('0'):
            date[0].replace('0', '')
        elif date[1].startswith('0'):
            date[1].replace('0', '')

        day = int(date[0])
        month = int(date[1])
        year = int(date[2])

    except ValueError:
        print('Преобразование дней в date_split не удалось')
        return ValueError
    except IndexError:
        print('Преобразование дней в date_split не удалось')
        return ValueError
    else:
        return day, month, year


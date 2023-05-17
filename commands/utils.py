import datetime
from datetime import datetime, date
from typing import Union


class Hotel:
    """
    Class that represents a hotel. It contains all the information about the hotel.
    :param name: Name of the hotel.
    :param hotel_id: id of the hotel.
    :param cost: Cost of the hotel.
    :param distance: Distance of the hotel.
    :param image: Image of the hotel.
    :param description: Description of the hotel.
    :param address: Address of the hotel.
    :param total_cost: Total cost of the hotel.
    """

    def __init__(self, name, hotel_id, cost, distance, image='', description='', address='', total_cost = 0):
        self.name = name
        self.id = hotel_id
        self.cost = cost
        self.image = image
        self.distance = distance
        self.description = description
        self.address = address
        self.total_cost = total_cost

def is_price_range_valid(start_price, end_price):
    """
    Price range validation.
    """

    try:
        start_price, end_price = int(start_price), int(end_price)
        if end_price <= start_price or end_price <= 0 or start_price <= 0:
            raise ValueError
    except ValueError:
        return False
    except TypeError:
        return False
    else:
        return True

def is_distance_range_valid(start_distance, end_distance):
    """
    Distance range validation.
    """

    try:
        start_distance, end_distance = int(start_distance), int(end_distance)
        if end_distance <= start_distance or end_distance <= 0 or start_distance <= 0:
            raise ValueError
    except ValueError:
        return False
    except TypeError:
        return False
    else:
        return True

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

        if isinstance(start_date, type) or isinstance(end_date, type):
            raise ValueError

        if datetime(start_date[2], start_date[1], start_date[0]) > datetime(end_date[2], end_date[1], end_date[0]):
            raise ValueError

        days_amount = (date(end_date[2], end_date[1], end_date[0])
                       - date(start_date[2], start_date[1], start_date[0])).days

        if days_amount <= 0:
            raise ValueError

        if not is_data_valid(start_date[0], start_date[1], start_date[2]) or not is_data_valid(
                end_date[0], end_date[1], end_date[2]):
            raise ValueError


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
        return ValueError
    except IndexError:
        return ValueError
    else:
        return day, month, year


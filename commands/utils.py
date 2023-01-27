from typing import Union


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
            (0 <= month > 12) or year < 2022 or day <= 0 or month <= 0:
        return False
    else:
        return True


def date_split(start_date: str, end_date: str) -> Union[tuple, type[ValueError]]:
    """
    Func that divides two dates into days, months and years.
    :param start_date: Check-in date.
    :param end_date: Check-out date.
    :return: Tuple with two divided dates.
    :rtype: Tuple (if everything is OK), Exception (if something went wrong).
    """

    start_date = start_date.split('.')
    end_date = end_date.split('.')

    try:
        if start_date[0].startswith('0'):
            start_date[0].replace('0', '')
        elif start_date[1].startswith('0'):
            start_date[1].replace('0', '')
        elif end_date[0].startswith('0'):
            end_date[0].replace('0', '')
        elif end_date[1].startswith('0'):
            end_date[1].replace('0', '')

        start_day = int(start_date[0])
        start_month = int(start_date[1])
        start_year = int(start_date[2])

        end_day = int(end_date[0])
        end_month = int(end_date[1])
        end_year = int(end_date[2])

    except ValueError:
        print('Преобразование дней в date_split не удалось')
        return ValueError
    except IndexError:
        print('Преобразование дней в date_split не удалось')
        return ValueError
    else:
        return (start_day, start_month, start_year), (end_day, end_month, end_year)


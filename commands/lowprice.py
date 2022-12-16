import json
import datetime
from typing import Union, Type

import requests
import translators.server as tss


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


def lowprice(city: str, hotels_amount: int, start_date: str, end_date: str, photos_flag: str, photos_amount: int = 3)\
        -> Union[tuple, Type[TypeError], Type[ValueError], Type[NameError]]:
    """
    Func that finds a specified number of the cheapest hotels in a specified city.

    :param city: City to look for hotels.
    :param hotels_amount: Number of hotels to be found.
    :param start_date: Check-in date.
    :param end_date: Check-out date.
    :param photos_flag: Specifies whether to display photos.
    :param photos_amount: Number of photos to output.

    :return: Tuple consisting of information about hotels.
    :rtype: Tuple (in case everything is OK) or Exception (in case something went wrong).
    """
    # Блок проверок на правильность введённых данных

    if not all([isinstance(city, str), isinstance(hotels_amount, int), isinstance(start_date, str),
                isinstance(end_date, str), isinstance(photos_flag, str), isinstance(photos_amount, int)]):
        print('Ошибка: неправильный ввод данных')
        return TypeError

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
        print('Ошибка: неверная дата')
        return ValueError
    except IndexError:
        print('Ошибка: неверная дата')
        return ValueError

    if not is_data_valid(start_day, start_month, start_year) or not is_data_valid(end_day, end_month, end_year):
        print('Ошибка: неверная дата')
        return ValueError

    if start_day >= end_day and start_month >= end_month and start_year >= end_year:
        print('Ошибка: неверная дата')
        return ValueError

    if hotels_amount <= 0 or hotels_amount > 5 or photos_amount > 3 or photos_amount <= 0:
        print('Ошибка: неправильный ввод данных')
        return ValueError

    if photos_flag == 'да':
        photos_flag = True
    elif photos_flag == 'нет':
        photos_flag = False
    else:
        print('Ошибка: неправильный ввод данных')
        return ValueError

    # print('Ввод данных работает нормально. Завершаю тест.')
    # return None

    from_language, to_language = 'ru', 'en'                         # перевод введенного пользователем
    translated_city = tss.google(city, from_language, to_language)  # города на английский язык

    city_url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    properties_url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    querystring = {"q": translated_city}

    city_headers = {
        "X-RapidAPI-Key": "681522802emsh38e571f157da2b7p1f8724jsn4921d6d0d281",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    properties_headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "681522802emsh38e571f157da2b7p1f8724jsn4921d6d0d281",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    city_response = requests.request("GET", city_url, headers=city_headers, params=querystring)
    city_data = json.loads(city_response.text)

    for elem in city_data['sr']:
        if elem['type'] == 'CITY' and elem['regionNames']['shortName'].lower() == translated_city.lower():
            city_id = str(elem['gaiaId'])  # поиск gaiaId города для дальнейшего поиска отелей
            break

    try:
        properties_parameters = {'destination': {'regionId': city_id},
                                 'checkInDate': {'day': start_day,
                                                 'month': start_month,
                                                 'year': start_year},
                                 'checkOutDate': {'day': end_day,
                                                  'month': end_month,
                                                  'year': end_year},
                                 'rooms': [{'adults': 1}]}
    except NameError:
        print('Ошибка: данный город не найден')
        return NameError

    properties_response = requests.request("POST", properties_url,
                                           json=properties_parameters, headers=properties_headers)
    properties_data = json.loads(properties_response.text)

    hotels_list = []

    # составляем список из отелей с наименьшей стоимостью
    for elem in properties_data['data']['propertySearch']['properties']:

        if len(hotels_list) != hotels_amount and round(elem['price']['lead']['amount']) != 0:

            if photos_flag:
                hotels_list.append({
                    'name': elem['name'],
                    'id': elem['id'],
                    'cost': round(elem['price']['lead']['amount']),
                    'image': [elem['propertyImage']['image']['url']],
                    'distance': elem['destinationInfo']['distanceFromDestination']['value']})

            else:
                hotels_list.append({
                    'name': elem['name'],
                    'id': elem['id'],
                    'cost': round(elem['price']['lead']['amount']),
                    'distance': elem['destinationInfo']['distanceFromDestination']['value']})

        else:

            for hotel in hotels_list[:]:

                if hotel['cost'] > round(elem['price']['lead']['amount']) != 0:
                    if photos_flag:
                        hotels_list.remove(hotel)
                        hotels_list.append({
                            'name': elem['name'],
                            'id': elem['id'],
                            'cost': round(elem['price']['lead']['amount']),
                            'image': [elem['propertyImage']['image']['url']],
                            'distance': elem['destinationInfo']['distanceFromDestination']['value']})

                    else:
                        hotels_list.remove(hotel)
                        hotels_list.append({
                            'name': elem['name'],
                            'id': elem['id'],
                            'cost': round(elem['price']['lead']['amount']),
                            'distance': elem['destinationInfo']['distanceFromDestination']['value']})

                    break


    hotels_url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    days_amount = (datetime.date(end_year, end_month, end_day) - datetime.date(start_year, start_month, start_day)).days

    # добавляем найденным отелям общую цену, адрес, описание и фото, если нужно
    for index, hotel in enumerate(hotels_list[:]):
        hotel_parameters = {'propertyId': hotel['id']}
        hotel_response = requests.request('post', hotels_url, json=hotel_parameters, headers=properties_headers)
        hotel_data = json.loads(hotel_response.text)
        hotels_list[index]['description'] = hotel_data['data']['propertyInfo']['summary']['tagline']
        hotels_list[index]['address'] = hotel_data['data']['propertyInfo']['summary']['location']['address']['addressLine']
        hotels_list[index]['totalCost'] = hotels_list[index]['cost'] * days_amount
        if photos_flag:
            if photos_amount >= 2:
                hotels_list[index]['image'].append(hotel_data['data']['propertyInfo']['propertyGallery']['images'][1]['image']['url'])
                if photos_amount == 3:
                    hotels_list[index]['image'].append(
                        hotel_data['data']['propertyInfo']['propertyGallery']['images'][2]['image']['url'])

    return tuple(hotels_list)


if __name__ == '__main__':
    search_town = input('Введите город для поиска: ')
    search_hotels_amount = int(input('Введите количество отелей (не больше 5): '))
    is_photos = input('Нужно ли выводить фотографии? (да/нет): ').lower()
    if is_photos == 'да':
        photos_amount = int(input('Введите количество фотографий (не больше 3): '))
    else:
        photos_amount = 3
    start_date = input('Введите планируемую дату заселения в отель (в формате дд.мм.гг): ')
    end_date = input('Введите планируемую дату выезда из отеля (в формате дд.мм.гг): ')
    for hotel in lowprice(
            search_town, search_hotels_amount, start_date, end_date, is_photos, photos_amount=photos_amount):
        print('\nНазвание отеля:', hotel['name'])
        print('ID отеля:', hotel['id'])
        print('Описание отеля:', hotel['description'])
        print('Адрес отеля:', hotel['address'])
        print('Расстояние до центра (в милях):', hotel['distance'])
        print('Цена за одну ночь:', str(hotel['cost']) + '$', end='\t')
        print('Итоговая цена:', str(hotel['totalCost']) + '$')

        if 'images' in hotel.keys():
            for image in hotel['images']:
                print('Ссылка на изображение:', image)


import datetime
import json
from typing import Union, Type

import requests
import translators.server as tss

from commands import lowprice


def highprice_parser(api_data, hotels_amount: int, photos_flag: bool) -> list:
    """
    Parser func for the most expensive hotels.
    :param api_data: JSON with all properties in the specified city.
    :param hotels_amount: Amount of hotels to be found.
    :param photos_flag: Whether to add photo.
    :return: List of the most expensive hotels.
    :rtype: list
    """

    hotels_list = []

    for elem in api_data['data']['propertySearch']['properties']:

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

                if hotel['cost'] < round(elem['price']['lead']['amount']) != 0:
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

    return hotels_list


def highprice(params: dict) -> Union[tuple, Type[TypeError], Type[ValueError], Type[NameError]]:
    """
    Func that returns a specified number of the most expensive hotels in a specified city.

    :param params: Dict containing parameters for func.

    :return: Tuple consisting of information about hotels.
    :rtype: Tuple (in case everything is OK) or Exception (in case something went wrong).
    """

    city, hotels_amount, start_date, end_date, photos_flag, photos_amount = \
        params['town'], params['hotelsAmount'], params['startDate'], \
        params['endDate'], params['isPhotos'], params['photosAmount']

    # Блок проверок на правильность введённых данных

    try:
        hotels_amount = int(hotels_amount)
        photos_amount = int(photos_amount)
    except ValueError:
        print('Отель или фото в int не перевелись')
        return ValueError

    if not all([isinstance(city, str), isinstance(hotels_amount, int), isinstance(start_date, str),
                isinstance(end_date, str), isinstance(photos_flag, str), isinstance(photos_amount, int)]):
        print('Ошибка: неправильный ввод данных (тип не соответствует)')
        return TypeError

    try:
        dates_tuple = lowprice.date_split(start_date, end_date)
        start_date, end_date = dates_tuple[0], dates_tuple[1]
        start_day, start_month, start_year = start_date[0], start_date[1], start_date[2]
        end_day, end_month, end_year = end_date[0], end_date[1], end_date[2]
    except TypeError:
        print('С разделением даты из tuple проблема')
        return TypeError

    if not lowprice.is_data_valid(start_day, start_month, start_year) or not lowprice.is_data_valid(
            end_day, end_month, end_year):
        print('Ошибка: дата не прошла проверку на валидность')
        return ValueError

    if start_day >= end_day and start_month >= end_month and start_year >= end_year:
        print('Ошибка: ошибка с днями')
        return ValueError

    if hotels_amount <= 0 or hotels_amount > 5 or photos_amount > 3 or photos_amount <= 0:
        print('Ошибка: с количеством отелей или фото')
        return ValueError

    if photos_flag.lower() == 'да':
        photos_flag = True
    elif photos_flag.lower() == 'нет':
        photos_flag = False
    else:
        print('Ошибка: флаг фото')
        return ValueError

    days_amount = (datetime.date(end_year, end_month, end_day) - datetime.date(start_year, start_month, start_day)).days
    if days_amount <= 0:
        print('Ошибка: даты одна вперед другой либо одинаковые')
        return ValueError

    # print('Ввод данных работает нормально. Завершаю тест.')
    # return None

    from_language, to_language = 'ru', 'en'  # перевод введенного пользователем
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

    hotels_list = highprice_parser(properties_data, hotels_amount, photos_flag)

    hotels_url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    # добавляем найденным отелям общую цену, адрес, описание и фото, если нужно
    for index, hotel in enumerate(hotels_list[:]):
        hotel_parameters = {'propertyId': hotel['id']}
        hotel_response = requests.request('post', hotels_url, json=hotel_parameters, headers=properties_headers)
        hotel_data = json.loads(hotel_response.text)
        hotels_list[index]['description'] = hotel_data['data']['propertyInfo']['summary']['tagline']
        hotels_list[index]['address'] = hotel_data['data']['propertyInfo']['summary']['location']['address'][
            'addressLine']
        hotels_list[index]['totalCost'] = hotels_list[index]['cost'] * days_amount
        if photos_flag:
            if photos_amount >= 2:
                hotels_list[index]['image'].append(
                    hotel_data['data']['propertyInfo']['propertyGallery']['images'][1]['image']['url'])
                if photos_amount == 3:
                    hotels_list[index]['image'].append(
                        hotel_data['data']['propertyInfo']['propertyGallery']['images'][2]['image']['url'])

    return tuple(hotels_list)

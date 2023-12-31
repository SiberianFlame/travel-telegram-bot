import datetime
import json
import copy
from typing import Union, Type

import requests
import translators.server as tss

from commands import utils, history
from commands.utils import Hotel



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
            new_hotel = Hotel(name=elem['name'],
                          hotel_id=elem['id'],
                          cost=round(elem['price']['lead']['amount']),
                          distance=round(elem['destinationInfo']['distanceFromDestination']['value'] * 1.609, 2))

            if photos_flag:
                new_hotel.image = [elem['propertyImage']['image']['url']]
            hotels_list.append(copy.deepcopy(new_hotel))

        else:

            for hotel in hotels_list[:]:

                if hotel.cost < round(elem['price']['lead']['amount']) != 0:
                    hotels_list.remove(hotel)
                    new_hotel = Hotel(name=elem['name'],
                                  hotel_id=elem['id'],
                                  cost=round(elem['price']['lead']['amount']),
                                  distance=round(elem['destinationInfo']['distanceFromDestination']['value'] * 1.609, 2))

                    if photos_flag:
                        new_hotel.image = [elem['propertyImage']['image']['url']]
                    hotels_list.append(copy.deepcopy(new_hotel))

                    break

    return hotels_list


@history.database_decorator
def highprice(params: dict) -> Union[tuple, Type[TypeError], Type[ValueError], Type[NameError]]:
    """
    Highprice func for /highprice command. Returns the most expensive hotels.
    :param params: Dict with params for searching.
    :return: Tuple with hotels (if everything's OK), error (if something went wrong)
    """

    city, hotels_amount, start_date, end_date, photos_flag, photos_amount = \
        params['town'], params['hotelsAmount'], params['startDate'], \
        params['endDate'], params['isPhotos'], params['photosAmount']

    try:
        start_day, start_month, start_year = utils.date_split(start_date)
        end_day, end_month, end_year = utils.date_split(end_date)
    except TypeError:
        return TypeError

    days_amount = (datetime.date(end_year, end_month, end_day) -
                   datetime.date(start_year, start_month, start_day)).days

    try:
        from_language, to_language = 'ru', 'en'  # перевод введенного пользователем
        translated_city = tss.google(city, from_language, to_language)  # города на английский язык
    except TypeError:
        return TypeError

    city_url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    properties_url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    querystring = {"q": translated_city}

    city_headers = {
        "X-RapidAPI-Key": "d97fd53db6msh4d9089b1849e616p1d574fjsn59345fc9ed65",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    properties_headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "d97fd53db6msh4d9089b1849e616p1d574fjsn59345fc9ed65",
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
        return NameError

    properties_response = requests.request("POST", properties_url,
                                           json=properties_parameters, headers=properties_headers)
    properties_data = json.loads(properties_response.text)

    hotels_list = highprice_parser(properties_data, hotels_amount, photos_flag)

    hotels_url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    # добавляем найденным отелям общую цену, адрес, описание и фото, если нужно
    for index, hotel in enumerate(hotels_list[:]):
        hotel_parameters = {'propertyId': hotel.id}
        hotel_response = requests.request('post', hotels_url, json=hotel_parameters, headers=properties_headers)
        hotel_data = json.loads(hotel_response.text)
        hotels_list[index].description = hotel_data['data']['propertyInfo']['summary']['tagline']
        hotels_list[index].address = hotel_data['data']['propertyInfo']['summary']['location']['address'][
            'addressLine']
        hotels_list[index].total_cost = hotels_list[index].cost * days_amount
        if photos_flag:
            if photos_amount >= 2:
                hotels_list[index].image.append(
                    hotel_data['data']['propertyInfo']['propertyGallery']['images'][1]['image']['url'])
                if photos_amount == 3:
                    hotels_list[index].image.append(
                        hotel_data['data']['propertyInfo']['propertyGallery']['images'][2]['image']['url'])

    return tuple(hotels_list)

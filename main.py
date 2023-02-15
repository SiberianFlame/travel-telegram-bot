import json.decoder

import telebot
from telebot import types

from commands import lowprice, highprice, utils, history

if __name__ == '__main__':
    token = '5942028647:AAHKqonu2bEJbBYOpBlFqBzgMPF_pg45m-8'
    bot = telebot.TeleBot(token)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_help = types.KeyboardButton('/help')
    key_lowprice = types.KeyboardButton('/lowprice')
    key_highprice = types.KeyboardButton('/highprice')
    key_history = types.KeyboardButton('/history')
    keyboard.add(key_help, key_lowprice, key_highprice, key_history)
    params_dict = {}



    @bot.message_handler(commands=['start'])
    def start(message) -> None:
        bot.send_message(message.chat.id,
                         'Привет, я - бот!\nМои команды:'
                         '\n/lowprice - выводит самые дешевые отели в выбранном городе'
                         '\n/highprice - выводит самые дорогие отели в выбранном городе'
                         '\n/help - выводит список команд',
                         reply_markup=keyboard)



    @bot.message_handler(commands=['lowprice'])
    def lowprice_message(message) -> None:
        bot.send_message(message.from_user.id, "Введите название города")
        is_lowprice = True
        bot.register_next_step_handler(message, get_hotels_amount, is_lowprice)


    @bot.message_handler(commands=['highprice'])
    def highprice_message(message) -> None:
        bot.send_message(message.from_user.id, "Введите название города")
        is_lowprice = False
        bot.register_next_step_handler(message, get_hotels_amount, is_lowprice)


    @bot.message_handler(commands=['help'])
    def help_message(message) -> None:
        bot.send_message(message.from_user.id,
                         'Список команд:'
                         '\n/lowprice - выводит самые дешевые отели в выбранном городе'
                         '\n/highprice - выводит самые дорогие отели в выбранном городе')

    @bot.message_handler(commands=['history'])
    def history_message(message) -> None:
        if history.history_list:
            for elem in history.history_list:
                bot.send_message(message.from_user.id, 'Дата ввода команды {name}: {date}'.format(
                    name=elem.command,
                    date=elem.input_time))
                for hotel in elem.hotels:
                    result_str = '{name}\n{description}\nАдрес отеля: {address}' \
                                 '\nЦена за одну ночь: {cost}$\nИтоговая цена: {total_cost}$'.format(name=hotel.name,
                                                                                                     description=hotel.description,
                                                                                                     address=hotel.address,
                                                                                                     cost=hotel.cost,
                                                                                                     total_cost=hotel.total_cost)
                    bot.send_message(message.from_user.id, result_str)
                    if hotel.image:
                        for image in hotel.image:
                            bot.send_photo(message.from_user.id, image)

        else:
            bot.send_message(message.from_user.id, 'История поиска отсутствует!')
            start(message)



    @bot.message_handler(content_types=['text'])
    def get_text_messages(message) -> None:
        bot.send_message(message.from_user.id, "Я тебя не понимаю :( Напиши /help")


    def get_hotels_amount(message, is_lowprice):
        params_dict['town'] = message.text
        if not utils.is_city_valid(params_dict['town']):
            bot.send_message(message.from_user.id, "Ошибка: город введён неверно!\nПожалуйста, попробуйте снова.")
            start(message)
        else:
            bot.send_message(message.from_user.id, "Введите количество отелей (не больше 5)")
            bot.register_next_step_handler(message, get_photos_flag, is_lowprice)


    def get_photos_flag(message, is_lowprice):
        try:
            params_dict['hotelsAmount'] = int(message.text)
        except ValueError:
            bot.send_message(message.from_user.id,
                             "Ошибка: количество отелей введено неверно!\nПожалуйста, попробуйте снова.")
            start(message)

        else:
            if not utils.is_hotels_amount_valid(params_dict['hotelsAmount']):
                bot.send_message(message.from_user.id,
                                 "Ошибка: количество отелей введено неверно!\nПожалуйста, попробуйте снова.")
                start(message)
            else:
                bot.send_message(message.from_user.id, "Нужно ли отправлять вам фото отеля? (да/нет)")
                bot.register_next_step_handler(message, get_photos_amount, is_lowprice)


    def get_photos_amount(message, is_lowprice):
        params_dict['isPhotos'] = message.text
        if not utils.is_photos_flag_valid(params_dict['isPhotos']):
            bot.send_message(message.from_user.id, "Ошибка: неверный ввод!\nПожалуйста, попробуйте снова.")
            start(message)
        else:
            if params_dict['isPhotos'].lower() == 'да':
                params_dict['isPhotos'] = True
                bot.send_message(message.from_user.id, "Введите количество фотографий (не больше 3)")
                bot.register_next_step_handler(message, get_start_date, is_lowprice)
            else:
                params_dict['isPhotos'] = False
                params_dict['photosAmount'] = 3
                bot.send_message(message.from_user.id,
                                 "Введите планируемую дату заселения в отель (в формате дд.мм.гг):")
                bot.register_next_step_handler(message, get_end_date, is_lowprice)


    def get_start_date(message, is_lowprice):
        try:
            params_dict['photosAmount'] = int(message.text)
        except ValueError:
            bot.send_message(message.from_user.id,
                             "Ошибка: количество фото введено неверно!\nПожалуйста, попробуйте снова.")
            start(message)

        else:
            if not utils.is_photos_amount_valid(params_dict['photosAmount']):
                bot.send_message(message.from_user.id,
                                 "Ошибка: неверный ввод количества фото!\nПожалуйста, попробуйте снова.")
                start(message)
            else:
                bot.send_message(message.from_user.id,
                                 "Введите планируемую дату заселения в отель (в формате дд.мм.гг):")
                bot.register_next_step_handler(message, get_end_date, is_lowprice)


    def get_end_date(message, is_lowprice):
        params_dict['startDate'] = message.text
        bot.send_message(message.from_user.id, "Введите планируемую дату выезда из отеля (в формате дд.мм.гг):")
        bot.register_next_step_handler(message, output_func, is_lowprice)


    def output_func(message, is_lowprice):
        params_dict['endDate'] = message.text

        if not utils.is_dates_valid(params_dict['startDate'], params_dict['endDate']):
            bot.send_message(message.from_user.id, "Ошибка: неверный ввод дат!\nПожалуйста, попробуйте снова.")
            start(message)

        else:
            bot.send_message(message.from_user.id, "Пожалуйста, подождите... Ищу отели.")

            if is_lowprice:
                try:
                    hotels = lowprice.lowprice(params_dict)
                except json.decoder.JSONDecodeError or UnboundLocalError:
                    bot.send_message(message.from_user.id, "Произошла ошибка. Пожалуйста, попробуйте позже.")
                    start(message)

            else:
                try:
                    hotels = highprice.highprice(params_dict)
                except json.decoder.JSONDecodeError or UnboundLocalError:
                    bot.send_message(message.from_user.id, "Произошла ошибка. Пожалуйста, попробуйте позже.")
                    start(message)

            if isinstance(hotels, type):
                bot.send_message(message.from_user.id, "Ошибка - неверный ввод данных\nПопробуйте снова!")
            else:
                for elem in hotels:
                    result_str = '{name}\n{description}\nАдрес отеля: {address}' \
                                 '\nЦена за одну ночь: {cost}$\nИтоговая цена: {total_cost}$'.format(name=elem.name,
                                                                                                     description=elem.description,
                                                                                                     address=elem.address,
                                                                                                     cost=elem.cost,
                                                                                                     total_cost=elem.total_cost)
                    bot.send_message(message.from_user.id, result_str)
                    if elem.image:
                        for image in elem.image:
                            bot.send_photo(message.from_user.id, image)
                    start(message)


    bot.polling(none_stop=True, interval=0)

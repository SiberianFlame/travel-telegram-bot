import json.decoder

import telebot
from telebot import types

from commands import lowprice

if __name__ == '__main__':
    token = '5942028647:AAHKqonu2bEJbBYOpBlFqBzgMPF_pg45m-8'
    bot = telebot.TeleBot(token)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_help = types.KeyboardButton('\u2753 Помощь')
    key_lowprice = types.KeyboardButton('\u2B07\uFE0F Самые дешевые отели')
    keyboard.add(key_help, key_lowprice)
    params_dict = {}


    @bot.message_handler(commands=['start'])
    def start(message) -> None:
        bot.send_message(message.chat.id,
                         'Привет, я - бот!\nМои команды:'
                         '\n/lowprice - выводит самые дешевые отели в выбранном городе'
                         '\n/help - выводит список команд',
                         reply_markup=keyboard)


    @bot.message_handler(content_types=['text'])
    def get_text_messages(message) -> None:
        if message.text == '/lowprice' or message.text == '\u2B07\uFE0F Самые дешевые отели':
            bot.send_message(message.from_user.id, "Введите название города")
            bot.register_next_step_handler(message, get_hotels_amount)
        elif message.text == '/help' or message.text == '\u2753 Помощь' or message.text.lower() == 'помощь':
            bot.send_message(message.from_user.id,
                             'Список команд:'
                             '\n/lowprice - выводит самые дешевые отели в выбранном городе')
        else:
            bot.send_message(message.from_user.id, "Я тебя не понимаю :( Напиши /help")


    def get_hotels_amount(message):
        params_dict['town'] = message.text
        bot.send_message(message.from_user.id, "Введите количество отелей (не больше 5)")
        bot.register_next_step_handler(message, get_photos_flag)


    def get_photos_flag(message):
        params_dict['hotelsAmount'] = message.text
        bot.send_message(message.from_user.id, "Нужно ли отправлять вам фото отеля? (да/нет)")
        bot.register_next_step_handler(message, get_photos_amount)


    def get_photos_amount(message):
        params_dict['isPhotos'] = message.text
        if params_dict['isPhotos'].lower() == 'да':
            bot.send_message(message.from_user.id, "Введите количество фотографий (не больше 3)")
            bot.register_next_step_handler(message, get_start_date)
        else:
            params_dict['photosAmount'] = 3
            bot.send_message(message.from_user.id, "Введите планируемую дату заселения в отель (в формате дд.мм.гг):")
            bot.register_next_step_handler(message, get_end_date)

    def get_start_date(message):
        if params_dict['isPhotos'].lower() == 'да':
            params_dict['photosAmount'] = message.text
        bot.send_message(message.from_user.id, "Введите планируемую дату заселения в отель (в формате дд.мм.гг):")
        bot.register_next_step_handler(message, get_end_date)


    def get_end_date(message):
        params_dict['startDate'] = message.text
        bot.send_message(message.from_user.id, "Введите планируемую дату выезда из отеля (в формате дд.мм.гг):")
        bot.register_next_step_handler(message, lowprice_output)


    def lowprice_output(message):
        params_dict['endDate'] = message.text
        bot.send_message(message.from_user.id, "Пожалуйста, подождите... Ищу отели.")
        try:
            hotels = lowprice.lowprice(params_dict)
        except json.decoder.JSONDecodeError:
            bot.send_message(message.from_user.id, "Произошла ошибка. Пожалуйста, попробуйте позже.")

        if isinstance(hotels, type):
            bot.send_message(message.from_user.id, "Ошибка - неверный ввод данных\nПопробуйте снова!")
        else:
            for elem in hotels:
                result_str = '{name}\n{description}\nАдрес отеля: {address}' \
                             '\nЦена за одну ночь: {cost}$\nИтоговая цена: {total_cost}$'.format(name=elem['name'],
                                                                                                 description=elem[
                                                                                                     'description'],
                                                                                                 address=elem[
                                                                                                     'address'],
                                                                                                 cost=elem['cost'],
                                                                                                 total_cost=elem[
                                                                                                     'totalCost'])
                bot.send_message(message.from_user.id, result_str)
                if 'image' in elem.keys():
                    for image in elem['image']:
                        bot.send_photo(message.from_user.id, image)


    bot.polling(none_stop=True, interval=0)

import telebot
from telebot import types

if __name__ == '__main__':
    token = '5942028647:AAHKqonu2bEJbBYOpBlFqBzgMPF_pg45m-8'
    bot = telebot.TeleBot(token)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_help = types.KeyboardButton('Помощь')
    key_hello = types.KeyboardButton('Поздороваться')
    keyboard.add(key_hello, key_help)

    @bot.message_handler(commands=['start'])
    def start(message) -> None:
        bot.send_message(message.chat.id,
                         'Привет, я - бот!\nМои команды:'
                         '\n/hello - выводит надпись "Привет, мир!"'
                         '\n/help - выводит список команд',
                         reply_markup=keyboard)

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message) -> None:
        if message.text == '/hello' or message.text.lower() == 'привет' or message.text.lower() == 'поздороваться':
            bot.send_message(message.from_user.id, "Привет, мир!")
        elif message.text == '/help' or message.text.lower() == 'помощь':
            bot.send_message(message.from_user.id,
                             'Список команд:'
                             '\n/hello - выводит надпись "Привет, мир!"')
        else:
            bot.send_message(message.from_user.id, "Я тебя не понимаю :( Напиши /help")


    bot.polling(none_stop=True, interval=0)

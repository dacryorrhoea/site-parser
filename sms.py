# import telebot

# bot_token = ""
# bot = telebot.TeleBot(bot_token)

# @bot.message_handler(commands=['start'])
# def start(message):
#     chat_id = message.chat.id
#     print(chat_id)
#     bot.send_message(chat_id, "Привет, это бот!")

# bot.polling()

import requests

url = f'https://api.telegram.org/bot2043706009:AAGyOD6rkIbtv93jtWFBeEgCAoBoXYlP98I/sendMessage'
params = {
    'chat_id': '699063672',
    'text': 'Привет, мир!'
}
response = requests.get(url, params=params)
# _*_ coding: utf-8 _*_

from pprint import pprint
import KrakenAlertBot as alertbot
from KrakenAlertBot import User, Pair, Order
import requests
from flask import Flask
from flask import request
from flask import jsonify
import telebot

token = '530641125:AAHpy5d-6g1KqsAoK8wfQfj4Z5-dXrTrgGo'
URL = 'https://api.telegram.org/bot530641125:AAHpy5d-6g1KqsAoK8wfQfj4Z5-dXrTrgGo/'

app = Flask(__name__)
bot = telebot.TeleBot(token)

def send_message(chat_id, text):
    params = {
        'chat_id': chat_id,
        'text': text
    }
    r = requests.post(URL + 'sendMessage', json=params)
    print(r.json())


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         r = request.get_json()
#         pprint(r)
#         chat_id = r['message']['chat']['id']
#         command = r['message']['text']
#         print(command, chat_id)
#         send_message(chat_id, command)
#     return '<h1>Hi, man!</h1>'

# Process webhook calls
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        Flask.abort(403)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message,
                 ("Hi there, I am EchoBot.\n"
                  "I am here to echo your kind words back to you."))


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)


if __name__ == '__main__':
    app.run()



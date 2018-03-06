# _*_ coding: utf-8 _*_

# import KrakenAlertBot as alertbot
# from KrakenAlertBot import User, Pair, Order
# import requests

# from flask import Flask
# from flask import request
# from flask import jsonify
# import telebot

# token = '530641125:AAHpy5d-6g1KqsAoK8wfQfj4Z5-dXrTrgGo'
# URL = 'https://api.telegram.org/bot530641125:AAHpy5d-6g1KqsAoK8wfQfj4Z5-dXrTrgGo/'

# WEBHOOK_HOST = 'https://pamir2.pythonanywhere.com/'
# WEBHOOK_PORT = 443  # 443, 80, 88 or 8443 (port need to be 'open')
# WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

# WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
# WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

# app = Flask(__name__)
# bot = telebot.TeleBot(token)

# logger = telebot.logger
# # telebot.logger.setLevel(logging.INFO)

# def send_message(chat_id, text):
#     params = {
#         'chat_id': chat_id,
#         'text': text
#     }
#     r = requests.post(URL + 'sendMessage', json=params)
#     print(r.json())

# # @app.route('/', methods=['GET', 'POST'])
# # def index():
# #     if request.method == 'POST':
# #         r = request.get_json()
# #         chat_id = r['message']['chat']['id']
# #         command = r['message']['text']
# #         print(command, chat_id)
# #         send_message(chat_id, command)
# #     return '<h1>Hi, man!</h1>'

# #Process webhook calls
# @app.route('/', methods=['POST'])
# def webhook():
#     if request.headers.get('content-type') == 'application/json':
#         json_string = request.get_data().decode('utf-8')
#         update = telebot.types.Update.de_json(json_string)
#         bot.process_new_updates([update])
#         return ''
#     else:
#         Flask.abort(403)


# # Handle '/start' and '/help'
# @bot.message_handler(commands=['help', 'start'])
# def send_welcome(message):
#     bot.reply_to(message,
#                  ("Hi there, I am EchoBot.\n"
#                   "I am here to echo your kind words back to you."))


# # Handle all other messages
# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def echo_message(message):
#     bot.reply_to(message, message.text)


# if __name__ == '__main__':
#     app.run(host=WEBHOOK_LISTEN,
#         port=WEBHOOK_PORT,
#         ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
#         debug=True)



import flask
import telebot
import logging
import os, sys

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

API_TOKEN = '530641125:AAHpy5d-6g1KqsAoK8wfQfj4Z5-dXrTrgGo'

WEBHOOK_HOST = 'pamir2.pythonanywhere.com'
WEBHOOK_PORT = 443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

# WEBHOOK_SSL_CERT = '/home/pamir2/KrakenBot/webhook_cert.pem'  # Path to the ssl certificate
# WEBHOOK_SSL_PRIV = '/home/pamir2/KrakenBot/webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)


# logger = telebot.logger
# telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = flask.Flask(__name__)


# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'GET Works'


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


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


# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
print(WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

# Start flask server
if __name__ == '__main__':
    app.run()
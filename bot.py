#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a simple echo bot using decorators and webhook with CherryPy
# It echoes any incoming text messages and does not use the polling method.

import cherrypy
import telebot
from telebot import types
from KrakenAlertBot import User, Order, KrakenAlertBot
import time
from datetime import datetime
import threading
import config
import sys

API_TOKEN = config.token

WEBHOOK_HOST = config.host
WEBHOOK_PORT = config.port  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)

# WebhookServer, process webhook calls
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

bot = telebot.TeleBot(API_TOKEN)
engine = KrakenAlertBot()

markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
add_btn = types.KeyboardButton('/add')
dell_btn = types.KeyboardButton('/dell')
all_btn = types.KeyboardButton('/all')
pairs_list_btn = types.KeyboardButton('/pairs')
help_btn = types.KeyboardButton('/help')
contact_btn = types.KeyboardButton('/contact_us')
markup.add(add_btn, dell_btn, all_btn, pairs_list_btn, help_btn, contact_btn)


@bot.message_handler(commands=['contact_us'])
def send_contact(message):
    bot.send_message(message.chat.id, "If your want to make some proposals or you've "
                                      "found a bug, please contact us @GalinaKoljadina", reply_markup=markup)


@bot.message_handler(commands=['start'])
def send_start(message):
    user = User(message.chat.id)
    engine.put_to_db(user)
    bot.send_message(message.chat.id, """\
Greetings! I will track your orders on Kraken. Here is my commands:

/add - Add new tracking order
/dell - Delete order from tracking
/all - Shows all your tracings
/pairs - List of all available crypto pairs
/help - Just simple help
/contact_us - Information about contacting with us
""", reply_markup=markup)


@bot.message_handler(commands=['add'])
def send_add(message):
    user = User(message.chat.id)
    engine.put_to_db(user)
    bot.send_message(message.chat.id, """
Input here [short_pair_name] [> or <] [price]
For example: XBTUSD > 10000, USDTUSD < 1.01
List of supported crypto pairs you can get with command /pairs
""", reply_markup=markup)


@bot.message_handler(commands=['dell'])
def send_add(message):
    all_user_pairs_list = engine.get_orders_from_db(message.chat.id)
    if all_user_pairs_list:
        msg = bot.send_message(message.chat.id, """
Input here an ID (number before ':') of your tracking order.\n{}
""".format('\n'.join(engine.get_orders_from_db(message.chat.id))), reply_markup=markup)
        bot.register_next_step_handler(msg, input_dell_number)
    else:
        bot.send_message(message.chat.id, "You don't have tracking orders yet")


def input_dell_number(message):
    try:
        order_id = int(message.text)
        return_code = engine.del_order_from_db_with_chatid(order_id, message.chat.id)
        if return_code == 1:
            bot.send_message(message.chat.id, 'Tracking order {} removed successfully!'.format(order_id))
        else:
            bot.send_message(message.chat.id, 'Ooooops, there is some problem with ID. Check it please!')
    except ValueError:
        print(sys.exc_info())
        bot.send_message(message.chat.id, 'Order ID should be number!')


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, """
List of commands:
/add - Add new tracking order
/dell - Delete order from tracking
/all - Shows all your tracings
/pairs - List of all available crypto pairs
/help - Just simple help
/contact_us - Information about contacting with us

How to make an order:
1. Choose a pair for tracking from /pairs list
2. Type /add command
3. Type short pair name, condition (only '>' or '<') and price.
Use format: [pair_name] [condition] [price]

For example: 
XBTUSD > 10000
usdtusd < 1.01 

***Version 1.01:
You can input just currency short name to get actual price.
For example: xbt, eth, ltc, ...
""", reply_markup=markup)


@bot.message_handler(commands=['pairs'])
def send_pairs(message):
    bot.send_message(message.chat.id, """
Available pairs:
{}
""".format(engine.pairs_list_string), reply_markup=markup)


@bot.message_handler(commands=['all'])
def send_all(message):
    list_of_orders = engine.get_orders_from_db(message.chat.id)
    if list_of_orders:
        bot.send_message(message.chat.id, "I'm tracking your orders:\n" +
                         "\n".join(list_of_orders), reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "There is no tracking orders from you")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    text = message.text
    if len(text) == 3 or len(text) == 4:
        current_currency_price = engine.get_price_by_currency(text)
        bot.send_message(message.chat.id, current_currency_price)
        return 0

    try_command = engine.check_expression(message.text)
    if isinstance(try_command, tuple):
        current_pair = try_command[0]
        current_condition = try_command[1]
        current_price = try_command[2]
        current_user = engine.get_user_from_db(message.chat.id)
        order = Order(current_pair, current_condition, current_price, current_user)
        engine.put_to_db(order)

        bot.send_message(message.chat.id, 'Order has added successfully!')
        return 0
    else:
        bot.send_message(message.chat.id, try_command)
        return 1


def get_word_by_condition(condition):
    if condition == '>':
        return 'became more'
    else:
        return 'became less'


def send_ready_orders():
    while 1:
        orders_dict = engine.compareison_higher_prices()
        for key in orders_dict:
            for order in orders_dict[key]:
                print(order)
                time_now = datetime.strftime(datetime.now(), "%H:%M:%S")
                bot.send_message(order['chat_id'], '''
Attention! 
Rate {} in {} (GMT +0) {} {}.
This message was sent when rate is {}
'''.format(key, time_now, get_word_by_condition(order['condition']), order['order_price'], order['current_price']))

                engine.del_order_from_db(order['order_id'])
        time.sleep(10)


if __name__ == '__main__':
    send_ready_orders_thread = threading.Thread(target=send_ready_orders)
    send_ready_orders_thread.start()

    # Set webhook
    print(WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)
    bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    # Disable CherryPy requests log
    access_log = cherrypy.log.access_log
    for handler in tuple(access_log.handlers):
        access_log.removeHandler(handler)

    # Start cherrypy server
    cherrypy.config.update({
        'server.socket_host': WEBHOOK_LISTEN,
        'server.socket_port': WEBHOOK_PORT,
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        'server.ssl_private_key': WEBHOOK_SSL_PRIV
    })

    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
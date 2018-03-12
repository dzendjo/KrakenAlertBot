
import sys
import telebot
from telebot import types

from KrakenAlertBot import User, Order, KrakenAlertBot
import time
from datetime import datetime
import threading

API_TOKEN = '560993839:AAGNESgMvLryZaU7YX-DqQPW2FFoYQSRTJI'

bot = telebot.TeleBot(API_TOKEN)
engine = KrakenAlertBot()

markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
add_btn = types.KeyboardButton('/add')
all_btn = types.KeyboardButton('/all')
help_btn = types.KeyboardButton('/help')
pairs_list_btn = types.KeyboardButton('/pairs')
markup.add(add_btn, all_btn, help_btn, pairs_list_btn)


@bot.message_handler(commands=['start'])
def send_start(message):
    user = User(message.chat.id)
    engine.put_to_db(user)
    bot.send_message(message.chat.id, """\
Greetings! I will track your orders on Kraken. Here is my commands:

/add - Add new tracing order
/all - Shows all your tracings
/pairs - List all all available crypto pairs
/help - Just simple help
""", reply_markup=markup)


@bot.message_handler(commands=['add'])
def send_add(message):
    user = User(message.chat.id)
    engine.put_to_db(user)
    msg = bot.send_message(message.chat.id, """
Input here your pair name, condition ('>' or '<') and price
For example: XBTUSD > 10000, USDTUSD < 1.01
List of supported crypto pairs you can get with command /pairs
""")
    # bot.register_next_step_handler(msg, input_tracking_order)

# def input_tracking_order(message):
#     if message.text == '/pairs':
#         send_pairs(message)
#     else:
#         try_command = engine.check_expression(message.text)
#         if isinstance(try_command, tuple):
#             current_pair = try_command[0]
#             current_condition = try_command[1]
#             current_price = try_command[2]
#             current_user = engine.get_user_from_db(message.chat.id)
#             order = Order(current_pair, current_condition, current_price, current_user)
#             engine.put_to_db(order)
#
#             bot.send_message(message.chat.id, 'Order has added successfully!')
#         else:
#             bot.send_message(message.chat.id, try_command)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, """
List of commands:
/add - Add order for tracking
/all - List of all your tracking orders
/pairs - List of available crypto pairs
/help - List of commands and rules of adding orders

How to make an order:
1. Choose a pair for tracking from /pairs list
2. Type /add command
3. Type pair name, order condition and price

For example: XBTUSD > 10000, USDTUSD < 1.01 
""")

@bot.message_handler(commands=['pairs'])
def send_pairs(message):
    bot.send_message(message.chat.id, """
Available pairs:
{}
""".format(engine.pairs_list_string))

@bot.message_handler(commands=['all'])
def send_all(message):
    list_of_orders = engine.get_orders_from_db(message.chat.id)
    bot.send_message(message.chat.id, "I'm tracking your orders:\n" + "\n".join(list_of_orders))

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    try_command = engine.check_expression(message.text)
    if isinstance(try_command, tuple):
        current_pair = try_command[0]
        current_condition = try_command[1]
        current_price = try_command[2]
        current_user = engine.get_user_from_db(message.chat.id)
        order = Order(current_pair, current_condition, current_price, current_user)
        engine.put_to_db(order)

        bot.send_message(message.chat.id, 'Order has added successfully!')
    else:
        bot.send_message(message.chat.id, try_command)

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
    while 1:
        try:
            bot.polling()
            
        except Exception:
            print(sys.exc_info()[1])
            time.sleep(15)


# while 1:
#     print(engine.kraken_prices)
#     time.sleep(5)

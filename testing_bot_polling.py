# # This is a simple echo bot using the decorator mechanism.
# # It echoes any incoming text messages.
import sys
import telebot
from KrakenAlertBot import User, Pair, Order, KrakenAlertBot
import time

API_TOKEN = '560993839:AAGNESgMvLryZaU7YX-DqQPW2FFoYQSRTJI'

bot = telebot.TeleBot(API_TOKEN)
engine = KrakenAlertBot()


# @bot.message_handler(commands=['start'])
# def send_start(message):
#     user = User(message.chat.id)
#     engine.put_to_db(user)
#     bot.send_message(message.chat.id, """\
# Приветствую! Буду отслеживать ваши заявки на Kraken.
# Для начала ознакомьтесь со списком моих команд:
#
# /help - список команд и правила ввода заявок
# /add - добавить заявку на отслеживание курса криптопары
# /all - список всех ваших заявок
# /pair_list - список всех доступных пар
# """)
#
#
# @bot.message_handler(commands=['add'])
# def send_add(message):
#     user = User(message.chat.id)
#     engine.put_to_db(user)
#     bot.send_message(message.chat.id, """\
# Введите заявку в таком формате:
# {Пара} {Условие: < или >} {Цена}
# Пример: XBTUSD > 12300
# """)
#
#
# @bot.message_handler(commands=['help'])
# def send_help(message):
#     bot.send_message(message, """\
# Список моих команд:
# /add - добавить заявку на отслеживание курса определенной пары
# /all - список всех моих заявок
#
# Как ставить заявку:
# 1. Напишите /add
# 2. Выберите пару
# 3. Напишите условия отслеживания: < число, > число, = число
#
# Например:
# 1. /add
# 2.
# """)
#
# @bot.message_handler(commands=['all'])
# def send_all(message):
#     list_of_orders = engine.get_orders_from_db(message.chat.id)
#     bot.send_message(message.chat.id, 'Я слежу за вашими заявками:\n' + '\n'.join(list_of_orders))
#
# # Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     command = str(message.text).replace(' ', '')
#     is_ok = False
#     try:
#         pair = command[0:6]
#         condition = command[6:7]
#         price = float(command[7:].replace(',', '.'))
#         is_ok = True
#     except ValueError:
#         bot.send_message(message.chat.id, 'Не могу сконвертировать в цифру выражение "{}"'.format(command[7:]))
#     except Exception:
#         print(sys.exc_info())
#         bot.send_message(message.chat.id, 'Команда не распознана')
#
#
#     if pair not in engine.list_pairs:
#         bot.send_message(message.chat.id, 'Не могу найти пару "{}"'.format(pair))
#
#     if condition not in ['<', '>']:
#         bot.send_message(message.chat.id, 'Не понятное условие "{}"'.format(condition))
#
#     if is_ok:
#         current_pair = engine.get_pair_from_db('XBTUSD')
#         current_user = engine.get_user_from_db(message.chat.id)
#         order = Order(current_pair, condition, price, current_user)
#         engine.put_to_db(order)
#
#         bot.send_message(message.chat.id, '''
# Поздравляю, заявка успешно добавлена!
# Я оповещу вас, когда цена пары {} будет {} цены {}
# '''.format(pair, condition, price))
#
#
# if __name__ == '__main__':
#     while 1:
#         try:
#             bot.polling()
#         except Exception:
#             print(sys.exc_info()[1])
#             time.sleep(15)


while 1:
    print(engine.kraken_prices)
    time.sleep(5)

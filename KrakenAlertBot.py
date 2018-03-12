import requests
import json
import threading
import sys
import time
import re
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String)

    def __init__(self, telegram_id):
        self.telegram_id = telegram_id

    def __repr__(self):
        return '{} - {}'.format(self.id, self.telegram_id)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    pair_name = Column(String)
    condition = Column(String(1))
    price = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

    # pair = relationship("Pair", foreign_keys=[pair_id])
    user = relationship("User", foreign_keys=[user_id])

    def __init__(self, pair_name, condition, price, user):
        self.pair_name = pair_name
        self.condition = condition
        self.price = price
        self.user = user

    def __repr__(self):
        return '{}: {}, {}, {}, {}'.format(self.id, self.pair_name, self.condition, self.user, self.price)


class KrakenAlertBot:

    def __init__(self):
        db_engine = create_engine('sqlite:///db.sqlite') #,echo=True)
        self.session = sessionmaker(bind=db_engine)()
        self.pairs_json = dict(json.load(open('pairs.json')))
        self.pairs_list_string = self.get_pair_list_string()
        self.kraken_prices = self.get_prices_dict_ones()
        self.thread_get_actually_prices = threading.Thread(target=self.get_prices_dict)
        self.thread_get_actually_prices.start()

    def get_pair_list_string(self):
        i = 0
        list_pairs_string = ''
        for pair in self.pairs_json.keys():
            i += 1
            list_pairs_string += '{} - {}\n'.format(i, pair)
        return list_pairs_string

    def compareison_higher_prices(self):
        result_higher_prices_dict = {}

        for key in self.pairs_json:
            match_orders_list = []
            current_price = float(self.kraken_prices[key])
            query = self.session.query(Order).\
                filter(Order.pair_name == key, Order.condition == '>', Order.price < current_price)
            for line in query:
                match_orders_list.append({
                    'order_id': line.id,
                    'chat_id': line.user.telegram_id,
                    'order_price': line.price,
                    'current_price': current_price,
                    'condition': line.condition
                })

            query = self.session.query(Order). \
                filter(Order.pair_name == key, Order.condition == '<', Order.price > current_price)
            for line in query:
                match_orders_list.append({
                    'order_id': line.id,
                    'chat_id': line.user.telegram_id,
                    'order_price': line.price,
                    'current_price': current_price,
                    'condition': line.condition
                })
            result_higher_prices_dict[key] = match_orders_list
            self.session.commit()
        return result_higher_prices_dict

    def get_prices_dict_ones(self):
        try:
            pair_price_dict = {}
            for pair in self.pairs_json:
                r = requests.get('https://api.kraken.com/0/public/Ticker?pair={}'.format(pair)).json()
                pair_price_dict[pair] = r['result'][self.pairs_json[pair]]['c'][0]
            return pair_price_dict
            time.sleep(20)
        except Exception:
            print(sys.exc_info()[1])
            time.sleep(10)

    def get_prices_dict(self):
        while 1:
            try:
                pair_price_dict = {}
                for pair in self.pairs_json:
                    r = requests.get('https://api.kraken.com/0/public/Ticker?pair={}'.format(pair)).json()
                    pair_price_dict[pair] = r['result'][self.pairs_json[pair]]['c'][0]
                self.kraken_prices = pair_price_dict
                time.sleep(10)
            except Exception:
                print(sys.exc_info()[1])
                time.sleep(20)

    def put_to_db(self, entity):
        class_name = type(entity).__name__

        if class_name == 'User':
            if self.session.query(User.telegram_id).filter_by(telegram_id=entity.telegram_id).first():
                self.session.commit()
                return 0

        self.session.add(entity)
        self.session.commit()
        return 0

    def get_user_from_db(self, chat_id):
        user = self.session.query(User).filter_by(telegram_id=chat_id).first()
        self.session.commit()
        return user

    def get_orders_from_db(self, telegram_id):
        list_of_orders = []
        user = self.get_user_from_db(telegram_id)
        all_orders = self.session.query(Order).filter_by(user=user).all()

        for order in all_orders:
            order_as_string = '{} {} {}'.format(order.pair_name, order.condition, order.price)
            list_of_orders.append(order_as_string)

        self.session.commit()
        return list_of_orders

    def del_from_db(self, entity):
        class_name = type(entity).__name__
        self.session.query(class_name).filter_by(id=entity.id).delete
        self.session.commit()

    def del_order_from_db(self, entity_id):
        self.session.query(Order).filter_by(id=entity_id).delete()
        self.session.commit()
        print('order {} has been deleted from base'.format(entity_id))

    def get_current_rate(self, pair):
        try:
            request = requests.get('https://api.kraken.com/0/public/Ticker?pair={}'.format(pair))
            price = request.json()['result']['USDTZUSD']['c'][0]
            return price
        except Exception:
            return 'Error connection to Kraken: {}'.format(sys.exc_info()[1])

    def check_expression(self, expression):
        normalized_expretion = str(expression).replace(' ', '').replace(',', '.').upper()
        print(normalized_expretion)

        pair = re.findall(r'|'.join(self.pairs_json.keys()), normalized_expretion)
        condition = re.findall(r'[<,>]', normalized_expretion)
        price = re.findall(r'[>,<]\s*(\d+.?\d*)', normalized_expretion)

        if not pair:
            return "Cann't find pair name"
        elif not condition:
            return "Cann't find condition ('>' or '<')"
        elif not price:
            return "Cann't find price"

        return (pair[0], condition[0], float(price[0]))


import requests
import json
import threading
from kraken_request_prices import KrakenPrices
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


class Pair(Base):
    __tablename__ = 'pairs'
    id = Column(Integer, primary_key=True)
    pair_kraken_get = Column(String)
    pair_kraken_dict = Column(String)

    def __init__(self, pair_kraken_get, pair_kraken_dict):
        self.pair_kraken_get = pair_kraken_get
        self.pair_kraken_dict = pair_kraken_dict

    def __repr__(self):
        return '{} - {}'.format(self.id, self.pair_kraken_get, self.pair_kraken_dict)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    pair_id = Column(Integer, ForeignKey("pairs.id"))
    condition = Column(String(1))
    price = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

    pair = relationship("Pair", foreign_keys=[pair_id])
    user = relationship("User", foreign_keys=[user_id])

    def __init__(self, pair, condition, price, user):
        self.pair = pair
        self.condition = condition
        self.price = price
        self.user = user

    def __repr__(self):
        return '{}: {}, {}, {}, {}'.format(self.id, self.pair, self.condition, self.user, self.price)


class KrakenAlertBot:

    def __init__(self):
        db_engine = create_engine('sqlite:///db.sqlite', echo=True)
        self.session = sessionmaker(bind=db_engine)()
        self.kraken_prices = KrakenPrices().prices_dict

    def put_to_db(self, entity):
        class_name = type(entity).__name__

        if class_name == 'User':
            if self.session.query(User.telegram_id).filter_by(telegram_id=entity.telegram_id).first():
                return 1

        self.session.add(entity)
        self.session.commit()
        return 1

    def get_user_from_db(self, chat_id):
        return self.session.query(User).filter_by(telegram_id=chat_id).first()

    def get_pair_from_db(self, pair):
        return self.session.query(Pair).filter_by(pair_kraken_get=pair).first()

    def get_orders_from_db(self, telegram_id):
        list_of_orders = []
        user = self.get_user_from_db(telegram_id)
        all_orders = self.session.query(Order).filter_by(user=user).all()

        for order in all_orders:
            order_as_string = '{} {} {}'.format(order.pair.pair_kraken_get, order.condition, order.price)
            list_of_orders.append(order_as_string)

        self.session.commit()
        return list_of_orders


    def del_from_db(self, entity):
        class_name = type(entity).__name__
        self.session.query(class_name).filter_by(id=entity.id).delete
        self.session.commit()

    def get_current_rate(self, pair):
        request = requests.get('https://api.kraken.com/0/public/Ticker?pair={}'.format(pair))
        try:
            price = request.json()['result']['USDTZUSD']['c'][0]
        except Exception:
            return request.json()
        return price

    def get_my_all_bids(self):
        pass


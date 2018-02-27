import requests
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
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
    pair = Column(String)

    def __init__(self, pair):
        self.pair = pair

    def __repr__(self):
        return '{} - {}'.format(self.id, self.pair)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    pair_id = Column(Integer, ForeignKey("pairs.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    price = Column(Integer)

    pair = relationship("Pair", foreign_keys=[pair_id])
    user = relationship("User", foreign_keys=[user_id])

    def __init__(self, pair, user, price):
        self.pair = pair
        self.user = user
        self.price = price

    def __repr__(self):
        return '{}: {}, {}, {}'.format(self.id, self.pair.pair, self.user.telegram_id, self.price)


class KrakenAlertBot:
    def __init__(self):
        db_engine = create_engine('sqlite:///db.sqlite', echo=True)
        self.session = sessionmaker(bind=db_engine)()

    def put_to_db(self, entity):
        self.session.add(entity)
        self.session.commit()

    def get_user_from_db(self, telegram_id):
        return self.session.query(User).filter_by(telegram_id=telegram_id).first()

    def get_pair_from_db(self, pair):
        return self.session.query(Pair).filter_by(pair=pair).first()

    def get_orders_from_db(self, telegram_id):
        user = self.get_user_from_db(telegram_id)
        return self.session.query(Order).filter_by(user=user).all()

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


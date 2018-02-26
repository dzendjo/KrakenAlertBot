import requests
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey


class KrakenAlertBot:
    def __init__(self):
        self.db_engine = create_engine('sqlite:///db.sqlite', echo=True)
        metadata = MetaData()
        users_table = Table('users', metadata,
                            Column('id', Integer, primary_key=True),
                            Column('telegram_id', String)
                            )

        pairs_table = Table('pairs', metadata,
                            Column('id', Integer, primary_key=True),
                            Column('pair', String)
                            )

        orders_table = Table('orders', metadata,
                            Column('id', Integer, primary_key=True),
                            Column('pair_id', Integer, ForeignKey('pairs.id')),
                            Column('user_id', Integer, ForeignKey('users.id')),
                            Column('price', Integer)
                             )

        metadata.create_all(self.db_engine)



    def put_to_storage(self):
        pass

    def del_from_storage(self):
        pass

    def get_current_rate(self, pair):
        request = requests.get('https://api.kraken.com/0/public/Ticker?pair={}'.format(pair))
        try:
            price = request.json()['result']['USDTZUSD']['c'][0]
        except Exception:
            return request.json()
        return price

    def get_my_all_bids(self):
        pass


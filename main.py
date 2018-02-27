import KrakenAlertBot as alertbot
from KrakenAlertBot import User, Pair, Order


a = alertbot.KrakenAlertBot()
user1 = User('1234590111')

print(a.get_orders_from_db('12345901'))
# a.put_to_storage(user1)
# user1 = User('12345901')
# pair1 = a.session.query(Pair).filter_by(id=1).first()
# a.session.add(Order(pair1, user1, 1.001))
# print('op')
#
# a.session.commit()

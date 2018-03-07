import requests
import json
import time
import threading
import sys


class KrakenPrices:
    def __init__(self):
        self.pairs_json = dict(json.load(open('pairs.json')))
        self.prices_dict = self.get_prices_dict_ones()
        self.thread = threading.Thread(target=self.get_prices_dict)
        self.thread.start()

    def get_prices_dict_ones(self):
        try:
            pair_price_dict = {}
            for pair in self.pairs_json:
                r = requests.get('https://api.kraken.com/0/public/Ticker?pair={}'.format(pair)).json()
                pair_price_dict[pair] = r['result'][self.pairs_json[pair]]['c'][0]
            return pair_price_dict
            time.sleep(10)
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
                self.prices_dict = pair_price_dict
                time.sleep(10)
            except Exception:
                print(sys.exc_info()[1])
                time.sleep(10)


if __name__ == '__main__':
    kp = KrakenPrices()
    while 1:
        print(kp.prices_dict)
        time.sleep(5)


import json


pairs_dict = {
    'XBTUSD': 'XXBTZUSD'
}

with open('pairs.json', 'w') as f:
    json.dump(pairs_dict, f)
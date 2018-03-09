# import json
#
#
# pairs_dict = {
#     'XBTUSD': 'XXBTZUSD'
# }
#
# with open('pairs.json', 'w') as f:
#     json.dump(pairs_dict, f)

import re

pair_list = ['XBTUSD', 'USDTUSD']

s1 = 'XBTUSD < 11000.00'
s2 = 'USDTUSD < 1.0001'
s3 = 'XBTUSD>12000.00'
s4 = 'xbtusd<9009.00'

test_list = [s1, s2, s3, s4]
for s in test_list:
    print(re.findall(r'|'.join(pair_list), s))
    print(re.findall(r'[<,>]', s))
    # print(float(re.findall(r'[>,<]\s*(\d+.?\d*)', s)[0]))

a = (1, 2, 3)
print(a.__class__.__name__)
if isinstance(a, tuple):
    print('daaaaaaaaaaaa')

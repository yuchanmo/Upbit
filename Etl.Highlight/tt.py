import requests
import json
from pprint import pprint
a = requests.get('https://www.christies.com/api/discoverywebsite/auctionpages/lotsearch?action=paging&geocountrycode=KR&language=en&page=2&pagesize=30&saleid=29041&salenumber=19846&sid=8dffb0e0-ed0e-4bec-9f7e-161a707ad109&sortby=lot_number')
res = json.loads(a.text)
pprint(res)
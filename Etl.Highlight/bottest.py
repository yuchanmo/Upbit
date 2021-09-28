import requests
chat_id = '1597918203'
token = '1625539842:AAE9yZyi2Fe1U3W7j6Yy-XA5ghkWqdc_q4M'
msg = 'test\n test2 \n test3'
url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}'
requests.get(url)




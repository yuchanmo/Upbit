from dbconnector import sqlserver
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import datetime as dt
import numpy as np
import requests
from sklearn.preprocessing import MinMaxScaler

df = pd.read_sql("SELECT * FROM [CoinStar].[dbo].[MarketPrice]  where market = 'KRW-OMG' and regdate between '2021-05-01 10:29' and '2021-05-01 10:42:05'",sqlserver)
df.set_index('regdate',inplace=True)
df['trade_price']
df = df.sort_index()
print(df['market'].unique())
df[['cur_acc_trade_price','cur_trade_volume']] = df[['acc_trade_price','acc_trade_volume']].diff().apply(pd.Series)
trade_number_df = df[['cur_acc_trade_price','cur_trade_volume','trade_price']]
trade_number_df[['coef_cur_acc_trade_price','coef_cur_trade_volume','coef_trade_price']] = ((trade_number_df - trade_number_df.shift(1))/trade_number_df.shift(1)).apply(pd.Series)
cur_trade_number = trade_number_df.iloc[-1]
df['avg_5'] = df['trade_price'].rolling(window=5,min_periods=1).mean()
df['avg_10'] = df['trade_price'].rolling(window=10,min_periods=1).mean()
df['avg_20'] = df['trade_price'].rolling(window=20,min_periods=1).mean()
df[['trade_price','avg_5','avg_10','avg_20']].plot()
plt.show()
tail_df = df.tail(5)
y = tail_df[['avg_5','avg_10','avg_20']].values
y= MinMaxScaler().fit(y).transform(y)
np.linspace(0,1,5)
x = np.linspace(0,1,5).reshape(-1,1)
coefs = LinearRegression().fit(x,y).coef_
last_row = df.iloc[-1]
cur_trade_number['avg_5'] = last_row['avg_5']
cur_trade_number['avg_10'] = last_row['avg_10']
cur_trade_number['avg_20'] = last_row['avg_20']
cur_trade_number['avg_5_coef'] = coefs[0][0]
cur_trade_number['avg_10_coef'] = coefs[1][0]
cur_trade_number['avg_20_coef'] = coefs[2][0]
res_df = cur_trade_number.to_frame().T
res_df['posi_coef'] = np.all(coefs>0)
res_df['correct_order_avg'] = last_row['avg_5'] >= last_row['avg_10'] >= last_row['avg_20']
res_df['market'] = last_row['market']
res_df.reset_index()
res_df.iloc[0]
from dbconnector import sqlserver
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import datetime as dt
import numpy as np
import requests
from sklearn.preprocessing import MinMaxScaler
#5,10,20 이동평균선 우상향
#이동 평균선 정배열
#거래량 5배 이상 증가
#가격 



def calculateStats(df:pd.DataFrame):
    print(df['market'].unique())
    df.sort_index()
    df[['cur_acc_trade_price','cur_trade_volume']] = df[['acc_trade_price','acc_trade_volume']].diff().apply(pd.Series)
    trade_number_df = df[['cur_acc_trade_price','cur_trade_volume','trade_price']]
    trade_number_df[['coef_cur_acc_trade_price','coef_cur_trade_volume','coef_trade_price']] = ((trade_number_df - trade_number_df.shift(1))/trade_number_df.shift(1)).apply(pd.Series)
    cur_trade_number = trade_number_df.iloc[-1]
    df['avg_5'] = df['trade_price'].rolling(window=5,min_periods=1).mean()
    df['avg_10'] = df['trade_price'].rolling(window=10,min_periods=1).mean()
    df['avg_20'] = df['trade_price'].rolling(window=20,min_periods=1).mean()
    tail_df = df.tail(5)
    y = tail_df[['avg_5','avg_10','avg_20']].values
    y= MinMaxScaler().fit(y).transform(y)
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
    #print(res_df)
    return res_df

all_df = pd.read_sql("select regdate,market,acc_trade_price,acc_trade_volume,trade_price from MarketPrice where regdate >= dateadd(hour,-1,getdate())",sqlserver)
all_df.set_index('regdate',inplace=True)


all_res = []
for gn,g in all_df.groupby(['market']):
    print(gn)
    all_res.append(calculateStats(g))

summary_df = pd.concat(all_res,axis=0)

filter_pred = (summary_df['posi_coef'] == True) & \
              (summary_df['correct_order_avg']==True)&(summary_df['coef_cur_trade_volume']>10) & (summary_df['coef_cur_trade_volume']!=np.inf) &\
                        (summary_df['coef_trade_price']>=0.005)                                        

summary_df = summary_df[filter_pred].reset_index()
summary_df.replace([np.inf, -np.inf], np.nan, inplace=True)


if len(summary_df)>0:
    print('=================add result=======================')
    summary_df.to_sql('Summary',sqlserver,'dbo',index=False,if_exists="append")
    summary_df = summary_df.sort_values(by=['coef_cur_trade_volume','coef_trade_price'],ascending=False)
    msg ='<1분전 대비 시세>\n'
    for i,row in summary_df.iterrows():
        msg = msg + f"[COIN종목] : {row['market']} - [거래량] : {row['cur_trade_volume']} - [물량 증가량] : {round(row['coef_cur_trade_volume'],1)}배 - [가격 증가(%)] : {round(row['coef_trade_price']*100,1)}%\n"        
    t = '1625539842:AAE9yZyi2Fe1U3W7j6Yy-XA5ghkWqdc_q4M'    
    c_id = '@cocoinmaster'
    # bot = telegram.Bot(token=t)
    # bot.sendMessage(chat_id=c_id,text=msg)    
    url = f'https://api.telegram.org/bot{t}/sendMessage?chat_id={c_id}&text={msg}'
    requests.get(url)

# all_df[all_df['market']=='KRW-XTZ'].head(2)

# all_df.groupby(['market']).apply(lambda x : calculateStats(x))

# (cur_trade_number['coef_cur_acc_trade_price'] > 5.0) and \
# (cur_trade_number['coef_cur_trade_volume'] > 5.0) and \
# (cur_trade_number['coef_trade_price'] > 0.01)

# df[['trade_price','avg_5','avg_10','avg_20']].plot()
# plt.show()
# df['acc_trade_volume'].diff().plot(kind='bar')
# df['trade_volume'].plot(kind='bar')
# plt.show()
# df.columns


# import requests

# url = "https://api.upbit.com/v1/orderbook"

# response = requests.request("GET", url)

# print(response.text)
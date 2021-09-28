import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import json
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import numpy as np
from dbconnector import sqlserver
import os
import sys

pd.set_option('display.max_columns', None)
#telegram info
def sendMsgViaTelegram(msg:str):
    try:
        t = '1625539842:AAE9yZyi2Fe1U3W7j6Yy-XA5ghkWqdc_q4M'    
        c_id = '@cocoinmaster'
        url = f'https://api.telegram.org/bot{t}/sendMessage?chat_id={c_id}&text={msg}'
        requests.get(url)
    except Exception as e:
        print('failed to send via telegram')

def calculateStatus(df:pd.DataFrame):
    try:        
        # url = "https://api.upbit.com/v1/candles/minutes/1"
        # querystring = {"market":f"{market_name}","count":"25"}
        # response = requests.request("GET", url, params=querystring)
        # rows = json.loads(response.text)
        # df = pd.DataFrame(rows)
        df['candle_date_time_kst'] = pd.to_datetime(df['candle_date_time_kst'])
        df['candle_date_time_utc'] = pd.to_datetime(df['candle_date_time_utc'])
        df['index'] = df['candle_date_time_kst']
        df.set_index('index',inplace=True)
        df = df.sort_index()
        tmp = df[['candle_acc_trade_volume','trade_price']]
        df[['volume_multiple','price_multiple']]= ((tmp - tmp.shift(1))/tmp.shift(1)).apply(pd.Series)

        df['redcandle'] = df['trade_price'] > df['opening_price']
        df['avg_5'] = df['trade_price'].rolling(window=5,min_periods=1).mean()
        df['avg_10'] = df['trade_price'].rolling(window=10,min_periods=1).mean()
        df['avg_20'] = df['trade_price'].rolling(window=20,min_periods=1).mean()
        #
        tail_df = df.tail(5)
        y = tail_df[['avg_5','avg_10','avg_20']].values
        y= MinMaxScaler().fit(y).transform(y)
        x = np.linspace(0,1,5).reshape(-1,1)
        coefs = LinearRegression().fit(x,y).coef_

        res = df.iloc[-1].to_dict()
        res['avg_5_coef'] = coefs[0][0]
        res['avg_10_coef'] = coefs[1][0]
        res['avg_20_coef'] = coefs[2][0]
        res['posi_coef'] = np.all(coefs>0)
        res['correct_order_avg'] = res['avg_5'] >= res['avg_10'] >= res['avg_20']
        beam_pred = (res['posi_coef'] == True) &\
            (res['correct_order_avg']==True) &\
                (res['volume_multiple']>10) &\
                    (res['volume_multiple']!=np.inf) &\
                                (res['price_multiple']>=0.005)  
        
        summary_df = pd.Series(res).to_frame().T
        summary_df['cate']=''
        cols = ['market', 'candle_date_time_utc', 'candle_date_time_kst',
            'opening_price', 'high_price', 'low_price', 'trade_price', 'timestamp',
            'candle_acc_trade_price', 'candle_acc_trade_volume', 'unit',
            'redcandle', 'avg_5', 'avg_10', 'avg_20', 'volume_multiple',
            'price_multiple', 'avg_5_coef', 'avg_10_coef', 'avg_20_coef',
            'posi_coef', 'correct_order_avg', 'cate']

        types = ['str','datetime64','datetime64','float','float','float','float','int64',
                'float','float','float','bool','float','float','float','float','float',
                'float','float','float','bool','bool','str']

        dtypes = {c:t for c,t in zip(cols,types)}
        summary_df = summary_df.astype(dtypes)
        m = summary_df.iloc[0]['market']
        #슛팅
        if beam_pred:
            print(f'=================슛팅 : {m}=======================')               
            summary_df['cate'] = 'BEAM'
            #summary_df.to_sql('Summary',sqlserver,'dbo',index=False,if_exists="append")
            
        #슛팅 후 2연속 상승
        beam_cont_pred = (df.iloc[-2]['price_multiple'] > 0.0005) & (df.iloc[-1]['price_multiple'] > 0.0005) & (df.iloc[-2]['volume_multiple']>50)
        if beam_cont_pred:
            print(f'=================연속 슛팅 : {m} =======================')           
            summary_df['cate'] = 'BEAM_CONT'
            
        return summary_df
    except Exception as e:
        pass


#if __name__ =='__main___':
print('start monitoring point coin')
total_df = pd.read_sql("select * from MarketPrice where regdate >= dateadd(MINUTE,-30,getdate())",sqlserver)
final_df = total_df.groupby(['market']).apply(calculateStatus).reset_index(drop=True)
final_df = final_df.drop(['price_id'],axis=1)
final_df = final_df[final_df['cate']!='']
final_df.to_sql('Summary',sqlserver,'dbo',index=False,if_exists="append")

b_df = final_df[final_df['cate'] == 'BEAM']
bc_df = final_df[final_df['cate']=='BEAM_CONT']

if len(final_df)>0:
    msg = ''
    if len(b_df)>0:
        msg +=f"============[슛팅리스트]============\n"    
        for i,row in b_df.iterrows():    
            msg = msg + f"[COIN종목] : {row['market']} - [거래량] : {row['candle_acc_trade_volume']} - [물량 증가량] : {round(row['volume_multiple'],1)}배 - [가격 증가(%)] : {round(row['price_multiple']*100,1)}%\n"        
            msg+='\n'
        msg += '\n'
    if len(bc_df)>0:
        msg +=f"============[연속상승중]============\n" 
        for i,row in bc_df.iterrows():    
            msg = msg + f"[COIN종목] : {row['market']} - [거래량] : {row['candle_acc_trade_volume']} - [물량 증가량] : {round(row['volume_multiple'],1)}배 - [가격 증가(%)] : {round(row['price_multiple']*100,1)}%\n"        
            msg+='\n'
    sendMsgViaTelegram(msg)





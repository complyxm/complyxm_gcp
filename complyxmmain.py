import requests
import json
from datetime import datetime

# 現在価格を取得する
def getPrice():
    response = requests.get('https://coincheck.com/api/rate/btc_jpy',)
    rate_json = response.json()
    rate = rate_json["rate"]
    return rate

# 現在時刻を取得しunixtimeに変換
# Bitcoin現在価格を取得
currentTime = datetime.now().strftime('%Y/%m/%d')
currentPrice = getPrice()

data =  {
          'date' : '%s' % currentTime, 
          'rate' : '%s' % currentPrice
        }

# Firestoreへの格納
from google.cloud import firestore
db = firestore.Client()

# DBのprice collectionを参照する
prices_ref = db.collection(u'prices')

# pricesにデータを格納する
prices_ref.add(data)

# 以下、取得した最新データをcsvに読み込む作業を行う
pricelists = prices_ref.get()

# csv準備
import csv
with open('actualprice.csv', 'w',newline='') as csv_file:
  fieldnames = ['rate', 'date']
  writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
  writer.writeheader()

  for pricelist in pricelists:
    price_dict = pricelist.to_dict()
    writer.writerow(price_dict)

# -----------------------------------------
# 書き込み先のjsonファイルを用意する
# f = open('actualprice.json','w')
# DBの要素をjsonにdumpしていく。
#    a = '{}=>{}'.format(pricelist.id, pricelist.to_dict())
#    json.dump(a, f, ensure_ascii=True, indent=4, sort_keys=True, separators=(',', ': '))
#    print(a)
# f.close()

# jsonをcsvに変換
# df = pd.read_json("actualprice.json")
# 行列を倒置してcsvに吐き出し
# df = df.T
# df.to_csv("actualprice.csv")
# -----------------------------------------

import pandas as pd
import numpy as np

df = pd.read_csv("actualprice.csv")
df = df.rename(columns={'date': 'ds', 'rate': 'y'})
df['ds'] = pd.to_datetime(df['ds']) 
df = df.sort_values('ds')
df.to_csv("actualprice.csv")

# import matplotlib.pyplot as plt
from fbprophet import Prophet

# CSVファイル読み込み
df = pd.read_csv('actualprice.csv')
# テスト用はprocessed_data.csv
# 本番用はactualprice.csv

# 機械学習ライブラリへの読み込み
model = Prophet(yearly_seasonality = True, weekly_seasonality = True, daily_seasonality = True)

# 予測モデルへの入力
model.fit(df)
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# 30日後の予測値と今日の価格を出力
f = forecast['yhat'].tail(1).values[0]
today = df['y'].tail(1).values[0]

if f >= today:
     print("本日の価格は %d で、１ヶ月後の価格は %d となり価格上昇傾向です" % (today,f))
else:
     print("本日の価格は %d で、１ヶ月後の価格は %d となり価格下落傾向です" % (today,f))

# graph
#from fbprophet.plot import add_changepoints_to_plot
#fig = model.plot(forecast)
#a = add_changepoints_to_plot(fig.gca(), model, forecast)
#fig.savefig('a.png');
#model.plot_components(forecast).savefig('b.png');
#plt.show()
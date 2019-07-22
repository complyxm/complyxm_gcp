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

# 以下、取得した最新データをJSONに書き出す作業を行う
pricelists = prices_ref.get()
pricelists = [i.to_dict() for i in pricelists]

# 書き込み先のjsonファイルを用意する
f = open('loaded_price.json','w')
# DBの要素をjsonにdumpしていく。
json.dump(pricelists, f, ensure_ascii=True, indent=4, sort_keys=True, separators=(',', ': '))
f.close()

import pandas as pd
import numpy as np

# jsonデータをpandasに渡す
df = pd.read_json("loaded_price.json")

# jsonデータのcolumnをprophetの指定名称に書き換え、時系列でソートする
df = df.rename(columns={'date': 'ds', 'rate': 'y'})
df['ds'] = pd.to_datetime(df['ds']) 
df = df.sort_values('ds')
print(df)

# prophetライブラリを読み込む
# import matplotlib.pyplot as plt
from fbprophet import Prophet

# 予測モデルの指定
model = Prophet(yearly_seasonality = True, weekly_seasonality = True, daily_seasonality = True)

# 予測モデルへのdf読み込み
model.fit(df)
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# 30日後の予測値と今日の価格を出力
f = forecast['yhat'].tail(1).values[0]
today = df['y'].tail(1).values[0]

if f >= today:
  result = "本日の価格は %d で、１ヶ月後の価格は %d となり価格上昇傾向です" % (today,f)
else:
  result = "本日の価格は %d で、１ヶ月後の価格は %d となり価格下落傾向です" % (today,f)

def printResult():
   return result

# graph
#from fbprophet.plot import add_changepoints_to_plot
#fig = model.plot(forecast)
#a = add_changepoints_to_plot(fig.gca(), model, forecast)
#fig.savefig('a.png');
#model.plot_components(forecast).savefig('b.png');
#plt.show()
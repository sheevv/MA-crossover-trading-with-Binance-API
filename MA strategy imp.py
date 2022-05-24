#!/usr/bin/env python
# coding: utf-8

pip install python-binance
pip install bta-lib
pip install backtrader
pip install pyfolio
pip install qgrid


### **Import requirement packages**
import csv
import os
import pandas as pd
from binance.client import Client
from datetime import datetime
import btalib
import matplotlib.pyplot as plt
import backtrader as bt
import math
import qgrid
#from binance import BinanceSocketManager
#from twisted import reactor

# ## **Set API**
api_real = 'Insert your API key here'
secret_real = 'Insert secret key here'
client = Client(api_real, secret_real)

# ## **Test API Connection**
# get balances for all assets & some account information
print(client.get_account())

price = client.get_symbol_ticker(symbol="ETHUSDT")
# print full output (dictionary)
print(price)

# ## **Read Data**
def GetHistoricalData(symbol, interval, fromDate, toDate):
    klines = client.get_historical_klines(symbol, interval, fromDate, toDate)
    df = pd.DataFrame(klines, columns=['dateTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'])
    df.dateTime = pd.to_datetime(df.dateTime, unit='ms')
    df['date'] = df.dateTime.dt.strftime("%d/%m/%Y")
    df['time'] = df.dateTime.dt.strftime("%H:%M:%S")
    df = df.drop(['closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol','takerBuyQuoteVol', 'ignore'], axis=1)
    column_names = ["date", "open", "high", "low", "close"]
    df = df.reindex(columns=column_names)
    return df


fromDate = str(datetime.strptime('01/01/2018', '%d/%m/%Y'))
toDate = str(datetime.strptime('01/01/2022', '%d/%m/%Y'))
interval = Client.KLINE_INTERVAL_1DAY

btc_data = "BTCUSDT"
eth_data = "ETHUSDT"
bnb_data = "BNBUSDT"
df_btc = GetHistoricalData(btc_data, interval, fromDate, toDate)
df_eth = GetHistoricalData(eth_data, interval, fromDate, toDate)
df_bnb = GetHistoricalData(bnb_data, interval, fromDate, toDate)

df_btc['date']= pd.to_datetime(df_btc['date'])
df_eth['date']= pd.to_datetime(df_eth['date'])
df_bnb['date']= pd.to_datetime(df_bnb['date'])

df_btc = df_btc.set_index('date')
df_eth = df_eth.set_index('date')
df_bnb = df_bnb.set_index('date')

df_btc.astype('float').dtypes
df_eth.astype('float').dtypes
df_bnb.astype('float').dtypes


df_btc.to_csv("btc.csv")
#df_btc.to_csv("eth.csv")
#df_btc.to_csv("bnb.csv")

# ## **Strategy**
class price_sma_Cross(bt.Strategy):
    params = (('buy_period', 50), ('sell_period', 50), ('order_percentage', 1), ('ticker', 'BTCUSDT'))
    def __init__(self):
        self.buy_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.buy_period, plotname='50 day moving average'
        )
        self.sell_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.sell_period, plotname='50 day moving average'
        )

        self.buy_crossover = bt.indicators.CrossOver(self.data.close, self.buy_moving_average)
        self.sell_crossover = bt.indicators.CrossOver( self.data.close, self.sell_moving_average)

    def next(self):
        if self.position.size == 0:
            if self.buy_crossover > 0:
                amount_to_invest = (self.params.order_percentage * self.broker.cash)
                self.size = math.floor(amount_to_invest / self.data.close[0])
                print("BUY {} shares of {} at {}".format(self.size, self.params.ticker, self.data.close[0]))
                self.buy(size = self.size)
        if self.position.size > 0:
            if self.sell_crossover < 0:
                print("SELL {} shares of {} at {}".format(self.size, self.params.ticker, self.data.close[0]))
                self.close()


# ### **Backtest on BTC with m=50 and n=50**

cerebro = bt.Cerebro()
cerebro.broker.setcash(10000)
df_btc = pd.read_csv('btc.csv', index_col='date', parse_dates=True)
btc_feed = bt.feeds.PandasData(dataname=df_btc)
cerebro.adddata(btc_feed)
cerebro.addstrategy(price_sma_Cross)
start_portfolio_value = cerebro.broker.getvalue()
cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
cerebro.run()
end_portfolio_value = cerebro.broker.getvalue()
pnl = end_portfolio_value - start_portfolio_value
print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
print(f'Final Portfolio Value: {end_portfolio_value:2f}')
print(f'PnL: {pnl:.2f}')


# ### **Optimize parameters for BTCUSDT**
cerebro = bt.Cerebro()
df_btc = pd.read_csv('btc.csv', index_col='date', parse_dates=True)
btc_feed = bt.feeds.PandasData(dataname=df_btc)
cerebro.adddata(btc_feed)
strats = cerebro.optstrategy(price_sma_Cross, buy_period = range(40, 50), sell_period = range(40, 50))
cerebro.broker.setcash(10000)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = "sharpe")
cerebro.addanalyzer(bt.analyzers.DrawDown, _name = "drawdown")
cerebro.addanalyzer(bt.analyzers.Returns, _name = "returns")
back = cerebro.run()

par_list = [[x[0].params.buy_period, 
             x[0].params.sell_period,
             x[0].analyzers.returns.get_analysis()['rnorm100'], 
             x[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
             x[0].analyzers.sharpe.get_analysis()['sharperatio']
            ] for x in back]

par_df = pd.DataFrame(par_list, columns = ['buy_period', 'sell_period', 'return', 'dd', 'sharpe'])

par_df
par_df[par_df['return']==par_df['return'].max()] # best params in range specified in optimization cycle





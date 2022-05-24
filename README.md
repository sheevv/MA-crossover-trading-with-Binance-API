# MA crossover trading with Binance API
This python code reads data from Binance exchange with its API. After prepairing data, MA crossover strategy has been implemented. 
## Step 1: Import requirement packages
I have used packages bellow in the python code:
* python binance
* bta-lib
* backtrader
* pyfolio

## Step 2: Setting up a binance API
You may want to open an account in binance exchange (if you don't have one) and take an API and secret key to fetch data.

## Step 3: Reading data
`GetHistoricalData()` is a function implemented to read the prefered data. It takes symbol name, a time interval and date range and return a dataframe containing the OHLC data.
In the code I have taken DAILY data of BTC, ETH and BNB from 2018 til 2022, but just BTC data have been used for implementing the strategy.

## Step 4: Implementing the strategy
In the core step of the project, `Backtrader` python module is used to implement the strategy. Backtrader is a python framework for implementing strategies, backtesting
and optimization. In this project simple crossover strategy is used in order to focus on the process of implementing a trading strategy.
The main function of this framework is `nex()`, which has the strategy codes.

## Step 5: Backtest and optimization
In the final step of the project, `cerebro` class is used for backtesting and optimization of the strategy.
Three steps of using the class consists of: creating an object of `cerebro`, adding a data feed instantiated before and finally passing the strategy class directly
(here `price_sma_Cross` class).
For backtesting, the crossover strategy tested with `m=50` (as long moving average) and `n=50` (as short moving average).
`cerebro` engin has it's own analyzers, which could be used to check the performance of the strategy. Three parameters used for analyzing the performance of the
strategy in this project are: `analyzers.SharpeRatio`, `analyzers.DrawDown`, `analyzers.Returns`.

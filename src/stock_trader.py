import os
import time
import pandas as pd
from alpaca_trade_api.rest import REST, TimeFrame
from datetime import datetime, timedelta

API_KEY = os.getenv('APCA_API_KEY_ID')
API_SECRET = os.getenv('APCA_API_SECRET_KEY')
BASE_URL = os.getenv('APCA_API_BASE_URL')
api = REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')

symbol = 'TSLA'
timeframe = TimeFrame.Minute
short_window = 50
long_window = 200
interval = 60  # time interval between checks in seconds

def get_stock_data(symbol, timeframe, limit):
    stock_data = api.get_bars(symbol, timeframe, limit=limit).df
    return stock_data

def calculate_moving_average(stock_data, window):
    return stock_data['close'].rolling(window=window).mean()

def trading_strategy(symbol, stock_data):
    stock_data['short_mavg'] = calculate_moving_average(stock_data, short_window)
    stock_data['long_mavg'] = calculate_moving_average(stock_data, long_window)
    return stock_data

def execute_trade(symbol, stock_data):
    short_mavg = stock_data.iloc[-1]['short_mavg']
    long_mavg = stock_data.iloc[-1]['long_mavg']
    position = None

    try:
        position = api.get_position(symbol)
    except Exception as e:
        print(f"No position found for {symbol}: {e}")

    if short_mavg > long_mavg and position is None:
        print(f"Buy {symbol} at {stock_data.iloc[-1]['close']}")
        # Add your order execution logic here
    elif short_mavg < long_mavg and position is not None:
        print(f"Sell {symbol} at {stock_data.iloc[-1]['close']}")
        # Add your order execution logic here

def is_market_open():
    clock = api.get_clock()
    return clock.is_open

def print_daily_stats():
    portfolio = api.get_portfolio_history(period='1D', timeframe='1D')
    profit = portfolio.profit_loss.iloc[-1]
    print(f"Today's profit/loss: {profit}")

    # You can add more stats here, such as:
    # - Total portfolio value
    # - Position breakdown
    # - Performance metrics like Sharpe ratio, etc.

if __name__ == '__main__':
    print(is_market_open())
    stock_data = get_stock_data(symbol, timeframe, long_window)
    print(stock_data)
    stock_data = trading_strategy(symbol, stock_data)
    print(stock_data)
    execute_trade(symbol, stock_data)
    # while True:
    #     print("in while")
    #     try:
    #         print("in try")
    #         # stock_data = get_stock_data(symbol, timeframe, long_window)
    #         # stock_data = trading_strategy(symbol, stock_data)
    #         # execute_trade(symbol, stock_data)
    #     except Exception as e:
    #         print(f"Error occurred: {e}")
    #     # time.sleep(5)

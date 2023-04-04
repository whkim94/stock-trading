import os
import time
import pandas as pd
from alpaca_trade_api.rest import REST, TimeFrame
from datetime import datetime, timedelta

API_KEY = os.getenv('APCA_API_KEY_ID')
API_SECRET = os.getenv('APCA_API_SECRET_KEY')
BASE_URL = os.getenv('APCA_API_BASE_URL')
api = REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')

symbol = 'BTC/USD'
quantity = 1
timeframe = TimeFrame.Minute
short_window = 500
long_window = 2000
interval = 60  # time interval between checks in seconds

def is_market_open():
    clock = api.get_clock()
    return clock.is_open

def minutes_to_market_close():
    clock = api.get_clock()
    market_close_time = clock.next_close.replace(tzinfo=None)
    current_time = clock.timestamp.replace(tzinfo=None)
    return (market_close_time - current_time).seconds // 60

def get_stock_data(symbol, timeframe, limit):
    stock_data = api.get_bars(
        symbol,
        timeframe
    ).df.tail(limit)
    return stock_data

def calculate_moving_average(stock_data, window):
    return stock_data['close'].rolling(window=window).mean()

def trading_strategy(symbol, stock_data):
    stock_data['short_mavg'] = calculate_moving_average(stock_data, short_window)
    stock_data['long_mavg'] = calculate_moving_average(stock_data, long_window)
    return stock_data

def calculate_daily_profit_percentage():
    portfolio_history = api.get_portfolio_history(period='1D', timeframe='1D')
    equity_data = list(portfolio_history.equity.values())
    profit_loss_data = list(portfolio_history.profit_loss.values())
    daily_profit_percentage = (profit_loss_data[-1] / equity_data[-1]) * 100
    return daily_profit_percentage

def check_profit_and_manage_trading(trading_paused_until, symbol):
    daily_profit = calculate_daily_profit_percentage()

    if daily_profit >= 3:
        print("Daily profit goal of 3% reached. Selling all positions and pausing trading for the day.")
        api.close_all_positions()
        symbol = None
        trading_paused_until = api.get_clock().next_open.replace(tzinfo=None)
    elif daily_profit <= -2:
        print("Daily loss of 2% reached. Pausing trading for 30 minutes.")
        trading_paused_until = datetime.now() + timedelta(minutes=30)

    return trading_paused_until, symbol

def execute_trade(symbol, stock_data):
    short_mavg = stock_data.iloc[-1]['short_mavg']
    long_mavg = stock_data.iloc[-1]['long_mavg']
    position = None

    try:
        position = api.get_position(symbol)
    except Exception as e:
        print(f"No position found for {symbol}: {e}")

    time_to_market_close = minutes_to_market_close()

    if time_to_market_close <= 30 and position is not None:
        print(f"Sell {symbol} at {stock_data.iloc[-1]['close']} to avoid overnight holding")
        api.submit_order(
            symbol=symbol,
            qty=position.qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )
    elif short_mavg > long_mavg and position is None and time_to_market_close > 30:
        print(f"Buy {symbol} at {stock_data.iloc[-1]['close']}")
        api.submit_order(
            symbol=symbol,
            qty=quantity,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
    elif short_mavg < long_mavg and position is not None:
        print(f"Sell {symbol} at {stock_data.iloc[-1]['close']}")
        api.submit_order(
            symbol=symbol,
            qty=position.qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )

def print_daily_stats():
    portfolio = api.get_portfolio_history(period='1D', timeframe='1D')
    profit = portfolio.profit_loss.iloc[-1]
    print(f"Today's profit/loss: {profit}")

    # You can add more stats here, such as:
    # - Total portfolio value
    # - Position breakdown
    # - Performance metrics like Sharpe ratio, etc.

if __name__ == '__main__':
    trading_paused_until = None

    while True:
        try:
            if is_market_open():
                if trading_paused_until and datetime.now() < trading_paused_until:
                    print("Trading paused")
                    time.sleep(interval)
                    continue

                # trading_paused_until, symbol = check_profit_and_manage_trading(trading_paused_until, symbol)

                stock_data = get_stock_data(symbol, timeframe, max(short_window, long_window))
                stock_data = trading_strategy(symbol, stock_data)
                execute_trade(symbol, stock_data)
                time.sleep(interval)
            else:
                print_daily_stats()
                time.sleep(3600)  # Wait for an hour before checking again
                continue

        except Exception as e:
            print(f"Error occurred: {e}")
            
        time.sleep(interval)

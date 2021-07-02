import math
import os
import sys
from datetime import datetime, timedelta

import numpy as np

import pandas as pd
from tqdm import tqdm

DIR = '../yahoo/price_history'


def main():
    curr_date = datetime(2021, 1, 1)
    end_date = datetime(2021, 6, 30)
    rows_threshold = 250
    selected_stocks = None
    journal = []
    active_deals = []
    possible_deals = []
    capital = 1_00_000
    risk = 1000

    tckrs = get_tckrs()

    while curr_date < end_date:
        print(f'Capital for {curr_date.strftime("%Y-%m-%d")} is {capital}')
        if curr_date.isoweekday() > 6:
            # On weekends select rising stocks
            selected_stocks = []
            for f in tqdm(os.listdir(DIR), desc=f'Selecting stocks on {curr_date.strftime("%Y-%m-%d")}'):
                if f[:-4] not in tckrs:
                    continue
                data = pd.read_csv(f'{DIR}/{f}', index_col=0).dropna(axis=0).drop_duplicates().sort_index()
                if len(data) < rows_threshold: continue
                data.index = [datetime.strptime(d, '%Y-%m-%d') for d in data.index]
                data['44SMA'] = data['Close'].rolling(44).mean()
                if is_rising(data.loc[data.index < curr_date, :]):
                    selected_stocks.append(f)
        elif curr_date.isoweekday() < 6 and selected_stocks is not None:
            # after getting possible deals, based on active deals, select and execute a few
            for deal in sorted(possible_deals, key=lambda x: x['profit'], reverse=True)[:10]:
                if deal['cost'] < capital:
                    data = get_df(deal['tckr'])
                    try:
                        high = data.loc[curr_date, 'High']
                        low = data.loc[curr_date, 'Low']
                        if low <= deal['entry'] <= high:
                            active_deals.append(deal)
                            capital -= deal['cost']
                            print(f'  - Capital decreased to {capital}')
                    except KeyError:
                        pass

            # Executing deals
            capital = execute_deal(active_deals, capital, curr_date, journal)

            # On weekdays search for good deals
            possible_deals = []
            for f in tqdm(selected_stocks, desc=f'Searching for deals on {curr_date.strftime("%Y-%m-%d")}'):
                data = get_df(f[:-4])
                data['44SMA'] = data['Close'].rolling(44).mean()
                trading_data = data.loc[data.index <= curr_date, :]
                try:
                    if is_green_candle(trading_data, curr_date) and is_near_sma(trading_data, curr_date):
                        trading_details = get_trading_details(trading_data, risk)
                        if trading_details['quantity'] == 0:
                            continue
                        else:
                            trading_details['tckr'] = f[:-4]
                            trading_details['buy_date'] = curr_date + timedelta(days=1)
                            possible_deals.append(trading_details)
                except KeyError:
                    pass

        curr_date += timedelta(days=1)

    print(f'Selling remaining {len(active_deals)} stocks ... ')
    while curr_date.isoweekday() >= 6:
        curr_date += timedelta(days=1)

    deals_to_remove = []
    for curr_deal in active_deals:
        data = get_df(curr_deal['tckr'])

        try:
            high = data.loc[curr_date, 'High']
            low = data.loc[curr_date, 'Low']
            mid = (high + low) / 2

            tmp = dict()
            tmp['symbol'] = curr_deal['tckr']
            tmp['bought_at'] = curr_deal['entry']
            tmp['sold_at'] = mid
            tmp['p/l'] = curr_deal['quantity'] * (tmp['sold_at'] - tmp['bought_at'])
            tmp['bought_on'] = curr_deal['buy_date']
            tmp['sold_on'] = curr_date
            journal.append(tmp)
            deals_to_remove.append(curr_deal)
            capital += ((curr_deal['quantity'] * tmp['bought_at']) + tmp['p/l'])
            print(f'  - Capital increased to {capital}')
        except KeyError as e:
            print('* Couldn\'t sell', curr_deal['tckr'])

    for deal in deals_to_remove:
        active_deals.remove(deal)

    total_profit = 0
    print('Completed Deals')
    for j in journal:
        print('  -', j)
        total_profit += j['p/l']
    print('P/L:', total_profit)
    print('Remaining Capital:', capital)
    print('Active Deals: ')
    for ad in active_deals:
        print('  -', ad)


def get_df(tckr):
    data = pd.read_csv(f'{DIR}/{tckr}.csv', index_col=0).dropna(axis=0)
    data = data.reset_index().drop_duplicates('Date', keep='last').set_index('Date').sort_index()
    data.index = [datetime.strptime(d, '%Y-%m-%d') for d in data.index]
    return data


def get_tckrs():
    df = pd.read_csv('../data/ind_nifty200list.csv')
    return df['Symbol'].to_list()


def trendline(arr, n_days=20):
    arr = arr[-n_days:]
    idx = list(range(len(arr)))
    return np.polyfit(idx, arr, deg=1)[-2]


def is_rising(data):
    if trendline(data['44SMA'].to_list(), n_days=20) > 1:
        return True
    return False


def is_green_candle(data, date):
    latest_value = data.loc[date, :]
    if latest_value['Close'] - latest_value['Open'] > 0:
        return True
    return False


def is_near_sma(data, date):
    latest_value = data.loc[date, :]
    if abs(data['44SMA'].iloc[-1] - latest_value['Low']) / data['44SMA'].iloc[-1] * 100 < 3.5:
        return True
    return False


def get_trading_details(data, risk=1000):
    high = data['High'].iloc[-1]
    buy = math.ceil(high * 1.01)
    stoploss = math.ceil(min(data['Low'].iloc[-1], data['Low'].iloc[-2]))
    loss_per_share = buy - stoploss
    quantity = int(risk / loss_per_share)
    profit = loss_per_share * 3
    target = math.ceil(buy + profit)
    total_cost = quantity * buy

    return dict(entry=buy,
                stoploss=stoploss,
                loss=loss_per_share,
                quantity=quantity,
                exit=target,
                profit=profit,
                cost=total_cost,
                )


def execute_deal(active_deals, capital, curr_date, journal):
    deals_to_remove = []
    for curr_deal in active_deals:
        data = get_df(curr_deal['tckr'])
        try:
            high = data.loc[curr_date, 'High']
            low = data.loc[curr_date, 'Low']
            if low <= curr_deal['exit'] <= high:
                tmp = dict()
                tmp['symbol'] = curr_deal['tckr']
                tmp['bought_at'] = curr_deal['entry']
                tmp['sold_at'] = curr_deal['exit']
                tmp['p/l'] = curr_deal['quantity'] * curr_deal['profit']
                tmp['bought_on'] = curr_deal['buy_date']
                tmp['sold_on'] = curr_date
                journal.append(tmp)
                deals_to_remove.append(curr_deal)
                capital += ((curr_deal['quantity'] * tmp['bought_at']) + tmp['p/l'])
                print(f'  - Capital increased to {capital}')
            elif low <= curr_deal['stoploss'] <= high:
                tmp = dict()
                tmp['symbol'] = curr_deal['tckr']
                tmp['bought_at'] = curr_deal['entry']
                tmp['sold_at'] = curr_deal['stoploss']
                tmp['p/l'] = -curr_deal['quantity'] * curr_deal['loss']
                tmp['bought_on'] = curr_deal['buy_date']
                tmp['sold_on'] = curr_date
                journal.append(tmp)
                deals_to_remove.append(curr_deal)
                capital += ((curr_deal['quantity'] * tmp['bought_at']) + tmp['p/l'])
                print(f'  - Capital increased to {capital}')
            else:
                continue
        except KeyError:
            pass

    for deal in deals_to_remove:
        active_deals.remove(deal)
    return capital


if __name__ == '__main__':
    main()

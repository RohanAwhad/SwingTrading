import io
import os
import time

import pandas as pd
import requests

from datetime import datetime, timedelta


def get_tckrs():
    df = pd.read_csv('data/NSE_equity.csv')
    for tckr in df['SYMBOL'].to_list():
        yield tckr


def get_data(tckr):
    end_date = datetime.today()
    if os.path.exists(f'yahoo/price_history/{tckr}.csv'):
        ret = pd.read_csv(f'yahoo/price_history/{tckr}.csv', index_col=0)\
            .dropna(axis=0).drop_duplicates().sort_index()
        last_date = datetime.strptime(ret.index[-1], '%Y-%m-%d')

        if end_date - last_date >= timedelta(days=1):
            ret = update_data(end_date, last_date, ret, tckr)
    else:
        delta = timedelta(days=365)
        start_date = end_date - delta
        ret = req_data(end_date, start_date, tckr)

    ret.to_csv(f'yahoo/price_history/{tckr}.csv')
    return ret.dropna(axis=0).drop_duplicates().sort_index()


def update_data(end_date, last_date, ret, tckr):
    print(f'Updating {tckr} ...')
    recent_df = req_data(end_date, last_date, tckr)
    ret = pd.concat((ret, recent_df), axis=0).drop_duplicates().sort_index()
    return ret


def req_data(end_date, start_date, tckr):
    time.sleep(5)
    end_date = int(end_date.timestamp())
    start_date = int(start_date.timestamp())
    url = f'https://query1.finance.yahoo.com/v7/finance/download/{tckr}.NS?period1={start_date}&period2={end_date}&interval=1d&events=history&includeAdjustedClose=true'
    data = requests.get(url).text
    df = pd.read_csv(io.StringIO(data), index_col=0)
    return df

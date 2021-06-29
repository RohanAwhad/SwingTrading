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
    if os.path.exists(f'yahoo/price_history/{tckr}.csv'):
        ret = pd.read_csv(f'yahoo/price_history/{tckr}.csv', index_col=0).dropna(axis=0).drop_duplicates().sort_index()

        last_date = sorted(ret.index.to_list())[-1]
        last_date = datetime.strptime(last_date, '%Y-%m-%d')
        end_date = datetime.today()

        if end_date - last_date >= timedelta(days=1):
            end_date = int(end_date.timestamp())
            last_date = int(last_date.timestamp())

            time.sleep(5)
            url = f'https://query1.finance.yahoo.com/v7/finance/download/{tckr}.NS?period1={last_date}&period2={end_date}&interval=1d&events=history&includeAdjustedClose=true'
            data = requests.get(url).text
            recent_df = pd.read_csv(io.StringIO(data), index_col=0)

            ret = pd.concat((ret, recent_df), axis=0).drop_duplicates().sort_index()
            ret.to_csv(f'yahoo/price_history/{tckr}.csv')
    else:
        end_date = datetime.today()
        delta = timedelta(days=366)
        start_date = end_date - delta
        end_date = int(end_date.timestamp())
        start_date = int(start_date.timestamp())

        time.sleep(5)
        url = f'https://query1.finance.yahoo.com/v7/finance/download/{tckr}.NS?period1={start_date}&period2={end_date}&interval=1d&events=history&includeAdjustedClose=true'
        data = requests.get(url).text
        ret = pd.read_csv(io.StringIO(data), index_col=0)
        ret.to_csv(f'yahoo/price_history/{tckr}.csv')

    return ret.drop_duplicates().sort_index()

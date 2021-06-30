import os

import numpy as np

from datetime import datetime, timedelta

from src.historical_prices import get_tckrs, get_data
from src.utils import save_txt, load_txt


def get_rising_stocks():
    if is_outdated():
        update_rising_stocks()

    return load_txt(f'selection/{get_latest_selection().strftime("%d-%B-%Y")}.txt').split('\n')


def is_outdated():
    latest_date = get_latest_selection()
    sunday_date = datetime.today() - timedelta(days=datetime.today().isoweekday())
    return sunday_date - latest_date > timedelta(days=2)


def get_latest_selection():
    return max([datetime.strptime(x.split('.')[0], '%d-%B-%Y') for x in os.listdir('selection')])


def trendline(arr, n_days):
    arr = arr[-n_days:]
    idx = list(range(len(arr)))
    return np.polyfit(idx, arr, deg=1)[-2]


def update_rising_stocks():
    tckrs = get_tckrs()
    rising_stocks = []

    for i, tckr in enumerate(tckrs):
        print(f'{i}] Loading {tckr} prices ...')
        try:
            data = get_data(tckr)
            if trendline(data['Close'].rolling(44).mean().to_list(), n_days=20) > 0.5:
                rising_stocks.append(tckr)

        except Exception as e:
            print('   * Failed', e)

    save_txt('\n'.join(rising_stocks), f'selection/{datetime.today().strftime("%d-%B-%Y")}.txt')

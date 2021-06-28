import sys

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

import requests

end_date = datetime.today()
# start_date = datetime(2019, 1, 1)
delta = timedelta(days=365)
start_date = end_date - delta

end_date = int(end_date.timestamp())
start_date = int(start_date.timestamp())


def get_tckrs():
    df = pd.read_csv('data/NSE_equity.csv')
    for tckr in df['SYMBOL'].to_list():
        yield tckr


def get_data(tckr, start_date, end_date):
    url = f'https://query1.finance.yahoo.com/v7/finance/download/{tckr}.NS?period1={start_date}&period2={end_date}&interval=1d&events=history&includeAdjustedClose=true'
    with open(f'yahoo/price_history/{tckr}.csv', 'w') as f:
        f.write(requests.get(url).text)
    return pd.read_csv(f'yahoo/price_history/{tckr}.csv', index_col=0).dropna(axis=0)


def plot(data, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=data['Close'], x=data.index, name='Close'))
    fig.add_trace(go.Scatter(y=data['Close'].rolling(44).mean(), x=data.index, name='44 SMA'))
    fig.update_layout(title=title)
    return fig


def main():
    tckrs = get_tckrs()
    if len(sys.argv) > 1:
        prev_idx = int(sys.argv[1])
    else:
        prev_idx = 0

    for i, tckr in enumerate(tckrs):
        if i < prev_idx:
            continue
        print(f'{i}] Loading {tckr} prices ...')
        try:
            data = get_data(tckr, start_date, end_date)
            fig = plot(data, tckr)
            fig.write_html(f'yahoo/plots/html/{tckr}.html')
            fig.write_image(f'yahoo/plots/images/{tckr}.png')
        except Exception as e:
            print('   * Failed', e)


if __name__ == '__main__':
    main()

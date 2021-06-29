import numpy as np
import plotly.graph_objects as go
import sys
import time

from src.historical_prices import get_tckrs, get_data


def plot(data, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=data['Close'], x=data.index, name='Close'))
    fig.add_trace(go.Scatter(y=data['Close'].rolling(44).mean(), x=data.index, name='44 SMA'))
    fig.update_layout(title=title)
    return fig


def trendline(arr, n_days):
    arr = arr[-n_days:]
    idx = list(range(len(arr)))
    return np.polyfit(idx, arr, deg=1)[-2]


def main():
    # tckrs = ['3MINDIA', '63MOONS', 'AARON', 'AARTIDRUGS', 'AARTISURF', 'AAVAS', 'SBIN', 'ABAN', 'DRCSYSTEMS']
    tckrs = get_tckrs()
    rising_stocks = []
    if len(sys.argv) > 1:
        prev_idx = int(sys.argv[1])
    else:
        prev_idx = 0

    for i, tckr in enumerate(tckrs):
        if i < prev_idx:
            continue
        print(f'{i}] Loading {tckr} prices ...')
        try:
            data = get_data(tckr)
            if trendline(data['Close'].rolling(44).mean().to_list(), n_days=20) > 0.5:
                rising_stocks.append(tckr)

            # fig = plot(data, tckr)
            # fig.write_image(f'yahoo/plots/images/{tckr}.png')
        except Exception as e:
            print('   * Failed', e)
    print(rising_stocks)


if __name__ == '__main__':
    main()

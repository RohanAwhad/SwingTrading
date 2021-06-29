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


def main():
    tckrs = get_tckrs()
    if len(sys.argv) > 1:
        prev_idx = int(sys.argv[1])
    else:
        prev_idx = 0

    for i, tckr in enumerate(tckrs):
        tckr = 'SBIN'
        if i < prev_idx:
            continue
        print(f'{i}] Loading {tckr} prices ...')
        try:
            data = get_data(tckr)
            print('  - Got data')
            fig = plot(data, tckr)
            fig.write_image(f'yahoo/plots/images/{tckr}.png')
            time.sleep(5)
        except Exception as e:
            print('   * Failed', e)
        break


if __name__ == '__main__':
    main()

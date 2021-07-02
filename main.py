import math
import pandas as pd
import streamlit as st

from src.historical_prices import get_data
from src.rising_stocks import get_rising_stocks
from src.visualizer import plot_44SMA

st.set_page_config(layout='wide')

@st.cache
def get_green_candles(stock_list):
    ret = []
    for tckr in stock_list:
        try:
            data = get_data(tckr)
            latest_value = data.iloc[-1, :]
            if latest_value['Close'] - latest_value['Open'] > 0:
                print(f'Latest candle is green for {tckr}')
                sma = data['Close'].rolling(44).mean()
                if abs(sma.iloc[-1] - latest_value['Low'])/sma.iloc[-1] * 100 < 3.5:
                    ret.append(tckr)
        except Exception as e:
            print(e)
            continue
    print(f'Selected {len(ret)} stocks')
    return ret


def trading_value(data, risk=1000):
    high = data['High'].iloc[-1]
    buy = math.ceil(high * 1.01)
    stoploss = math.ceil(min(data['Low'].iloc[-1], data['Low'].iloc[-2]))
    loss_per_share = buy - stoploss
    quantity = int(risk/loss_per_share)
    target = math.ceil(buy + (loss_per_share * 2))
    total_cost = quantity * buy

    ret = pd.DataFrame(dict(entry=[buy],
                            stoploss=[stoploss],
                            loss=[loss_per_share],
                            quantity=[quantity],
                            exit=[target],
                            profit=[loss_per_share*2],
                            cost=[total_cost], 
                            ))
    return ret

def main():
    # selected_stocks = get_green_candles(get_rising_stocks())
    selected_stocks = pd.read_csv('data/ind_nifty200list.csv')['Symbol'].to_list()
    col_1, col_2 = st.beta_columns(2)
    try:
        stock = col_1.selectbox('Select a stock to view its prices', selected_stocks)
        data = get_data(stock)
        # col_2.table(trading_value(data))
        st.plotly_chart(plot_44SMA(data, stock))
    except Exception as e:
        st.write(f'Failed to load {stock}. {e}')


if __name__ == '__main__':
    main()

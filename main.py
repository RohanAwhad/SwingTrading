import streamlit as st

from tqdm import tqdm 

from src.historical_prices import get_data
from src.rising_stocks import get_rising_stocks
from src.visualizer import plot_44SMA

st.set_page_config(layout='wide')

def get_green_candles(stock_list):
    ret = []
    for tckr in tqdm(stock_list):
        data = get_data(tckr)
        latest_value = data.iloc[-1, :]
        if latest_value['Close'] - latest_value['Open'] > 0:
            print(f'Latest candle is green for {tckr}')
            ret.append(tckr)
    return ret


def main():
    try:
        selected_stocks = get_green_candles(get_rising_stocks())
        stock = st.selectbox('Select a stock to view its prices', selected_stocks)
        data = get_data(stock)
        fig = plot_44SMA(data, stock)
        st.plotly_chart(fig)
    except Exception as e:
        st.write(f'Failed to load {stock}. {e}')


if __name__ == '__main__':
    main()

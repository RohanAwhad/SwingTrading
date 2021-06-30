import streamlit as st

from src.historical_prices import get_data
from src.rising_stocks import get_rising_stocks
from src.visualizer import plot_44SMA

st.set_page_config(layout='wide')

def main():
    selected_stocks = get_rising_stocks()
    stock = st.selectbox('Select a stock to view its prices', selected_stocks)
    try:
        data = get_data(stock)
        fig = plot_44SMA(data, stock)
        st.plotly_chart(fig)
    except Exception as e:
        st.write(f'Failed to load {stock}. {e}')


if __name__ == '__main__':
    main()

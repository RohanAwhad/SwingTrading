import plotly.graph_objects as go


def plot_44SMA(data, title):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'],
                                 high=data['High'], low=data['Low'], close=data['Close'], name='Daily'))

    fig.add_trace(go.Scatter(y=data['Close'].rolling(44).mean(), x=data.index, name='44 SMA'))
    fig.update_layout(title=title, width=2400, height=1000)
    return fig



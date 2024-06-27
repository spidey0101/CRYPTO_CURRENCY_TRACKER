import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from dateutil.relativedelta import relativedelta
import requests
from bs4 import BeautifulSoup

# Set up the title and sidebar
st.title('Cryptocurrency Tracker')
st.sidebar.title('Options')

# Expanded list of cryptocurrencies
crypto_list = [
    'BTC-USD', 'ETH-USD', 'LTC-USD', 'XRP-USD', 'BCH-USD', 'ADA-USD', 'LINK-USD', 'DOT-USD', 'BNB-USD', 
    'DOGE-USD', 'SOL-USD', 'UNI-USD', 'MATIC-USD', 'AVAX-USD', 'ALGO-USD'
]

# Sidebar inputs
crypto_mapping = st.sidebar.selectbox('Select a cryptocurrency', crypto_list)
start_date = st.sidebar.date_input('Start date', date.today() - relativedelta(months=1))
end_date = st.sidebar.date_input('End date', date.today())
interval = st.sidebar.selectbox("Select a time period", ["1d", "5d", "1wk", "1mo", "3mo", "6mo"])
selected_value = st.sidebar.selectbox("Select a value to display", ["Open", "High", "Low", "Close", "Volume"])
chart_type = st.sidebar.selectbox("Select chart type", ["Line", "Bar", "Scatter", "Candlestick"])
show_moving_averages = st.sidebar.checkbox("Show Moving Averages")
ma_periods = st.sidebar.multiselect("Select MA Periods", [5, 10, 20, 50, 100, 200], default=[20])

# Function to scrape news
def get_crypto_news():
    url = 'https://cointelegraph.com/tags/cryptocurrencies'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = soup.find_all('a', class_='post-card-inline__title-link')
    news = []
    for headline in headlines[:10]:  # Get top 10 headlines
        title = headline.get_text(strip=True)
        link = f"https://cointelegraph.com{headline['href']}"
        news.append({'title': title, 'link': link})
    return news

# Fetch data on button click
if st.sidebar.button('Track cryptocurrency'):
    try:
        crypto_history = yf.download(crypto_mapping, start=start_date, end=end_date, interval=interval)
        
        # Display selected value chart
        if chart_type == "Line":
            fig = px.line(crypto_history, x=crypto_history.index, y=selected_value, title=f'{crypto_mapping} {selected_value} Price')
        elif chart_type == "Bar":
            fig = px.bar(crypto_history, x=crypto_history.index, y=selected_value, title=f'{crypto_mapping} {selected_value} Price')
        elif chart_type == "Scatter":
            fig = px.scatter(crypto_history, x=crypto_history.index, y=selected_value, title=f'{crypto_mapping} {selected_value} Price')
        elif chart_type == "Candlestick":
            fig = go.Figure(data=[go.Candlestick(x=crypto_history.index,
                                                 open=crypto_history['Open'],
                                                 high=crypto_history['High'],
                                                 low=crypto_history['Low'],
                                                 close=crypto_history['Close'])])
            fig.update_layout(title=f'{crypto_mapping} Candlestick Chart', xaxis_title='Date', yaxis_title='Price')

        # Display moving averages if selected
        if show_moving_averages:
            for period in ma_periods:
                crypto_history[f'MA_{period}'] = crypto_history['Close'].rolling(window=period).mean()
                fig.add_scatter(x=crypto_history.index, y=crypto_history[f'MA_{period}'], mode='lines', name=f'MA {period}')

        st.plotly_chart(fig)

        # Display volume chart
        fig_vol = go.Figure(data=[go.Bar(x=crypto_history.index, y=crypto_history['Volume'], name='Volume')])
        fig_vol.update_layout(title=f'{crypto_mapping} Trading Volume', xaxis_title='Date', yaxis_title='Volume')
        st.plotly_chart(fig_vol)

        # Display basic statistics
        st.write(f"### {crypto_mapping} Basic Statistics")
        st.write(crypto_history.describe())

        # Display a table of the fetched data
        st.write(f"### {crypto_mapping} Historical Data")
        st.write(crypto_history)

        # Display percentage change
        st.write(f"### {crypto_mapping} Percentage Change")
        crypto_history['Percentage Change'] = crypto_history['Close'].pct_change() * 100
        fig_pct = px.line(crypto_history, x=crypto_history.index, y='Percentage Change', title=f'{crypto_mapping} Daily Percentage Change')
        st.plotly_chart(fig_pct)

        # Display correlation matrix with other cryptocurrencies
        st.write("### Correlation with Other Cryptocurrencies")
        correlation_data = pd.DataFrame()
        for crypto in crypto_list:
            correlation_data[crypto] = yf.download(crypto, start=start_date, end=end_date, interval=interval)['Close']
        correlation_matrix = correlation_data.corr()
        fig_corr = px.imshow(correlation_matrix, title='Cryptocurrency Correlation Matrix')
        st.plotly_chart(fig_corr)

    except Exception as e:
        st.error(f"Failed to retrieve data for {crypto_mapping}. Error: {e}")

    # Display recent news
    st.write("### Recent News")
    news = get_crypto_news()
    if news:
        for article in news:
            st.write(f"[{article['title']}]({article['link']})")
    else:
        st.write("Failed to retrieve news.")

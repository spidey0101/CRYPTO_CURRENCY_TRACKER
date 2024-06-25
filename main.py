import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from dateutil.relativedelta import relativedelta

# Set up the title and sidebar
st.title('Cryptocurrency Tracker')
st.sidebar.title('Options')

# Sidebar inputs
crypto_mapping = st.sidebar.selectbox('Select a cryptocurrency', ['BTC-USD', 'ETH-USD', 'LTC-USD'])
start_date = st.sidebar.date_input('Start date', date.today() - relativedelta(months=1))
end_date = st.sidebar.date_input('End date', date.today())
time_period = st.sidebar.selectbox("Select a time period", ["1d", "5d", "1mo", "3mo", "6mo"])
selected_value = st.sidebar.selectbox("Select a value to display", ["Open", "High", "Low", "Close", "Volume"])

# Fetch data on button click
if st.sidebar.button('Track cryptocurrency'):
    crypto_history = yf.download(crypto_mapping, start=start_date, end=end_date, interval=time_period)

    # Display selected value chart
    fig = px.line(crypto_history, x=crypto_history.index, y=selected_value, title=f'{crypto_mapping} {selected_value} Price')
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
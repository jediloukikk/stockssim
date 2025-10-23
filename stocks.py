from stocknews import StockNews
import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData

st.title('Stock Overview')
st.text('This website allows you to view the fundamentals & technicals '
        'of any listed company by using its ticker')
ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

data = yf.download(ticker, start=start_date, end=end_date)
if data is None or data.empty:
    st.warning('No data returned. Check ticker and date range.')
else:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]

    fig = px.line(data, x=data.index, y='Close', title=ticker)
    st.plotly_chart(fig)

pricing_data, fundamental_data, news = st.tabs(
    ["Pricing Data", "Fundamental Data", "Top 10 News"])

with pricing_data:
    st.header('Price Movements')
    data2 = data
    data2['% Change'] = data['Close']/data['Close'].shift(1)-1
    data2.dropna(inplace=True)
    st.write(data2)
    annual_return = data2['% Change'].mean()*252*100
    st.write('Annual Return is', annual_return, '%')
    stdev = np.std(data2['% Change'])*np.sqrt(252)
    st.write('Standard Deviation is ', stdev*100, '%')
    st.write('Risk Adj. Return is', annual_return/(stdev*100))


with fundamental_data:
    st.write('Fundamental')
    key = '80NUFWCJS4MP6WST'
    fd = FundamentalData(key, output_format='pandas')
    st.subheader('Balance Sheet')
    balance_sheet, meta_data = fd.get_balance_sheet_annual(ticker)
    bs = balance_sheet.T[2:]
    bs.columns = list(balance_sheet.T.iloc[0])
    st.write(bs)
    st.subheader('Income Statement')
    income_statement, meta_data = fd.get_income_statement_annual(ticker)
    is1 = income_statement.T[2:]
    is1.columns = list(income_statement.T.iloc[0])
    st.write(is1)
    st.subheader('Cash Flow Statement')
    cash_flow, meta_data = fd.get_cash_flow_annual(ticker)
    cf = cash_flow.T[2:]
    cf.columns = list(cash_flow.T.iloc[0])
    st.write(cf)

with news:
    st.header(f'News of {ticker}')
    sn = StockNews(ticker, save_news=False)
    df_news = sn.read_rss()
    for i in range(10):
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i])
        st.write(df_news['title'][i])
        st.write(df_news['summary'][i])
        title_sentiment = df_news['sentiment_title'][i]
        st.write(f'Title Sentiment {title_sentiment}')
        news_sentiment = df_news['sentiment_summary'][i]
        st.write(f'News Sentiment {news_sentiment}')

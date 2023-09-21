import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

ric = 'NQ=F'
period = 'max'
# period= 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max

time_frames = ['1m', '5m','15m', '1h','1d','1wk','1mo']
# Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
# Intraday data cannot extend last 60 days

start = datetime.timedelta(days=60)
# start: str
#     Download start date string (YYYY-MM-DD) or _datetime, inclusive.
#     Default is 1900-01-01
#     E.g. for start="2020-01-01", the first data point will be on "2020-01-01"
# end: str
#     Download end date string (YYYY-MM-DD) or _datetime, exclusive.
#     Default is now
#     E.g. for end="2023-01-01", the last data point will be on "2022-12-31"

data_path = r'2304_dsft_thebridge\2-Data_Analysis\Entregas\EDA\data'

for time_frame in time_frames:
    ticker = yf.Ticker(ric)
    data = ticker.history(period=period, interval=time_frame, start=start, end=datetime.now()) 

    data.to_csv(os.path.join(data_path, f'{ric}_{time_frame}_yfinance.csv'))

print('ok')

# type(data)

# data.info()

# print(data, data.describe())


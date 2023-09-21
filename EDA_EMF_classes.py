import yfinance as yf
import os


class time_frame():
    def __init__(self, ric='NQ=F', time_frame='1d', period='1mo'):
        self.ric = ric
        self.time_frame = time_frame
        self.period = period
        self.get_data()

    def get_data ():
        for time_frame in time_frames:
            ticker = yf.Ticker(ric)
            data = ticker.history(period=period, interval=time_frame) 

            data.to_csv(os.path.join(data_path, f'{self.ric}_{self.time_frame}_yfinance.csv'))

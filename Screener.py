import pandas as pd

pd.set_option('display.max_columns', 1000)  
pd.set_option('display.max_rows', 1000)  
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

from Downloader import Downloader
from HelperTA import HelperTA

class Screener:
    def __init__(self):
        self.downloader = Downloader()
        self.hta = HelperTA()
    
    def screen(self):
        self.downloader.download(period='1y')
        data = self.downloader.data['Close']

        self.marketCycles = self.hta.MarketCycle(data, data, data, 
                                            donchianPeriod=14, donchianSmoothing=3, 
                                            rsiPeriod=14, rsiSmoothing=3, 
                                            srsiPeriod=20, srsiSmoothing=3, srsiK=5, srsiD=5, 
                                            rsiWeight=0.5, srsiWeight=1, dcoWeight=1
                                            )
        self.sellList = self.marketCycles.loc[:, self.marketCycles.iloc[-1] >= 80].iloc[-1].sort_values(ascending=False)
        self.buyList = self.marketCycles.loc[:, self.marketCycles.iloc[-1] <= 20].iloc[-1].sort_values(ascending=True)

    
    def summary(self, watchlist):
        close = self.downloader.data["Close"][watchlist.index]
        df = pd.DataFrame(index=watchlist.index, columns=["Symbol", "MarketCycle", "close", "1D-change", "5D-change", "20D-change", "Exchange"])
        df["Symbol"] = watchlist.index
        df["MarketCycle"] = watchlist
        df["close"] = close.iloc[-1]
        df["1D-change"] = (close.iloc[-1]-close.iloc[-2])/close.iloc[-2]*100
        df["5D-change"] = (close.iloc[-1]-close.iloc[-6])/close.iloc[-6]*100
        df["20D-change"] = (close.iloc[-1]-close.iloc[-20])/close.iloc[-20]*100
        df["Exchange"] = self.downloader.stocklist[self.downloader.stocklist['Symbol'].isin(watchlist.index)].set_index('Symbol')["Exchange"]
        return df
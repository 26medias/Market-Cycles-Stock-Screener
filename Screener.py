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

        self.DCO, DCOs = self.hta.DCO(data, donchianPeriod=200, smaPeriod=3)

        curr = -4
        prev = -5

        self.processed = pd.DataFrame(index=self.marketCycles.iloc[curr].index, columns=["Symbol", "MarketCycle", "DCO", "close", "1D-change", "5D-change", "20D-change", "Exchange"])
        self.processed["Symbol"] = self.marketCycles.iloc[curr].index
        self.processed["MarketCycle"] = self.marketCycles.iloc[curr]
        self.processed["MarketCycle_prev"] = self.marketCycles.iloc[prev]
        self.processed["DCO"] = self.DCO.iloc[curr]
        self.processed["close"] = data.iloc[curr]
        self.processed["1D-change"] = (data.iloc[curr]-data.iloc[prev])/data.iloc[prev]*100
        self.processed["5D-change"] = (data.iloc[curr]-data.iloc[-6])/data.iloc[-6]*100
        self.processed["20D-change"] = (data.iloc[curr]-data.iloc[-20])/data.iloc[-20]*100
        self.processed["Exchange"] = self.downloader.stocklist[self.downloader.stocklist['Symbol'].isin(self.marketCycles.iloc[curr].index)].set_index('Symbol')["Exchange"]

        self.buySignals = self.processed[(self.processed['MarketCycle'] > 20) & (self.processed['MarketCycle_prev'] <= 20)]
        self.sellSignals = self.processed[(self.processed['MarketCycle'] < 80) & (self.processed['MarketCycle_prev'] >= 80)]
        self.buySignalsInTrend = self.processed[(self.processed['MarketCycle'] > 20) & (self.processed['MarketCycle_prev'] <= 20) & (self.processed['DCO'] > 50)]
        self.sellSignalsInTrend = self.processed[(self.processed['MarketCycle'] < 80) & (self.processed['MarketCycle_prev'] >= 80) & (self.processed['DCO'] < 50)]
        self.buySignalsCounterTrend = self.processed[(self.processed['MarketCycle'] > 20) & (self.processed['MarketCycle_prev'] <= 20) & (self.processed['DCO'] < 50)]
        self.sellSignalsCounterTrend = self.processed[(self.processed['MarketCycle'] < 80) & (self.processed['MarketCycle_prev'] >= 80) & (self.processed['DCO'] > 50)]

        return self.sellSignals
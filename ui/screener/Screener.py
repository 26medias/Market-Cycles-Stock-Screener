import pandas as pd

pd.set_option('display.max_columns', 1000)  
pd.set_option('display.max_rows', 1000)  
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

from screener.Downloader import Downloader
from screener.HelperTA import HelperTA

class Screener:
    def __init__(self):
        self.downloader = Downloader()
        self.hta = HelperTA()
        self.timeframe = None
        self.filtered = None
        self.date = ""
    
    # Pull the data
    def pullData(self, open_filename=None):
        self.downloader.download(period='10y', open_filename=open_filename)

    # Build the data (daily)
    def build_daily(self, settings=None):
        print("build_daily", settings)
        if self.downloader.downloaded is False:
            self.downloader.download(period='1y')
        self.timeframe = "Daily"
        data = self.downloader.data['Close']

        self.marketCycles = self.hta.MarketCycle(data, data, data, 
                                            donchianPeriod=int(settings["donchian_period"]), donchianSmoothing=3, 
                                            rsiPeriod=int(settings['rsi_period']), rsiSmoothing=3, 
                                            srsiPeriod=int(settings['srsi_period']), srsiSmoothing=3, srsiK=5, srsiD=5, 
                                            rsiWeight=settings['rsi_weight'], srsiWeight=settings['srsi_weight'], dcoWeight=settings['donchian_weight']
                                            )

        self.DCO, DCOs = self.hta.DCO(data, donchianPeriod=20, smaPeriod=3)

        curr = int(settings["curr"])
        prev = curr-1

        #print("data")
        #print(data.count())

        self.processed = pd.DataFrame(index=self.marketCycles.iloc[curr].index, columns=["Symbol", "DCO", "MarketCycle", "MarketCycle_prev", "1D-change", "5D-change", "20D-change", "close", "Exchange", "Datapoints"])
        self.processed["Symbol"] = self.marketCycles.iloc[curr].index
        self.processed["MarketCycle"] = self.marketCycles.iloc[curr]
        self.processed["MarketCycle_prev"] = self.marketCycles.iloc[prev]
        self.processed["DCO"] = self.DCO.iloc[curr]
        self.processed["close"] = data.iloc[curr]
        self.processed["1D-change"] = (data.iloc[curr]-data.iloc[prev])/data.iloc[prev]*100
        self.processed["5D-change"] = (data.iloc[curr]-data.iloc[prev-5])/data.iloc[prev-5]*100
        self.processed["20D-change"] = (data.iloc[curr]-data.iloc[prev-20])/data.iloc[prev-20]*100
        self.processed["Exchange"] = self.downloader.stocklist[self.downloader.stocklist['Symbol'].isin(self.marketCycles.iloc[curr].index)].set_index('Symbol')["Exchange"]
        self.processed["Datapoints"] = data.count()
        self.processed = self.processed.dropna()

        self.date = self.marketCycles.iloc[curr].name.strftime('%Y-%m-%d %H:%M:%S')

        return self.processed
    



    # Build the data (monthly)
    def build_monthly(self, settings=None):
        print("screen_monthly", settings)
        if self.downloader.downloaded is False:
            self.downloader.download(period='1y')
        self.timeframe = "Monthly"
        data = self.downloader.data['Close'].copy()
        data.index = pd.to_datetime(data.index)
        data = data.resample('M').last()

        #print(data)

        self.marketCycles = self.hta.MarketCycle(data, data, data, 
                                            donchianPeriod=settings['donchian_period'], donchianSmoothing=3, 
                                            rsiPeriod=settings['rsi_period'], rsiSmoothing=3, 
                                            srsiPeriod=settings['srsi_period'], srsiSmoothing=3, srsiK=5, srsiD=5, 
                                            rsiWeight=settings['rsi_weight'], srsiWeight=settings['srsi_weight'], dcoWeight=settings['donchian_weight']
                                            )

        curr = int(settings["curr"])
        prev = curr-1

        self.DCO, DCOs = self.hta.DCO(data, donchianPeriod=20, smaPeriod=3)

        # Get the daily data
        oData = self.downloader.data['Close'].copy().T
        dailyData = oData[oData.index.isin(self.marketCycles.iloc[curr].index)].T

        # Monthly df
        self.processed = pd.DataFrame(index=self.marketCycles.iloc[curr].index, columns=["Symbol", "DCO", "MarketCycle", "MarketCycle_prev", "1M-change", "1D-change", "5D-change", "20D-change", "close", "Exchange", "Datapoints"])
        self.processed["Symbol"] = self.marketCycles.iloc[curr].index
        self.processed["MarketCycle"] = self.marketCycles.iloc[curr]
        self.processed["MarketCycle_prev"] = self.marketCycles.iloc[prev]
        self.processed["DCO"] = self.DCO.iloc[curr]
        self.processed["close"] = data.iloc[curr]
        self.processed["1M-change"] = (data.iloc[curr]-data.iloc[prev])/data.iloc[prev]*100
        self.processed["1D-change"] = (dailyData.iloc[curr]-dailyData.iloc[prev])/dailyData.iloc[prev]*100
        self.processed["5D-change"] = (dailyData.iloc[curr]-dailyData.iloc[prev-5])/dailyData.iloc[prev-5]*100
        self.processed["20D-change"] = (dailyData.iloc[curr]-dailyData.iloc[prev-20])/dailyData.iloc[prev-20]*100
        self.processed["Exchange"] = self.downloader.stocklist[self.downloader.stocklist['Symbol'].isin(self.marketCycles.iloc[curr].index)].set_index('Symbol')["Exchange"]
        self.processed["Datapoints"] = dailyData.count()
        self.processed = self.processed.dropna()

        self.date = self.marketCycles.iloc[curr].name.strftime('%Y-%m-%d %H:%M:%S')

        return self.processed
    
    # Filter the data
    def filter(self, settings=None):
        df = self.processed.copy()
        self.buySignals = df[(df['MarketCycle'] > settings['oversold']) & (df['MarketCycle_prev'] <= settings['oversold']) & (df['Datapoints'] >= settings['minDatapoints'])]
        self.sellSignals = df[(df['MarketCycle'] < settings['overbought']) & (df['MarketCycle_prev'] >= settings['overbought']) & (df['Datapoints'] >= settings['minDatapoints'])]
        self.buySignalsInTrend = df[(df['MarketCycle'] > settings['oversold']) & (df['MarketCycle_prev'] <= settings['oversold']) & (df['DCO'] > 50) & (df['Datapoints'] >= settings['minDatapoints'])]
        self.sellSignalsInTrend = df[(df['MarketCycle'] < settings['overbought']) & (df['MarketCycle_prev'] >= settings['overbought']) & (df['DCO'] < 50) & (df['Datapoints'] >= settings['minDatapoints'])]
        self.buySignalsCounterTrend = df[(df['MarketCycle'] > settings['oversold']) & (df['MarketCycle_prev'] <= settings['oversold']) & (df['DCO'] < 50) & (df['Datapoints'] >= settings['minDatapoints'])]
        self.sellSignalsCounterTrend = df[(df['MarketCycle'] < settings['overbought']) & (df['MarketCycle_prev'] >= settings['overbought']) & (df['DCO'] > 50) & (df['Datapoints'] >= settings['minDatapoints'])]
        self.filtered = True

    # Main call
    def get_buySignals(self, options=None):
        if self.filtered is None:
            return None
        return self.buySignals
    
    def get_sellSignals(self, options=None):
        if self.filtered is None:
            return None
        return self.sellSignals
    
    def get_buySignalsInTrend(self, options=None):
        if self.filtered is None:
            return None
        return self.buySignalsInTrend
    
    def get_sellSignalsInTrend(self, options=None):
        if self.filtered is None:
            return None
        return self.sellSignalsInTrend
    
    def get_buySignalsCounterTrend(self, options=None):
        if self.filtered is None:
            return None
        return self.buySignalsCounterTrend
    
    def get_sellSignalsCounterTrend(self, options=None):
        if self.filtered is None:
            return None
        return self.sellSignalsCounterTrend

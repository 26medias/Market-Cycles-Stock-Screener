import yfinance as yf

from os import path
import pandas as pd
from os import path
import math
import datetime
import hashlib

pd.set_option('display.max_columns', 1000)  
pd.set_option('display.max_rows', 1000)  
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)




class Downloader:
  def __init__(self, figsize=(30,10)):
    self.figsize  = figsize
    self.getStocklist()

  def getStocklist(self):
    self.stocklist = pd.read_csv('us-stocks.csv')
    self.stocklist = self.stocklist.loc[self.stocklist['Symbol'].apply(lambda x: isinstance(x, str))]
    self.symbols   = list(self.stocklist[['Symbol']].values.flatten())
    self.sectors   = self.stocklist['Sector'].unique()
  
  def stats(self):
    return self.stocklist.groupby('Sector').aggregate(['count'])
  
  def download(self, sector=None, symbols=None, period='1y'):
    print("Download: ", sector, symbols)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H")
    #now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if sector is not None:
      self.sector = sector
      rows      = self.stocklist[self.stocklist['Sector']==sector]
      symbols   = list(rows[['Symbol']].values.flatten())
      filename  = sector+'.pkl'
      self.symbols = self.getSymbolsBySector(self.sector)
    else:
      if symbols is not None:
        self.symbols = symbols
        #filename  = 'temp.pkl'#'data_'+period+'_'+(hashlib.sha224((''.join(self.symbols)).encode('utf-8')).hexdigest())+".pkl"
        filename  = 'data_'+now_str+'_'+(hashlib.sha224((''.join(self.symbols)).encode('utf-8')).hexdigest())+".pkl"
      else:
        filename  = 'data_'+now_str+'_'+(hashlib.sha224(('all').encode('utf-8')).hexdigest())+".pkl"
    
    if path.exists(filename):
      print("Using cached data")
      self.data = pd.read_pickle(filename)
    else:
      print("Downloading the historical prices")
      self.data = yf.download(self.symbols, period=period, threads=True)
      self.data.to_pickle(filename)
    #self.data = self.data.dropna()
    self.data = self.data[~self.data.index.duplicated(keep='last')]
    self.build()

    return self.data
  
  def getSymbolsBySector(self, sector):
    sectorRows    = self.stocklist[self.stocklist['Sector']==sector]
    return list(sectorRows[['Symbol']].values.flatten())
  
  def getSymbolData(self, symbol):
    cols = ['Open','High','Low','Close','Volume']
    df = pd.DataFrame(columns=cols, index=self.data.index)
    try:
      for col in cols:
        df[col] = self.data[col][symbol]
      df = df.dropna()
    except:
      print("Failed:", symbol)
    return df
  
  # We don't use this, but keeping because useful maybe
  def build(self):
    self.prices = self.data.loc[:,('Adj Close', slice(None))]
    if math.isnan(self.prices.iloc[0].max()):
      self.data = self.data.iloc[1:]
      self.prices = self.data.loc[:,('Adj Close', slice(None))]
    self.prices.columns = self.prices.columns.droplevel(0)
    self.changes  = (self.prices-self.prices.shift())/self.prices.shift()
    self.returns  = (self.prices[:]-self.prices[:].loc[list(self.prices.index)[0]])/self.prices[:].loc[list(self.prices.index)[0]]
    self.sector_mean = self.returns[self.symbols].T.describe().T[['mean']]
    return self.stocklist.groupby('Sector').aggregate(['count'])

# downloader = Downloader()
# downloader.download(period='1y')

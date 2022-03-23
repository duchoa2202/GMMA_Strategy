import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr

# override yahoo library change
yf.pdr_override()

stock = input("Enter a stock ticker symbol: ")
print(stock)

startyear = 2019
startmonth = 1
startday = 1

start = dt.datetime(startyear, startmonth, startday)
now = dt.datetime.now()
# pull dataframe from yahoo
df = pdr.get_data_yahoo(stock,start,now)

ma = 50
smaString="Sma_"+str(ma)

# add sma_50 colume to dataframe
df[smaString]=df.iloc[:,4].rolling(window=ma).mean()


# cut out the first 50 days without any value
df=df.iloc[ma:]

numH = 0
numL = 0
# checking closing value above or below moving average
for i in df.index:
    if(df["Adj Close"][i] > df[smaString][i]):
        print("The Close is higher")
        numH+=1
    else:
        print("The Close is lower")
        numL+=1

print("Number of closing higher: ", str(numH))
print("Number of closing lower: ", str(numL))
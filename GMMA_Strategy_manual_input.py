import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr

# override yahoo library change
yf.pdr_override()

startyear = 2019
startmonth = 1
startday = 1

stock = input("Enter the stock symbol (enter 'quit' to stop): ") #Query user for stock ticker

while stock != "quit": #Runs this loop until user enters 'quit' (can do many stocks in a row)

    start = dt.datetime(startyear, startmonth, startday)
    now = dt.datetime.now()
    # pull dataframe from yahoo
    df = pdr.get_data_yahoo(stock, start, now)

    emaUsed = [3, 5, 8, 10, 12, 15, 30, 35, 40, 45, 50, 60]

    for x in emaUsed:
        ema = x
        df["EMA_"+str(ema)] = round(df.iloc[:,
                                            4].ewm(span=ema, adjust=False).mean(), 2)

    print(df.tail())
    print()

    pos = 0
    num = 0
    initial_capital = 250
    num_share = 0
    percentchange = []

    for i in df.index:
        cmin = min(df["EMA_3"][i], df["EMA_5"][i], df["EMA_8"][i],
                df["EMA_10"][i], df["EMA_12"][i], df["EMA_15"][i])
        cmax = min(df["EMA_30"][i], df["EMA_35"][i], df["EMA_40"][i],
                df["EMA_45"][i], df["EMA_50"][i], df["EMA_60"][i])

        close = df["Adj Close"][i]

        if (cmin > cmax):
            if (pos == 0):
                bp = round(close,2) #buy point at close
                pos = 1
                num_share = round(initial_capital/bp,2)
                print("Buying at "+str(bp) + " on "+ str(i) + " get number of share "+str(num_share))
        elif(cmin < cmax):
            if (pos == 1):
                pos = 0
                sp = round(close,2) #sell point at close
                pc = round((sp/bp-1)*100,2) #calculate percentage change after closing the trade
                percentchange.append(pc)
                initial_capital = round(initial_capital + initial_capital*pc/100,2)
                print("selling at "+str(sp) + " on "+str(i) + " with " + str(pc) + "%" + ". Capital value: " + str(initial_capital)+"€")

        # exit all open position
        if (num == df["Adj Close"].count()-1 and pos == 1):
            pos = 0
            sp = round(close,2) #sell point at close
            pc = round((sp/bp-1)*100,2)
            percentchange.append(pc)
            initial_capital = round(initial_capital + initial_capital*pc/100,2)
            print("open position. if selling now at "+str(sp) + " on "+str(i) + " profit will be " + str(pc) + "%"". Capital value NOW: " + str(initial_capital)+"€")

        num+=1

    gains = 0
    ng = 0 #number of gains
    losses = 0
    nl = 0 #number of losses
    totalR = 1 # total return

    for i in percentchange:
        if (i>0):
            gains+=i
            ng+=1
        else:
            losses+=i
            nl+=1
        totalR=totalR*((i/100)+1)

    totalR = round((totalR-1)*100,2)

    if (ng>0):
        avgGain = gains/ng
        maxR=str(round(max(percentchange),2))
    else:
        avgGain=0
        maxR="undefined"

    if (nl>0):
        avgLoss = losses/nl
        maxL=str(round(min(percentchange),2))
        ratio=str(round(-avgGain/avgLoss,2))
    else:
        avgLoss=0
        maxL="undefined"
        ratio="inf"

    if (ng>0 or nl>0):
        battingAvg=ng/(ng+nl)
    else:
        battingAvg=0

    print()
    print("Results for "+ stock +" going back to "+str(df.index[0])+", Sample size: "+str(ng+nl)+" trades")
    print("EMAs used: "+str(emaUsed))
    print("Batting Avg: "+ str(round(battingAvg,2)))
    print("Gain/loss ratio: "+ ratio)
    print("Average Gain: "+ str(round(avgGain,2))+"%")
    print("Average Loss: "+ str(round(avgLoss,2))+"%")
    print("Max Return: "+ maxR+"%")
    print("Max Loss: "+ maxL+"%")
    print("Total return over "+str(ng+nl)+ " trades: "+ str(totalR)+"%" )
    #print("Example return Simulating "+str(n)+ " trades: "+ str(nReturn)+"%" )
    print()

    stock = input("Enter the stock symbol (enter 'quit' to stop): ") #query user for next stock

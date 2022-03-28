import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
from pandas import ExcelWriter
import smtplib
import imghdr
from email.message import EmailMessage
import time

# override yahoo library change
yf.pdr_override()

EMAIL_ADDRESS = 'hoanguyen.asm@gmail.com'
EMAIL_PASSWORD = 'lmujshzzwjmhbrfa'

msg = EmailMessage()

startyear = 2022
startmonth = 3
startday = 20

start = dt.datetime(startyear, startmonth, startday)
now = dt.datetime.now()

root = Tk()
filePath=r"D:\10_Projects\03_Python_Finance\Full_Watchlist.xlsx"
stocklist = pd.read_excel(filePath)

buy_alerted = False
sell_alerted = False
buy_date=dt.datetime(2022, 3, 20)
sell_date=dt.datetime(2022, 3, 20)
buy_list=[]
sell_list=[]
record_sell_date = 0
record_buy_date = 0

def clear_buy_sell_list():
    if now.day > record_buy_date:
        buy_list.clear()
    if now.day > record_sell_date:
        sell_list.clear()

while 1:
    for i in stocklist.index: #Runs this loop through stock list file
        stock = str(stocklist["Symbol"][i])
        buy_alerted=False
        sell_alerted = False

        try:
            # pull dataframe from yahoo
            df = pdr.get_data_yahoo(stock, start, now)

            emaUsed = [3, 5, 8, 10, 12, 15, 30, 35, 40, 45, 50, 60]

            for x in emaUsed:
                ema = x
                df["EMA_"+str(ema)] = round(df.iloc[:,
                                                    4].ewm(span=ema, adjust=False).mean(), 2)

            print(stock)

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
                        buy_date = i
                        print("Buying at "+str(bp) + " on "+ str(i) + " get number of share "+str(num_share))
                elif(cmin < cmax):
                    if (pos == 1):
                        pos = 0
                        sp = round(close,2) #sell point at close
                        pc = round((sp/bp-1)*100,2) #calculate percentage change after closing the trade
                        percentchange.append(pc)
                        initial_capital = round(initial_capital + initial_capital*pc/100,2)
                        sell_date = i
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

        except Exception:
            print("No data on"+stock)

        if(buy_date.day==now.day and buy_date.month==now.month and buy_date.year==now.year and buy_alerted==False):

            msg['Subject'] = 'Buy alert on ' + stock+'!'
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = 'duchoa2202@gmail.com'
            
            buy_alerted=True

            message=stock +" Buy alert "+ str(stock) +\
            "\nCurrent Price: "+ str(bp)

            print(message)
            msg.set_content(message)

            if stock in buy_list:
                print("do not send email alert email again")
                print()
            else:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    smtp.send_message(msg)
                    buy_list.append(stock)
                    record_buy_date = buy_date.day
                    print("completed")
                    print()
            del msg['Subject']
            del msg['From']
            del msg['To']

        elif (sell_date.day == now.day and sell_date.month==now.month and sell_date.year==now.year and sell_alerted==False):
            msg['Subject'] = 'Sell alert on ' + stock+'!'
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = 'duchoa2202@gmail.com'
            
            sell_alerted=True

            message=stock +" Sell alert "+ str(stock) +\
            "\nCurrent Price: "+ str(bp)

            print(message)
            msg.set_content(message)

            if stock in sell_list:
                print("do not send sell alert email again")
                print()
            else:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    smtp.send_message(msg)
                    sell_list.append(stock)
                    record_sell_date = sell_date.day
                    print("completed")
                    print()
            del msg['Subject']
            del msg['From']
            del msg['To']

        else:
            print("No new alerts")
            print()

    time.sleep(60)
    clear_buy_sell_list()
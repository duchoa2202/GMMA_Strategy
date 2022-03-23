import os
import smtplib
import imghdr
from email.message import EmailMessage

import yfinance as yf
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import time

EMAIL_ADDRESS = 'hoanguyen.asm@gmail.com'
EMAIL_PASSWORD = 'lmujshzzwjmhbrfa'

msg = EmailMessage()

yf.pdr_override() # <== that's all it takes :-)
start =dt.datetime(2019,1,1)
now = dt.datetime.now()

stock="AAPL"
TargetPrice=111

msg['Subject'] = 'Alert on '+ stock+'!'
msg['From'] = EMAIL_ADDRESS
msg['To'] = 'duchoa2202@gmail.com'

alerted=False

while 1:

	df = pdr.get_data_yahoo(stock, start, now)
	currentClose=df["Adj Close"][-1]

	condition=currentClose>TargetPrice

	if(condition and alerted==False):

		alerted=True

		message=stock +" Has activated the alert price of "+ str(TargetPrice) +\
		 "\nCurrent Price: "+ str(currentClose)

		print(message)
		msg.set_content(message)

		# files=[r"C:\Users\hoang\Downloads\Stock list 3-24 share.xlsx"]

		# for file in files:
		# 	with open(file,"rb") as f:
		# 		file_data=f.read()
		# 		file_name="FundamentalList.xlsx"

		# 		msg.add_attachment(file_data, maintype="application",
		# 			subtype='ocetet-stream', filename=file_name)


		with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
		    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
		    smtp.send_message(msg)

		    print("completed")
	else:
		print("No new alerts")
	time.sleep(60)
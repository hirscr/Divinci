#!/usr/bin/env python3

import time
import locale
import pandas as pd
import numpy as np
import copy
import csv
import requests
import os.path
import json
import subprocess
import pandas as pd
import datetime
import pytz
from twilio.rest import Client

# Version 0.2
# Robert Hirsch
# 


# ================================
# =======functions================
# ================================


# ================================
# CMD. performs any divi-cli command
# input: command and the arguments for the command
# output: the divid response to the command
# ================================
def cmd(command, **kargs):
# some args may be address, amounts, intervals, etc
    core = "/home/vermion/divi_ubuntu/divi-cli"
    com=[core,command]
    out='boo'
    if len(kargs) != 0:
        if command == "walletpassphrase":
            com = [core,command ,kargs.get("pw"),kargs.get("time"), kargs.get("staking")]
        if command == "listtransactions":
            num=int(kargs.get("num"))
            if num > gmaxtxs :
                num = gmaxtxs
            com = [core,command ,kargs.get("account"),str(num), kargs.get("start")]
        if command == "getblock" :
            com = [core,command ,kargs.get("hash")]
            
    result = subprocess.run(com,stdout=subprocess.PIPE)
    out = (result.stdout.strip()).decode("utf-8")
    return out

# ================================
# MakeDFofTXs : make a dataframe of a list of transactions that came from listtransactions command
# input: a list of transactions 
# output: a data frame of of those transactions with time differences, adn date-times added
# ================================
def MakeDFofTXs(txs):
    time=[]
    confirms=[]
    amount=[]
    blocknum=[]
    category=[]
    timediffs=[0]
    for i in txs:    #for each tx
        if i["confirmations"] != -1 :    #sometimes confirmartions gives a -1 and no blockhash...why? dunno
           time.append(i["blocktime"])
           confirms.append(i["confirmations"])
           amount.append(i["amount"])
           blocknum.append(json.loads(cmd("getblock",**{"hash" : i["blockhash"]} ))["height"])
           category.append(i["category"])
        
    df= pd.DataFrame({'time' : time,'confirms':confirms,'amount':amount, 'category' : category}, index=blocknum)
    df['dTime'] = (df['time'].shift(1)-df['time'])*-1
    df['dTime'].fillna(value=0)
    df['datetime'] = df.apply(lambda row : findDateTime(row['time']), axis = 1)
    return df


# ================================
# Function : printTXs
# Description : prints dataframe and current balance
# input:  the dataframe to be printed
# output: the unmodified dataframe
# ================================
def printTXs(df):
    print(df)
    print("balance: ", getCurrentBalance())
    return df
    
# ================================
# Function : getCurrentBalance
# Description : gets the full balance fo the wallet including the transactions that are not yet confirmed
# input: none
# output: wallet balance
# ================================    
def getCurrentBalance() :
    walletinfo=json.loads(cmd("getwalletinfo"))
    return (walletinfo['balance'] + walletinfo['immature_balance'] + walletinfo['unconfirmed_balance'])
    
    
# ================================
# Function : findDateTime
# Description : finds the date-time of a UTC time with localization
# input: the UTC time
# output: a string with the date-time
# ================================
def findDateTime(UTCtime) :
    try:
        d = datetime.datetime.utcfromtimestamp(UTCtime)
        d = pytz.UTC.localize(d)
        tz = pytz.timezone(gtimezone) 
        d=d.astimezone(tz)
        d=d.strftime("%m/%d/%Y %H:%M:%S")
    except:
        d= 'failed date'
    return d

# ================================
# Function : keepRecentTXs
# Description : remove all txs that are not withing a certain amount of seconds
# input: the dataframe of transactions and the amount of time to keep
# output: a trimmed dataframe
# ================================
def getRecentTXs(df, seconds) :
    now=datetime.datetime.utcnow()
    return df.loc[df['time'] >= int(now.timestamp())-seconds]

# ================================
# Function : getStakeTXs
# Description : reduce a data frame to only include staking transactions
# input: a dataframe of transactions
# output: a reduced data frame
# ================================
def getStakeTXs(df) :
    return df.loc[df['category'] == 'stake_reward']
    
# ================================
# Function : getLotteryTXs
# Description : reduce a data frame to only include lottery transactions
# input: a dataframe of transactions
# output: a reduced data frame
# ================================
def getLotteryTXs(df) :
    return df.loc[df['category'] == 'lottery']

# ================================
# Function : getSentTXs
# Description : reduce a data frame to only include sent transactions
# input: a dataframe of transactions
# output: a reduced data frame
# ================================    
def getSendTXs(df) :
    return df.loc[df['category'] == 'send']

# ================================
# Function : getReceiveTXs
# Description : reduce a data frame to only include received transactions
# input: a dataframe of transactions
# output: a reduced data frame
# ================================
def getReceiveTXs(df) :
    return df.loc[df['category'] == 'receive']

# ================================
# Function : getLotteryTXs
# Description : reduce a data frame to only include lottery transactions
# input: a dataframe of transactions
# output: a reduced data frame
# ================================
def getMasternodeTXs(df) :
    return df.loc[df['category'] == 'masternode_reward']
    
# ================================
# Function : writeDailyData
# Description : write a row of data to the daily log
# input: a row of data as a list
# output: whether or not the write process failed
# ================================    
def WriteDailyData(row) :
    status=True
    try :
        with open(ghomedir+gdatafilename, 'a') as Datafile:
            RowWriter= csv.writer(Datafile, delimiter=',')
            RowWriter.writerow(row)
    except :
        status = False
    return status

# ================================
# Function : GetPrice
# Description :  gets the price of a coin
# input: the coin of interest
# output: the price of the coin
# ================================
def GetPrice(coin) :
    addr='https://api.coingecko.com/api/v3/simple/price?ids=' + coin + '&vs_currencies=usd'
    resp = requests.get(addr)
    try :
        resp = resp.json()
    except: 
        resp = resp.text
    return resp[coin]['usd']



# ================================
# ======= Main Code ==============
# ================================    

# first get configuration parameters
print("opening file...")
with open('/home/vermion/divi_ubuntu/divinci.conf','r') as cfgfile:
    config = json.load(cfgfile)

gmaxtxs = config[0]['maxtxs']
gtimezone = config[0]['timezone']
gdatafilename = config[0]['datafile']
ghomedir = config[0]['homedir']
ginterval = config[0]['interval']
gsid= config[0]['sid']
gtoken = config[0]['token']
gfromphone = config[0]['fromphone']
gtophone = config[0]['tophone']

firsttime = False
df=[]

# need to start the datafile if it doesnt exist
logfilefailed=False
if os.path.isfile(ghomedir+gdatafilename) != True:
    try:
        with open(gdatafilename, 'w+') as Datafile:
            writer = csv.writer(Datafile)
            writer.writerow(['Date-time','Balance','Lottery','Received','Number of Stakes','Daily Income','Daily RoR','Extended RoR','BTCPrice','DiviPrice','$ income'])
            firsttime=True
    except:
        print('failed to open data file' + gdatafilename)
        logfilefailed=True
        


walletfailed=False
#now let's start eh process of gathering row data. Lets first get more transactions than anyone could ever get in a day
try:
    txs=json.loads(cmd("listtransactions", **{"account" : "*","num" : "300" ,"start" : "0"}))
except:
    walletfailed=True

# now lets put that into a nice dataframe
if (walletfailed==False):
    print("making dataframe...")
    df=MakeDFofTXs(txs)
    # now lets trim the data frame to however many seconds we want to compile data over
    df=getRecentTXs(df,ginterval)

stakes=0
d=0
balance=0
oldbalance=0
income=0
lotterywins=0

print("compiling data...")

if len(df)!=0:    #make sure some stakes have actually come in
    #get current datetime
    dfdatetime = df.iloc[-1]['datetime']    

    # lets get a balance
    balance=getCurrentBalance()

    # lets get the lotteries
    lotterywins=getLotteryTXs(df)["amount"].sum()

    #lets get how much was sent to us
    received=getReceiveTXs(df)["amount"].sum()

    # now lets gather the stakes using a new dataframe
    stakes=len(getStakeTXs(df))

    # Get current income
    #first load in old csv file if this is not the first time
    oldbalance=0
    if firsttime != True :
        previousdata= pd.read_csv(ghomedir+gdatafilename)
        oldbalance=previousdata.iloc[-1]['Balance']
        income=balance-oldbalance
    else:
        income=balance

        # find the rate fo return fo the day
    ror=0.0
    if oldbalance != 0 :
        ror = (income-lotterywins)/oldbalance
    else:
        ror = 0

    #get annualized RoR
    secondsinyear = 365*24*3600
    multiple = secondsinyear/ginterval
    aror=ror*multiple

    d=GetPrice('divi')

    #ok, lets write this shit
    row=[dfdatetime,balance,lotterywins,received,stakes,income,ror,aror, GetPrice('bitcoin'),d,d*income]
    WriteDailyData(row)

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
client = Client(gsid, gtoken)

#assemble Message

if walletfailed==False :
    stakemsg="Daily income: " + str(int(stakes)) + " stakes and about $" + str(int(round(d*income)))

    if lotterywins!=0 :
        numofwins=int(lotterywins/25200)
        if numofwins>=10:
            stakemsg=stakemsg + " You won the Big Lottery!"
            numofwins -= 10
            
        stakemsg=stakemsg +" You also won " + str(numofwins) + " small lotteries"
else:
        stakemsg="WARNING: Wallet Stopped Functioning"

if logfilefailed == True:
    stakemsg=stakemsg + "Log file failed"

message = client.messages \
                .create(
                     body=stakemsg,
                     from_=gfromphone,
                     to=gtophone
                 )

print(message.sid)

# FIX
# if no TXS it blows up. if Len(df)=0 it blows up.  datetime = df.iloc[-1]['datetime']    so check that there are txs

# Run this script
#exec(open('dv.py').read())



    

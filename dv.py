#!/usr/bin/env python3

import time
import locale
import pandas as pd
import numpy as np
import copy
import csv
import sys
import requests
import os.path
import json
import subprocess
import datetime
import pytz
import commentjson
from pprint import pprint
from twilio.rest import Client


# Version 0.1
# Robert Hirsch
# hirscr@me.com


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
    core = ghomedir +"divi-cli"
    com=[core,command]
    out='boo'
    if len(kargs) != 0:
        if command == "walletpassphrase":
            if kargs.get("staking") != "":
                com = [core,command ,kargs.get("pw"),kargs.get("time"), kargs.get("staking")]
            else:
                com = [core,command ,kargs.get("pw"),kargs.get("time")]
			
        if command == "listtransactions":
            num=int(kargs.get("num"))
            if num > gmaxtxs :
                num = gmaxtxs
            com = [core,command ,kargs.get("account"),str(num), kargs.get("start")]
			
        if command == "getblock" :
            com = [core,command ,kargs.get("hash")]
			
        if command == "getblockhash":
            com = [core,command ,kargs.get("blocknum")]
			
        if command == "sendtoaddress" :
            com= [core,command ,kargs.get("address"),kargs.get("amount")]
        
        if command == "gettransaction" :
            com= [core,command ,kargs.get("txid")]
			
        #print(com)
    try:        
        result = subprocess.run(com,stdout=subprocess.PIPE)
    except:
        s=" "
        print("subprocess failed: com= " + s.join(com))
        out = "fail"
        return out
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
    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')
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

def GetStakingStatus():
    try:
        status=json.loads(cmd("getstakingstatus"))
    except:
        return False
    
    return status["staking status"]
    

# ================================
# ======= Recordday ==============
# ================================    
def recordday():

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
    
        #get how much was sent out of the wallet
        sent=getSendTXs(df)["amount"].sum()

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
        row=[dfdatetime,balance,lotterywins,received,stakes,income,ror,aror, GetPrice('bitcoin'),d,d*stakes*456]
        WriteDailyData(row)
        print("datetime= {} balance = {}, Stakes = {}".format(dfdatetime,balance,stakes))



    #assemble Message

    if walletfailed==False :
        #calculate staking income
        stakemsg="Hello from "+gwalletname+"! Daily income: " + str(int(stakes)) + " stakes and about $" + str(int(round(d*stakes*456)))
        #calculate if lottery was won
        if lotterywins!=0 :
            numofwins=int(lotterywins/25200)
            if numofwins>=10:
                stakemsg=stakemsg + " You won the Big Lottery!"
                numofwins -= 10
            stakemsg=stakemsg +" You also won " + str(numofwins) + " small lotteries"
        
        if received!=0:
            stakemsg=stakemsg +" You also received " + str(received) + " divi"
        
        if sent!=0:
            stakemsg=stakemsg +" You also sent out " + str(sent) + " divi"
    
        if GetStakingStatus()==False:
            stakemsg=stakemsg +" Wallet is not staking!"
    else:
            stakemsg="WARNING: Wallet Stopped Functioning"
            print("Wallet Stopped Functioninge")

    if logfilefailed == True:
        stakemsg=stakemsg + "Log file failed"
    
    if len(stakemsg) !=0:
        sendSMS(stakemsg)
    # FIX
    # if no TXS it blows up. if Len(df)=0 it blows up.  datetime = df.iloc[-1]['datetime']    so check that there are txs
    return
    
    
def sendSMS(msg):
    client = Client(gsid, gtoken)
    
    message = client.messages.create(
                         body=msg,
                         from_=gfromphone,
                         to=gtophone
                     )

    print("twilio message-id"+message.sid)
    return


def getDiviScanInfo(command):
    addr='https://api.diviproject.org/v1/' + command + '/'
    resp = requests.get(addr)
    try :
        resp = resp.json()
    except: 
        resp = resp.text
    return resp


def checkFork():
    walletblock=cmd("getblockcount")
    wallethash= cmd("getblockhash",**{"blocknum" : walletblock})
    chaininfo=(getDiviScanInfo("blocks"))
    chainblock=str(chaininfo[0]['height'])
    print("wallet block : " + walletblock)
    print("Chain block : " + chainblock)
    if chainblock!=walletblock:
        msg="walletblock: {}  chainblock: {} Wallet may be forked!".format(walletblock,chainblock)
        return msg
    chainhash=chaininfo[0]['hash']
    print("wallet hash : " + wallethash)
    print("chain hash : " + chainhash)
    if chainhash!=wallethash:
        msg="Hashes don't Match. Wallet may be forked!"
        return msg
    msg="OK"
    return msg

def getFee(txid):
    resp = cmd("gettransaction", **{"txid": txid})
    try:
        txs = json.loads(resp)
    except ValueError as e:
            return(0)
    else:
        return (-1*txs["fee"])
        

def sendFunds(amount, address):
    #assumes address and amount have been checked, as well as balance remianing
    try:
        resp = cmd("sendtoaddress", **{"address": address, "amount": str(amount)})
    except:
        return("FAIL","Send Failed")
    try:
        txs = json.loads(resp)
    except ValueError as e:
        if resp[0:4]=="error":
            return("FAIL",resp)
        return ("PASS",resp)
    else:
        return("FAIL",txs)


def multiSend (amount, address, lot):
    #assumes address and amount have been checked, as well as balance remaining
    #adds up fees, then sends one final send assuming 100 divi
    remaining=amount
    feesum=0
    
    while remaining > lot+100:
        complete = int((1 - remaining/amount)*100)
        print(str(complete)+'% complete', end='\r', flush=True)
        success,resp = sendFunds(lot,address)
    
        if success == "FAIL":
            return(success, resp)
        else:
            fee=getFee(resp)
            remaining=remaining-lot-fee    #fees are negative
            feesum=feesum+fee
    print("                                ")
    retsig = {"fee" : feesum, "remaining" : remaining}
    return "PASS",retsig
    
    
    
    
    
# =====================
# ==== MAIN ===========
# ======================
# use en_US.utf8 when on linux
# locale.setlocale(locale.LC_ALL, 'en_US.utf8')
def main(argv):
    global gforkcount
    global config
    # lets first figure out what is supposed to be happening
    # give instructions if the user didn't give an arg when calling script
    if len(sys.argv) == 1:
        print("********** Divinci CLI Helper *****************")
        print("<recordday>       to record income results from the last 24 hours")
        print("<checkfork>       to check if the wallet is on the main blockchain")
        print("<txs> <days>      to see transactions from last <days>")
        print("<staked> <days>   check for staking rewards over last <days>")
        print("<lottery>         check to see if you won recent lottery")
        print("<sent> <days>     check for any divi sent over last <days>")
        print("<received> <days> check for any divi received over last <days>")
        print("<balance>         print full current balances")
        print("<price> <coin>    print the current price of divi or btc ")
        print("<info>            show some stats about the wallet")
        print("<tail> <num>      to show the last <num> transactions")
        print("<smstest>         sends a test message using your twilio credentials")
        print("<multisend> <amount> <address> <lot> send <amount> in <lot> batches")
        print("<send> <amount> <address> 	useful for a cron task")
        print("<unlock> <seconds>			unlocks the wallet")
        print("<lock>            locks the wallet for staking")
        exit()

    # print('args : ' + str(sys.argv))
    
    command = sys.argv[1]
    args=sys.argv[2:]
    
    
    if command not in ['balance','send','multisend','lottery','recordday',
							'info','checkfork','smstest','lock']:
        if len(args) != 1:
            print("incorrect number of arguments for command")
            if command == 'price':
                print("the command requires <coin>")
            elif command == 'tail':
                print("the command requires <num>")
            elif command == 'unlock':
                print("the command requires <seconds>")
            else:
                print("the command requires <days>")
            exit()
            
    if command not in ['price','unlock']:
        if command=='lottery':
            timespan=7
        else:
            timespan=int(args[0])
        #estimate possible number of txs
        if timespan < 1:
            print("please enter a positive number of days")
            exit()
        txspan=int(timespan*60*24*0.1)  #assumes that no one gets more than 10% of all stakes
        if txspan>gmaxtxs:
            txspan=gmaxtxs
        
        if command=='tail':
            txspan=timespan   #in this case timespan is number of txs the user wants to see
            
        try:
            resp=cmd("listtransactions", **{"account" : "*","num" : str(txspan) ,"start" : "0"})
            txs=json.loads(resp)
        except:
            print('Wallet failed')
            pprint(resp)
            exit()

        
        df=MakeDFofTXs(txs)
        # now lets trim the data frame to however many seconds we want to compile data over
        if command != 'tail':
            df=getRecentTXs(df,timespan*60*60*24)
    
    if command =='recordday':
        recordday()
        exit()
        
    if command in ['txs','tail']:
        printTXs(df)
        exit()

    if command == 'staked':
        print("over the last "+args[0]+ " days, you received " +str(len(getStakeTXs(df))) + " Stakes")
        print("resulting in an additional " + str(getStakeTXs(df)["amount"].sum()) + " Divi")
        exit()
    
    if command == 'sent':
        print("over the last "+args[0]+ " you sent" +str(getSendTXs(df)["amount"].sum()) + " Divi")
        exit()
    
    if command == 'received':
        print("over the last "+args[0]+ " you received " +str(getReceiveTXs(df)["amount"].sum()) + " Divi")
        exit()
    
    if command == 'lottery':
        lotterywins = getLotteryTXs(df)["amount"].sum()
        if lotterywins!=0 :
            numofwins=int(lotterywins/25200)
            if numofwins>=10:
                print(" You won the Big Lottery!")
                numofwins -= 10
            print("You also won " + str(numofwins) + " small lotteries")
        else: 
            print("Sorry, you didnt win any lotteries")
        exit()
      
    if command == 'balance': 
        print("your total wallet balance is: " + str(getCurrentBalance()) + " Divi")
         
    if command == 'price':
        if args[0] in ['divi', 'bitcoin','btc']:
            if args[0]=='btc':
                args[0]='bitcoin'
            print("The price of " +args[0]+ " is " +str(GetPrice(args[0])) + " USD")
        else:
            print("I dont do that coin")
        exit()
    
    if command == 'info': 
        print("Balance: " + str(getCurrentBalance()))
        print("Staking status:" + str(GetStakingStatus()))
        exit()
    
    if command == 'checkfork':
        message=checkFork()
        if message != "OK":
            gforkcount=gforkcount+1
            if gforkcount==5:           #make sure the blockcount or hash doesnt match 5 times
                sendSMS(message)
                print(message)
                gforkcount=0
        else:
            print("Wallet is on correct fork of Divi blockchain. Forkcounter = "+ str(gforkcount))
            gforkcount=0
        config['forkcount']=gforkcount
        #update the fork counter
        with open('divinci.conf','w') as cfgfile:
            json.dump(config,cfgfile,indent=4)
        cfgfile.close()
        exit()
    
    if command == 'smstest':
        sendSMS('Hola! from ' + gwalletname)

    if command in ['send','multisend']:
        if len(args) < 2:
            print("the send command requires <amount> and <address>")
            exit()
        try:
            amount = float(args[0])
        except:
            print("Amount must be a floating point number")
            exit()

        addr = args[1]

        if addr[0] != 'D' and len(addr) != 34:
            print("that is not a valid Divi address")
            exit()

        if amount > getCurrentBalance():
            print("You don't enough funds")
            exit()
        
        if command == 'send':
            # we already have checked that the amount is a float and the address is valid
    
            success, resp = sendFunds(amount,addr)
            
            if success=="FAIL":
                pprint(resp)
            else:
                print("TXID: " + resp)
            exit()
        else:
            if len(args) != 3:
                print("multisend need a lot size")
                exit()
            
            try:
                lot = float(args[2])
            except:
                print("Lot must be a floating point number")
                exit()
            
            if lot>amount/2 :
                print("Lot size must be smaller than half the amount being sent")
                exit()
            
            success, resp = multiSend(amount,addr,lot)
            if success=="FAIL":
                pprint(resp)
            else:
                fee= resp["fee"]
                remaining= resp["remaining"]
                print("Success!")
                print(" Remaining Divi from multisend: " + str(remaining))
                print(" total fees: " ,str(fee))
            exit()
			
    if command == 'unlock':  #unlock for <seconds> seconds, already checked for seconds arg
        seconds=args[0]
        try:
            resp = cmd("walletpassphrase", **{"pw": gacctpw, "time": str(seconds), "staking":""})
            #txs = json.loads(resp)
        except:
            print('wallet unlock failed')
            pprint(resp)
            exit()

    if command == 'lock':
        try:
            resp = cmd("walletpassphrase", **{"pw": gacctpw, "time": "0","staking":"true"})
            #txs = json.loads(resp)
        except:
            print('wallet unable to lock')
            pprint(resp)
            exit()


    #FUTURE COMMANDS
# perform commands
# divisince <"date">
# incomesince <"date">
# makehistogram
# valueof <howmanydivi>


# first get configuration parameters
with open('divinci.conf','r') as cfgfile:
    config = commentjson.load(cfgfile)
cfgfile.close()

gmaxtxs = config['maxtxs']
gtimezone = config['timezone']
gdatafilename = config['datafile']
ghomedir = config['homedir']
ginterval = config['interval']  
gsid= config['sid']
gtoken = config['token']
gfromphone = config['fromphone']
gtophone = config['tophone'] 
gforkcount = config['forkcount']
gacctpw = config['acctpw']
gwalletname = config['walletname']

if __name__ == "__main__":
    main(sys.argv[1:])
    
# Run this script in python
#exec(open('dv.py').read())
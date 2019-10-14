# Divinci
A companion app for the Divi CLI wallet.

## What does Divinci do?

Divinci is intended to run along side of your own personal Divi CLI wallet, with the intention of improving the way
transactions are viewed as well as being able to record daily staking income for the dreaded tax day.It also texts you
daily about your staking results for the day as well as whether or not you won a lottery.

## what is needed for Divi to function?

Here are the modules Divinci requires

`import time`  
`import locale`  
`import pandas as pd`  
`import numpy as np`  
`import copy`  
`import csv`  
`import sys`  
`import requests`  
`import os.path`  
`import json`  
`import subprocess`  
`import datetime`  
`import pytz`  
`from pprint import pprint`  
`from twilio.rest import Client`  

Divinci does NOT work on any CLI client before 1.0.4

## Using divinci

First you will have to set up the Config file to be applicable to you. Also in the DV file, I have not generalized the home directory. You will have to change that too. Change every instance of `"/home/vermion/divi_ubuntu/"` to apply to your directory where the divi wallet is. Put the companion app in the same directory.

Here are the commands for Divinci

`cmd(command, **kargs)`

There are three commands right now that CMD can perform
1. walletpassphrase
2. listtransactions
3. getblock

Also, CMD can perform any other wallet command that doesnt have any arguments like "getinfo" or "getbalance"

Obviously, each requires additional arguments. To use "walletpassphrase" to unlock the wallet you must also pass the passphrase, the amount of time you want the wallet unlocks and whether or not its for staking.

So an example would be:
`>>>cmd("walletpassphrase",**{"pw": "mypassphrase","time" : "600","staking" : "0"})`

 To use "listtransactions" you have to also give the account name (usually "*"), how many transactions you want to see, and 
 how many transactions back you wish to start from. So as an example:
 
 `>>>txs=cmd("listtransactions", **{"account" : "*","num" : "300" ,"start" : "0"})`
 
To use "getblock" you will need the hash of the block you are interested in. Frankly I have not used this for anything and the results are no different than using the command. You need to supply the hash for the block you are interested in which you can get from chainz or diviscan. An example would be:

`>>>cmd("getblock", **{"hash" : "puttheblockhashere"})`

Really, for the rest of this, only the listtransactions command matters.

## getting to the good stuff

Divinci currently has a few commands and you can execute any of them as a cron job or singualrly Here they are.  
all commands start with 
`python3 dv.py `

| **Command** | **Description                                   |
|---------|---------------------------------------------------------|
| recordday  | to record income results from the last 24 hours       |
| txs num  | to see transactions from last <num> days           |
| staked num  | check for staking rewards over last <num> days |
| amount | the amount of coins you want to trade (float)           |
| lottery  |    check to see if you won last lottery             | 
| sent num  |   check for any divi sent over last <num> days    |
| received num  |    check for any divi received over last <num> days      | 
| balance  |   print full current balance          | 
| price coin  |  right now only coins handled by coin gecko   | 
| info  |    show some stats about the wallet      | 
| tail num        |   to show the last <num> transactions in a nice table format       | 



## getting a financial started
I wanted to record daily income, running balance, and the daily income in $, so I set up a cron job to run dv.py every day at midnight. Thus I get a file with each row as follows:

##### 'Date-time','Balance','Lottery','Received','Number of Stakes','Daily Income','Daily RoR','Extended RoR','BTCPrice','DiviPrice','$ income'

In order to do so, you have to set up the divinci.conf file with the correct data for your set up. It will create the file on
its own as long as you have set up a file name. dv will add a row every time "recordday" is called.

## twilio
to get a text every day, you need ot set up a twilio account. Then put the sid and secret and phone numbers into the .conf file. Then you should be good to go. The free credits they give you has lasted me 4 months so far. 




 

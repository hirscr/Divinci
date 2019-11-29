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

###please note new config file required for latest divinci release

I use crontab for two things. First, I schedule a "recordday" once a day to add a staking income line to the financials file. The recordday job will send me a summary as an SMS (if you set up a twilio account). Then, every 5 minutes I schedule a "checkfork" to make sure my wallet has not gotten on to a forked blockchain. The checkfork job will send me a text if it has found that the wallet has been on a forked chain 5 consecutive times. Thus if your wallet gets forked, you will know in 30 minutes.

so my crontab file looks as follows:
```
0 0 * * * cd /home/user/divi_ubuntu/ && python3 dv.py recordday >> dvoutput.txt 2>&1
*/5 * * * * cd /home/user/divi_ubuntu/ && python3 dv.py checkfork >> forkcheck.txt 2>&1
```

If you want to test the twilio aspect of the scriopt, you can just send a test message to yourself, with the 'smstest' command.


## getting to the good stuff

Divinci currently has a few commands and you can execute any of them as a cron job or singualrly Here they are.  
all commands start with 
`python3 dv.py `

| **Command** | **Description                                   |
|---------|---------------------------------------------------------|
| recordday  | to record income results from the last 24 hours       |
| txs num  | to see transactions from last "num" days           |
| staked num  | check for staking rewards over last "num" days |
| amount | the amount of coins you want to trade (float)           |
| lottery  |    check to see if you won last lottery             | 
| sent num  |   check for any divi sent over last "num" days    |
| received num  |    check for any divi received over last "num" days      | 
| balance  |   print full current balance          | 
| price coin  |  right now only coins handled by coin gecko   | 
| info  |    show some stats about the wallet      | 
| tail num        |   to show the last "num" transactions in a nice table format       | 
| checkfork        |   checks to see if your wallet is on a forked chain       | 
| smstest        |   to test your twilio account with divinci       | 



## getting a financial started
I wanted to record daily income, running balance, and the daily income in $, so I set up a cron job to run dv.py every day at midnight. Thus I get a file with each row as follows:

##### 'Date-time','Balance','Lottery','Received','Number of Stakes','Daily Income','Daily RoR','Extended RoR','BTCPrice','DiviPrice','$ income'

In order to do so, you have to set up the divinci.conf file with the correct data for your set up. It will create the file on
its own as long as you have set up a file name. dv will add a row every time "recordday" is called.

## twilio
to get a text every day, you need ot set up a twilio account. Then put the sid and secret and phone numbers into the .conf file. Then you should be good to go. The free credits they give you has lasted me 4 months so far. 




 

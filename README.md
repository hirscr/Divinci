# Divinci
A companion app for the Divi CLI wallet.

## What does Divinci do?

Divinci is intended to run along side of your own personal Divi CLI wallet, with the intention of improving the way
transactions are viewed as well as being able to record daily staking income for the dreaded tax day.It also texts you
daily about your staking results for the day as well as whether or not you won a lottery.

## setting up Divinci
Divinci is a script. So go into the divi_ubuntu directory, install dv.py and divinci.conf. Edit the divinci.conf file to be appropriate for your user directory, your timezone (you may have to do some googling to find the correct thing to put there), your twilio credentials. Then you are going to have to make sure you have the correct libraries installed. So issues the following commands:
```
pip3 install pandas 
pip3 install requests
pip3 install pprint 
pip3 install twilio 
pip3 install commentjson
```

Next you want to set up an alias for divinci. To do so, use the following command:
```alias dv='python3 dv.py'```

This will allow you to easily, run the commands that are sent to the script.

## using Divinci
Divinci has the following commands

| **Command** | **Description                                           |
|-------------|---------------------------------------------------------|
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
| multisend     |  send -amount- in -lot- batches       | 
| send           | send -amount- to an address       | 
| unlock         | unlocks the wallet for -seconds-       | 
| lock           | locks the wallet for staking       | 


so, to use any command you simply write `dv command argument` examples as follows:
```
dv smstest
dv recordday
dv checkfork
dv staked 5
dv price divi
```

You will also need to set up the divinci.conf file. There are comments in the file that guide you on what to put. Take care about where commas are and what needs quotes.

## getting a financial started
I wanted to record daily income, running balance, and the daily income in $, so I set up a cron job to run dv.py every day at midnight. Thus I get a file with each row as follows:

##### 'Date-time','Balance','Lottery','Received','Number of Stakes','Daily Income','Daily RoR','Extended RoR','BTCPrice','DiviPrice','$ income'

In order to do so, you have to set up the divinci.conf file with the correct data for your set up. Also, make sure it is called "divinci.conf" not the example name. It will create the file on its own as long as you have set up a file name. dv will add a row every time the `recordday` command is called.

## using crontab
I use crontab for two things. First, I schedule a "recordday" once a day to add a staking income line to the financials file. The recordday job will send me a summary as an SMS (if you set up a twilio account). Then, every 5 minutes I schedule a "checkfork" to make sure my wallet has not gotten on to a forked blockchain. The checkfork job will send me a text if it has found that the wallet has been on a forked chain 5 consecutive times. Thus if your wallet gets forked, you will know in 30 minutes.

so my crontab file looks as follows:
```
0 0 * * * cd /home/user/divi_ubuntu/ && python3 dv.py recordday >> dvoutput.txt 2>&1
*/5 * * * * cd /home/user/divi_ubuntu/ && python3 dv.py checkfork >> forkcheck.txt 2>&1
```

## twilio
to get a text every day, you need to set up a twilio account. The put the sid and secret and phone numbers into the .conf file. Then you should be good to go. The free credits they give you has lasted me 4 months so far.

If you want to test the twilio aspect of the scriopt, you can just send a test message to yourself, with the 'smstest' command.


## extending divinci for your programming

First you will have to set up the Config file to be applicable to you.  Put the companion app in the same directory as your wallet.

All commands for Divinci are based around `cmd`

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

So call listtransactions and pull up the last 300 txs. Then you want to put this human unreadable data into a dataframe.

`df=MakeDFofTXs(txs)`

Now you can print a version of the txs with a balance with:
`printTXs(df)`

Or you can grab a subset of the transactions
`smallDF=getRecentTXs(df, seconds)`

and then print that.

You can get the current price of any coin
`GetPrice("divi")'



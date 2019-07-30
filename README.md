# Divinci
A companion app for the Divi CLI wallet.

## What does Divinci do?

Divinci is intended to run along side of your own personal Divi CLI wallet, with the intention of improving the way
transactions are viewed as well as being able to record daily staking income for the dreaded tax day.It also texts you
daily about your staking results for the day as well as whether or not you won a lottery.

I would like to set it up such that you can simply write commands to it from the shell, but I have not yet learned how to do that. Thus you must start python, load it in, then call the functions from the python prompt.

to load it in:
`python`
`exec(open('dv.py').read())`

Now you can call it by functions. Please note, you will probably get a bunch of errors the first time you try. This is 
Because DV is set up as a script that gets run by crontab every day, once a day. DV does not keep running, it only goes once through. But if you are at python prompt you can still call the functions as needed. Further, DV uses twillio, to send you texts every time crontab calls it. That is how I get my daily staking results and notifications of lottery wins.

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

So call listtransactions and pull up the last 300 txs. Then you want to put this human unreadable data into a dataframe.

`df=MakeDFofTXs(txs)`

Now you can print a version of the txs with a balance with:
`printTXs(df)`

Or you can grab a subset of the transactions
`smallDF=getRecentTXs(df, seconds)`

and then print that.

You can get the current price of any coin
`GetPrice("divi")'

## getting a financial started
I wanted to record daily income, running balance, and the daily income in $, so I set up a cron job to run dv.py every day at midnight. Thus I get a file with each row as follows:

##### 'Date-time','Balance','Lottery','Received','Number of Stakes','Daily Income','Daily RoR','Extended RoR','BTCPrice','DiviPrice','$ income'

In order to do so, you have to set up the divinci.conf file with the correct data for your set up. It will create the file on
its own as long as you have set up a file name. dv will add a row every time it is called (which is a pain right now, since I want to use the pretty transaction printing also)

## twilio
to get a text every day, yo uneed ot set up a twilio account. The put the sid and secret and phone numbers into the .conf file. Then you should be good to go. The free credits they give you has lasted me 4 months so far.




 

# **Telegram Crawler** 


A Python package that communicates with the [Telegram messenger CLI](https://github.com/vysheng/tg), to send and receive messages and more. *Since January 2014*

Works with Python 3.3+.

## **Dependencies** ##
Install dependencies:
```
pip install -r requirements
```

## **Usage** ##

For running crawler, first you need to combile [My edited version of tg CLI](https://github.com/vysheng/tg) with the following command:
```
./bin/telegram-cli -k server_pub -p 4458 --json
```

then run the crawler:
```
python crawler.py
```
# **Telegram Crawler** 


Using this crawler, you can crawl telegram channels, groups or your private chats. Chats will be saved in SQLiteDB and text file with newline delimiter.
You can query with different parameters like channel names, group names, telegram usernames, telegram unique ids and etc.

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
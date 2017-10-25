# **Telegram Crawler** 


Using this crawler, you can crawl telegram channels, groups or your private chats. Chats will be saved in SQLite database and text file.
You can query in database with different parameters like channel names, group names, telegram usernames, telegram unique ids and etc.

Works with Python 3.3+.

## **Dependencies** ##
Install dependencies using this command:
```
pip install -r requirements
```
and if you don't have sqlite3, install it:
```
sudo apt-get install sqlite3
```

## **Usage** ##

For running this cute crawler, first you need to compile [my forked version of tg CLI](https://github.com/vhdmsm/tg). I fixed some of tg issues that causes tg to crash. After compiling tg with `make` command, run it using the following command:
```
./bin/telegram-cli -k server_pub -p 4458 --json
```

then run the crawler:
```
python crawler.py
```

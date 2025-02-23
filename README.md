# twitchTranslateBot
Twitch bot using twitchio and Google Translate python libraries to detect the language of comments and automatically translate to a desired language.

The script generates a list of global/local channel emotes from twitch and bttv and strip these from comments in an effort to increase the accuracy of the language detection.

# Requirements

Python version 3.8 or higher and the following packages. 

https://www.python.org/

```
pip install twitchio==2.10.0 requests googletrans
```
Will not currently work with twitchio 3.

You will need an access token, create a new twitch account for the bot to use and visit https://twitchtokengenerator.com to generate one. DO NOT SHARE THIS TOKEN WITH ANYONE.


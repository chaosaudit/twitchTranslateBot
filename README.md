# twitchTranslateBot
Twitch bot using twitchio and Google Translate python libraries to detect the language of comments and automatically translate to a desired language.

The script generates a list of global/local channel emotes from twitch and bttv to strip these from comments in an effort to increase the accuracy of the language detection.

# Requirements

Python version 3.8 or higher and the following packages. 

https://www.python.org/

You will need an access token, create a new twitch account for the bot to use and visit https://twitchtokengenerator.com to generate one. DO NOT SHARE THIS TOKEN WITH ANYONE.

# Usage

Clone or download the git repo

```
git clone https://github.com/chaosaudit/twitchTranslateBot
cd twitchTranslateBot
pip install -r requirements.txt
```
The bot will not currently work with twitchio 3.


python3 translateBot.py -a <access_token> -c <channel>

to join multiple channels pass the -c argument once for each channel e.g. -c <channel_one> -c <channel_two>

By default the bot will attempt to detect all comments that aren't English and translate them into English

use "!autotranslate on/off" in chat to toggle the automatic detection.
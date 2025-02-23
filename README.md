# twitchTranslateBot
Twitch bot using twitchio and Google Translate python libraries to detect the language of comments and automatically translate to a desired language.

The script generates a list of global/local channel emotes from twitch and bttv to strip these from comments in an effort to increase the accuracy of the language detection.

# Requirements

Python version 3.8 or higher and twitchio version 2 (tested with twitchio==2.10.0). 

https://www.python.org/

You will need an access token, create a new twitch account for the bot to use and visit https://twitchtokengenerator.com to generate one. DO NOT SHARE THIS TOKEN WITH ANYONE.

# Usage

Clone or download the git repo

```
git clone https://github.com/chaosaudit/twitchTranslateBot
cd twitchTranslateBot
pip install -r requirements.txt
python3 translateBot.py -a <access_token> -c <channel>
```
The bot will not currently work with twitchio 3.

To join multiple channels pass the -c argument once for each channel e.g. -c <channel_one> -c <channel_two>

By default the bot will attempt to detect all comments that aren't English and translate them into English

use "!autotranslate on/off" in chat to toggle the automatic detection.
"!translate to:<language_code> <message>" can be used to translate a message into a specific language

# Alternate version

The alternate version of the bot is aimed at bi-lingual friendly streams, any message determined to be one language, will be translated to another, and vice versa.
e.g. All English messages will be translated to German, and all German messages will be translated to English.

from twitchio.ext import commands
from googletrans import Translator
from bs4 import BeautifulSoup
import requests
import argparse

parser = argparse.ArgumentParser(
                    prog='https://github.com/chaosaudit/twitchTranslateBot',
                    description='Twitch bot using twitchio and Google Translate python libraries to detect the language of comments and automatically translate to a desired language.',
                    epilog='Requires twitchio 2.10.0, will not work with 3.0')

parser.add_argument('-a', '--access_token', help='https://twitchtokengenerator.com')
parser.add_argument('-c', '--channel', action="append", help="Specify a channel to join, can be used multiple times")
args = parser.parse_args()

print(f'Connecting to: {args.channel}')

# The bot will run in the channels listed here, can run in multiple channels at once, e.g. "channels = ['channel_1', 'channel_2']"
channels = args.channel 

 # This is the language that the autotranslate will use by default. 
 # List of codes can be found at https://developers.google.com/admin-sdk/directory/v1/languages
destination_language = 'en'


# This should automatically populate with all global, local and bttv emotes when the bot is launched, but
# words can also be added manually here.
# Any words added to this list will be stripped from any message before language detection / translation. 
# Can be used to ignore words that often cause a mistranslation, emote names, usernames etc...
word_ignore_list = set()


# Keeping track of the message that was sent before the current one.
# This allows people to use "!translate" on it's own to translate the
# message that was sent by the previous chatter.
previous_message = ""


statusAutotranslate = True # Translation on by default, chage to False for off by default

# twitchio bot and command handler.
class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=args.access_token,
            prefix='!',
            initial_channels=args.channel
            )

    async def event_ready(self):
        global word_ignore_list
        print(f'\nLogged in as | {self.nick}')
        print(f'User id is | {self.user_id}\n')


        # Grabbing all global / channel emotes to add to ignore list.
        global_emotes = await self.fetch_global_emotes()
        for emote in global_emotes:
            word_ignore_list.add(emote.name)
        print(f'{len(global_emotes)} global emotes added to ignore list.')

        fetch_global_bttv_emotes()
        fetch_global_ffz_emotes()

        for channel_name in channels:
            channel = await self.fetch_channel(channel_name)
            fetch_channel_emotes(channel.user.id, channel_name)
            fetch_channel_bttv_emotes(channel_name)
            fetch_channel_ffz_emotes(channel.user.id, channel_name)

        print(f'{len(word_ignore_list)} total ignored words')
        print(f'\n##### awaiting messages #####\n')

    # Everything under event_message will be run each time a new comment is seen in chat
    async def event_message(self, message):
        global previous_message, statusAutotranslate

        # Ignore our own messages
        if message.echo:
            previous_message = message.content
            return

        # Do not overwrite the previous message if the translate command is used on it's own.
        if message.content != '!translate':
            previous_message = message.content
        
        print(f'[{message.channel.name}] - {message.author.name}: {message.content}')

        if statusAutotranslate and str(message.content).split()[0] != '!translate':
            try:
                translator = Translator()
                cleaned_message = [word for word in str(message.content).split() if ((word not in word_ignore_list) and (word[0] != '@'))]
                if len(cleaned_message) < 4:
                    return
                cleaned_message = " ".join(cleaned_message)

                if cleaned_message != str(message.content):
                    print(f'# Cleaned message: {cleaned_message}')

                detection = translator.detect(cleaned_message)
                if detection.lang != destination_language and float(detection.confidence) > 0.90:
                    translation = translator.translate(cleaned_message, dest=destination_language)
                    print(f"{detection} | {translation}")
                    await message.channel.send(f'autotranslate | src={detection.lang} | {message.author.name}: "{translation.text}"')
                else:
                    if detection.confidence < 0.85:
                        print(f'## Unable to determine language ##: {message.content}')
            except Exception as e:
                print(e)

        # Wait for more commands after running event_message code
        await self.handle_commands(message)

    # !autotranslate command to show the status of auto function and allow it to be turned on or off by moderators.
    @commands.command()
    async def autotranslate(self, ctx: commands.Context):
        global statusAutotranslate
        arg_tokens = ctx.message.content.split()
        if len(arg_tokens) == 1:
            if statusAutotranslate:
                await ctx.send(f"autotranslate is currently [ACTIVE]. '!autotranslate off' to turn off.")
                return
            else:
                await ctx.send(f"autotranslate is currently [INACTIVE]. '!autotranslate on' to turn on.")
                return
        else:
            if len(arg_tokens) == 2:
                if arg_tokens[1].lower() == "on":
                    statusAutotranslate = True
                    await ctx.send(f"autotranslate is now [ACTIVE]. '!autotranslate off' to turn off.")
                    return
                if arg_tokens[1].lower() == "off":
                    statusAutotranslate = True
                    await ctx.send(f"autotranslate is now [INACTIVE]. '!autotranslate on' to turn on.")
                    return
    

    # !translate command to allow manual translation of comments.
    # !translate to:<language code> <message> to translate to languages other than English
    # e.g. "!translate to:es hello how are you" will translate the text to Spanish
    @commands.command(name="translate")
    async def translate(self, ctx: commands.Context):
        global previous_message

        translator = Translator()

        arg_tokens = previous_message.split()
        if previous_message.split()[0] == "!translate":
            arg_tokens = previous_message.split()[1:]
        
        author = ctx.author.name
        if "to:" in arg_tokens[0]:
            to_lang = arg_tokens[0].split(':')[1]
            subject = " ".join(arg_tokens[1:])
            print(f'Translating "{subject}" | to: {to_lang} ')
            try:
                translated = translator.translate(subject, dest=to_lang)
                text = translated.text
                new_message = f'[Translated by {author} | dest={to_lang}] - "{text}"'
                await ctx.send(new_message[:499])
            except Exception as e:
                if "invalid destination language" in str(e):
                    await ctx.send(
                        f"Unknown destination language. "
                        f"A list of codes can be found at: https://sites.google.com/site/opti365/translate_codes")
                    return
                else:
                    print(e)

        else:
            subject = " ".join(arg_tokens)
            print(f'Translating "{subject}" | to: en ')
            translated = translator.translate(subject, dest='en')
            src = translated.src
            text = translated.text
            new_message = f'[Translated by {author} | src={src}] - "{text}"'
            await ctx.send(new_message[:499])


def fetch_channel_emotes(channel_id, channel_name):
    global word_ignore_list
    default_badge_titles = ['cheer 1', 'cheer 100', 'cheer 1000', 'cheer 5000', 'cheer 10000', 'cheer 25000', 
                'Subscriber', '3-Month Subscriber', '6-Month Subscriber', '9-Month Subscriber', 
                '1-Year Subscriber', '2-Year Subscriber', 'Subscriber', '3-Month Subscriber', 
                '6-Month Subscriber', '9-Month Subscriber', '1-Year Subscriber', '2-Year Subscriber', 
                'Subscriber', '3-Month Subscriber', '6-Month Subscriber', '9-Month Subscriber', 
                '1-Year Subscriber', '2-Year Subscriber']
    
    page = requests.get(f'https://twitch-tools.rootonline.de/emotes.php?channel_id={channel_id}')
    soup = BeautifulSoup(page.text, 'html.parser')
    channel_emotes = []

    for emote in soup.find_all('div', class_='mt-2 text-center'):
        emote_title = emote.text.strip()
        if emote_title not in default_badge_titles:
            channel_emotes.append(emote_title)

    for emote in channel_emotes:
        word_ignore_list.add(emote)
    print(f'{len(channel_emotes)} twitch emotes added to ignore list from channel: {channel_name}')
    
def fetch_global_bttv_emotes():
    global word_ignore_list
    response = requests.get('https://api.betterttv.net/3/cached/emotes/global').json()
    for emote in response:
        word_ignore_list.add(emote['code'])
    print(f'{len(response)} global bttv emotes added to ignore list')

def fetch_channel_bttv_emotes(channel_name):
    global word_ignore_list
    response = requests.get(f'https://twitch.center/customapi/bttvemotes?channel={channel_name}').text
    emotes = response.split()
    for emote in emotes:
        word_ignore_list.add(emote)
    print(f'{len(emotes)} bttv emotes added to ignore list from channel: {channel_name}')

def fetch_global_ffz_emotes():
    global word_ignore_list
    response = requests.get('https://api.frankerfacez.com/v1/set/global/ids').json()
    for set in response['sets']:
        emotes = [emote['name'] for emote in response["sets"][set]["emoticons"]]
        for emote in emotes:
            word_ignore_list.add(emote)
    print(f'{len(emotes)} global ffz emotes added to ignore list.')

def fetch_channel_ffz_emotes(channel_id, channel_name):
    response = requests.get(f"https://api.frankerfacez.com/v1/room/id/{channel_id}").json()
    for set in response['sets']:
        emotes = [emote['name'] for emote in response["sets"][set]["emoticons"]]
        for emote in emotes:
            word_ignore_list.add(emote)                
    print(f'{len(emotes)} ffz emotes added to ignore list for channel: {channel_name}')


bot = Bot()
bot.run()


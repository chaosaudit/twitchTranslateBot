from twitchio.ext import commands
from googletrans import Translator
import requests

import json

with open('C:\\VMs\\creds.json', "r") as infile:
    creds_dict = json.loads(infile.read())

channels = ['chaosaudit', 'nyxipuff']

ACCESS_TOKEN: str = creds_dict['language_butt']['accessToken'] #  https://twitchtokengenerator.com/

# Change this to False to have autotranslate turned off by default when the bot is started.

statusAutotranslate = True


# Any words added to this list will be stripped from any message before language detection / translation. 
# Can be used to ignore words that often cause a mistranslation, emote names, usernames etc...
# This should automatically populate with all global, channel and bttv emotes when the bot is launched.

word_ignore_list = []

previous_message = ""

# twitchio bot and command handler.
class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=ACCESS_TOKEN,
            prefix='!',
            initial_channels=channels
            )

    async def event_ready(self):
        print(f'\nLogged in as | {self.nick}')
        print(f'User id is | {self.user_id}\n')


        # Grabing all global / channel emotes to add to ignore list.
        global_emotes = await self.fetch_global_emotes()
        for emote in global_emotes:
            word_ignore_list.append(emote.name)
        print(f'{len(global_emotes)} global emotes added to ignore list.')

        fetch_global_bttv_emotes()

        for channel_name in channels:
            channel = await self.fetch_channel(channel_name)
            fetch_channel_emotes(channel.user.id, channel_name)
            fetch_bttv_emotes(channel_name)

        print(f'{len(word_ignore_list)} total ignored words')
        print(f'\n##### awaiting messages #####\n')

        # with open('ignorelist.txt', 'w+') as outfile:
        #     for emote in word_ignore_list:
        #         outfile.write(f'{emote}\n')


        

    async def event_message(self, message):
        global statusAutotranslate
        # Ignore our own messages
        if message.echo:
            previous_message = message.content
            return
        
        # Keeping track of the message that was sent before the current one.
        # This allows people to use "!translate" on it's own to translate the
        # message that was sent by the previous chatter.
        if message.content != '!translate':
            previous_message = message.content

        print(message.content)

        if statusAutotranslate:
            try:
                async with Translator() as translator:
                    if len(message.content.split()) > 2:
                        cleaned_message = [word for word in str(message.content).split() if word not in word_ignore_list]
                        print(" ".join(cleaned_message))
                        detection = await translator.detect(" ".join(cleaned_message))
                        if detection.lang != "en" and float(detection.confidence) > 0.85:
                            translation = await translator.translate(" ".join(cleaned_message), dest="en")
                            print(f"{detection} | {translation}")
                            await message.channel.send(f'src={detection.lang} | {message.author.name}: "{translation.text}"') 
            except Exception as e:
                print(e)

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
    # e.g. "!translate to:es hello this is a test" will translate the text to Spanish
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
            print(f"Translating {subject} | to {to_lang} ")
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
            subject = " ".join(arg_tokens)
            print(f"Translating {subject} | to en ")
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
    channel_emotes = []
    for line in page.text.split('\n'):
        if 'class="mt-2 text-center"' in line:
            emote_title = line.split('">')[1].split('<')[0]
            if emote_title not in default_badge_titles:
                channel_emotes.append(emote_title)
    
    for emote in channel_emotes:
        if emote not in word_ignore_list:
            word_ignore_list.append(emote)

    print(f'{len(channel_emotes)} emotes added to ignore list from channel: {channel_name}')
    

def fetch_global_bttv_emotes():

    global word_ignore_list

    # Generate list of global bttv emotes.
    response = requests.get('https://api.betterttv.net/3/cached/emotes/global').json()
    for emote in response:
        if emote['code'] not in word_ignore_list:
            word_ignore_list.append(emote['code'])
    print(f'{len(response)} global bttv emotes added to ignore list')


def fetch_bttv_emotes(channel_name):

    global word_ignore_list

    response = requests.get(f'https://twitch.center/customapi/bttvemotes?channel={channel_name}').text
    emotes = response.split()
    for emote in emotes:
        if emote not in word_ignore_list:
            word_ignore_list.append(emote)
    print(f'{len(emotes)} bttv emotes added to ignore list from channel: {channel_name}')
    

bot = Bot()
bot.run()


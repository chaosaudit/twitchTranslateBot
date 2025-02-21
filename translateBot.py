from twitchio.ext import commands
from googletrans import Translator
import requests

import json

with open('C:\\VMs\\creds.json', "r") as infile:
    creds_dict = json.loads(infile.read())

channels = ['chaosaudit', 'nyxipuff']

ACCESS_TOKEN: str = creds_dict['language_butt']['accessToken'] #  https://twitchtokengenerator.com/


##### WORK IN PRGRESS #####


# Change this to False to have autotranslate turned off by default when the bot is started.
statusAutotranslate = True

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=ACCESS_TOKEN,
            prefix='?',
            initial_channels=channels
            )

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

        channel_ids = []
        for channel_name in channels:
            channel = await self.fetch_channel(channel_name)
            channel_ids.append(channel.user.id)
        
        for id in channel_ids:
            emote_list = requests.get(f"https://twitchemotes.com/channels/{id}")
            print(emote_list.text)


        global_emotes = await self.fetch_global_emotes()
        global_emotes = [x.name for x in global_emotes]
        print(f"Added {len(global_emotes)} global emotes to ignore list")
        
        # channel_emotes = await channel.fetch_emotes()
        # channel_emotes = [x.name for x in channel_emotes ]
        # print(channel_emotes)


    async def event_message(self, message):
        global statusAutotranslate
        # Ignore our own messages
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content)

        if statusAutotranslate:
            try:
                async with Translator() as translator:
                    if len(message.content.split()) > 4:
                        detection = await translator.detect(message.content)
                        if detection.lang != "en" and float(detection.confidence) > 0.85:
                            translation = await translator.translate(message.content, dest="en")
                            print(f"{detection} | {translation}")
                            await message.channel.send(f'src={detection.lang} | {message.author.name}: "{translation.text}"') 
            except Exception as e:
                await message.channel.send(e)

        await self.handle_commands(message)

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



bot = Bot()
bot.run()


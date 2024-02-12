from typing import Optional
import discord
from discord.ext import commands
from functools import wraps
import settings



#settingから読み込み
TOKEN = settings.BOT_TOKEN
MY_GUILD = discord.Object(id=settings.GUILD_ID)  # replace with your guild id
INITIAL_EXTENSIONS = [
  "cogs.random",
  "cogs.o_side",
  #"cogs.mogi",
  "cogs.score_atttack",
  "cogs.player_info"
]


class MyBot(commands.Bot):
    def __init__(self, *, command_prefix,intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.

    
    async def setup_hook(self):
        for cog in INITIAL_EXTENSIONS:
            await self.load_extension(cog)


        # インタラクションをシンクする。ギルドコマンドなので即時反映。
        await bot.tree.sync(guild = MY_GUILD)


    async def on_ready(self):
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('------')
        await bot.change_presence(activity=discord.CustomActivity(name="本日も誠心誠意、股濡れ中", type=1))
        return





intent = discord.Intents.all()
bot = MyBot(command_prefix='/',intents=intent)





bot.run(TOKEN)


#デコレータ例
def message_decorator(f):
    @wraps(f)
    def message_wrapper(*args, **kwargs):
        """デコレータのDocstringだよ"""
        print("デコレータだよ")
        return f(*args, **kwargs)
    return message_wrapper







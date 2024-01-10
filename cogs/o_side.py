import discord
from discord import app_commands
from discord.ext import commands
import settings
from typing import Optional
from libs import goma_util as gu
import pandas as pd

#あとでログを出すようにする...かも


MY_GUILD = discord.Object(id=settings.GUILD_ID)


class Oside(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #debugged
    @app_commands.command()
    async def gomamayo(self, interaction: discord.Interaction,text:str ="ゴママヨ"):
        """ゴママヨ発見器"""
        print(text)
        df = gu.gomamayo(text)
        print(df)
        x = gu.goma_em(df = df)
        if x is not None:
            await interaction.response.send_message(embed = x)
        else:
            await interaction.response.send_message("ゴママヨ not found...",ephemeral=True)


                


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Oside(bot),
        guilds = [MY_GUILD],
        override=True
    )


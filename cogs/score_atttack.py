import discord
from discord import app_commands
from discord.ext import commands,tasks
import random
import settings
from typing import Optional
from libs import music_util as mu
from libs import mogi_util as mou
import datetime as dt
import asyncio


SA_CHANNEL = 1191380562993229845
MOGI_REGI_CHANNEL = 1191380350404923462

MY_GUILD = discord.Object(id=settings.GUILD_ID)




def is_sachan(interaction: discord.Interaction):
    return interaction.channel_id == SA_CHANNEL
    






class SA(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        


    
    @app_commands.command()
    @app_commands.check(is_sachan)
    @app_commands.default_permissions(administrator=True)
    async def scheduel(self, interaction:discord.Interaction):
        self.managesa.start()

    
    #debugged
    @app_commands.command()
    @app_commands.check(is_sachan)
    async def start_sa(self, interaction:discord.Interaction):
        """
        このスレッドでスコアタを始める
        """
        if mou.is_on_mogi(interaction.channel_id):
            await interaction.response.send_message("このチャンネルは既にスコアタを開催中です。")
        
        else:
            with mou.Mogi2v2(interaction.channel_id) as mogi:
                await interaction.response.send_message("スコアタを開催します。\n この模擬は"+mogi.enddate+"に終了します\n /cを押して参加してください。現在0/4人")



    
    

    #debugged
    @app_commands.command()
    @app_commands.check(is_sachan)
    async def l_sa(self, interaction:discord.Interaction):
        """
        スコアタの課題曲,playerリストを表示するコマンド
        """
        if not mou.is_on_mogi(interaction.channel_id):
            await interaction.response.send_message("模擬が開催されていません。")
        else:
            with mou.Mogi2v2(interaction.channel_id) as mogi:
                channel = self.bot.get_channel(interaction.channel_id)
                guild = self.bot.get_guild(int(settings.GUILD_ID))
                usernamelist,players,teams,mrs = mogi.get_players()
                printstr = "\n"
                printstr = printstr + "TEAM1\n"
                for i in range(0,4):
                    if teams[i] == 1:
                        printstr = printstr + usernamelist[i]+"\t (MR:"+str(mrs[i])+")\n"
                printstr = printstr + "\nTEAM2\n"
                for i in range(0,4):
                    if teams[i] == 2:
                        printstr = printstr + usernamelist[i]+"\t (MR:"+str(mrs[i])+")\n"

                await interaction.response.send_message(printstr)

                n_song,songs= mogi.get_songs()
                embed = discord.Embed(
                    title = "課題曲",
                )
                embed.add_field(name="課題1",value=str(songs[0]))
                embed.add_field(name="課題2",value=str(songs[1]))
                embed.add_field(name="課題3",value=str(songs[2]))
            
                await channel.send(embed = embed)
            

    #debugged
    @app_commands.command()
    @app_commands.check(is_sachan)
    @app_commands.default_permissions(administrator=True)
    async def end_sa(self, interaction:discord.Interaction):
        """
        [admin専用コマンド]スコアタを強制的に中断します。
        """
        if not mou.is_on_mogi(interaction.channel_id):
            await interaction.response.send_message("模擬が開催されていません。")
        
        else:
            with mou.Mogi2v2(interaction.channel_id) as mogi:
                if mogi.cancel_mogi():
                    await interaction.response.send_message("Successfully cancelled")
                else:
                    await interaction.response.send_message("[Error]Bot Staffを呼んでください")



    #debugged
    @start_sa.error
    @l_sa.error
    @end_sa.error
    async def chan_error(self, interaction, error):
        if isinstance(error, discord.app_commands.errors.CheckFailure):
            await interaction.response.send_message("このチャンネルでは使用できません",ephemeral=True)

    #debugged
    @commands.Cog.listener()
    async def on_message(self,message):
        # メッセージ送信者がBotだった場合は無視する
        if message.author.bot:
            return
        
        tmpmes = message.content
        tlist = tmpmes.split()
        channel = self.bot.get_channel(message.channel.id)

        if not (message.channel.id) in SA_CHANNEL:
            return


        #submit関数の定義---------------
        if  tlist[0] == "!submit":
            if len(tlist) != 3:
                await channel.send("!submit [課題番号] [スコア]\nとして送信してください")
                return

            if int(tlist[1]) > 3 or int(tlist[1]) <= 0:
                await channel.send("!submitの次の数字は課題曲番号です。存在しない番号を入力してます")
                return
            
            if int(tlist[2]) < 0 or int(tlist[2]) > 1010000:
                await channel.send("存在しないスコアを記入しています")
                return
            
            #処理を書く-----------------------------------


        else:
            await channel.send("[Error] Try again")

    #debugged
    @tasks.loop(hours = 1)
    async def managesa(self):
    # 現在の時刻
        now = dt.datetime.now()
        for chan_id in SA_CHANNEL:
            #mogiが開催されていたら
            if mou.is_on_mogi(chan_id):
                #終了日時を過ぎているかチェック
                canfin = False
                with mou.Mogi2v2(chan_id) as mogi:
                    canfin =  dt.datetime.strptime(mogi.enddate, '%Y/%m/%d %H:%M:%S.%f') < now

                if canfin:
                    task1 = asyncio.create_task(self.mogiend(chan_id))
                    await task1
        return 
        


    #debugged
    async def saend(self,channel_id:int):
        guild = self.bot.get_guild(int(settings.GUILD_ID))
        channel = guild.get_channel(channel_id)
        with mou.Mogi2v2(channel_id) as mogi:
            mrs_before = mogi.mrs.copy()
            if (mogi.finish()):
                embedr = discord.Embed(title = "Result")
                embedr.add_field(name="TEAM1(sum)",value=str(mogi.total1))
                embedr.add_field(name="TEAM2(sum)",value=str(mogi.total2))
                await channel.send(embed = embedr)

                if mogi.winner == 1:
                    embed = discord.Embed(title = "TEAM1 win!!!!")
                elif mogi.winner == 2:
                    embed = discord.Embed(title = "TEAM2 win!!!!")
                else:
                    embed = discord.Embed(title = "DRAW!!!!")
                
                for i,player in enumerate(mogi.players):
                    embed.add_field(name=mou.id_to_username(player)+"(MR)",value=str(mrs_before[i])+" -> "+str(mogi.mrs[i]) + "\n delta: "+str(mogi.mrs[i] - mrs_before[i]))
                

                await channel.send(embed = embed)
                await channel.send("模擬戦を終了します。お疲れさまでした!!")

            else:
                await channel.send("[Error] Bot Staffを呼んでください")
        return




        

async def setup(bot: commands.Bot):
    await bot.add_cog(
        SA(bot),
        guilds = [MY_GUILD],
        override=True
    )
    




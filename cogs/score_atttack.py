import discord
from discord import app_commands
from discord.ext import commands,tasks
import random
import settings
from typing import Optional
from libs import music_util as mu
from libs import mogi_util as mou
from libs import sa_util as su
import datetime as dt
import asyncio

#提出チャンネル
SA_CHANNEL = 1199777689054228550

#模擬情報、結果報告チャンネル(開催判定はこっち)
SA_INFO = 1199777603721105478
MOGI_REGI_CHANNEL = 1199777370954010734

MY_GUILD = discord.Object(id=settings.GUILD_ID)
MOGI_ROLE_ID = settings.MOGI_ROLE

SA_LOCKED = []




def is_sachan(interaction: discord.Interaction):
    return interaction.channel_id == SA_INFO


def is_subchan(interaction: discord.Interaction):
    return interaction.channel_id == SA_CHANNEL

def is_regichan(interaction: discord.Interaction):
    return interaction.channel_id == MOGI_REGI_CHANNEL
    






class SA(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        


    
    @app_commands.command()
    @app_commands.check(is_sachan)
    @app_commands.default_permissions(manage_guild=True)
    async def schedule(self, interaction:discord.Interaction):
        """
        [admin専用]一週間に1回のスコアアタックを開始するコマンド
        """
        await interaction.response.send_message("スコアタが予約されました")
        self.managesa.start()
        


    @app_commands.command()
    @app_commands.check(is_sachan)
    @app_commands.default_permissions(manage_guild=True)
    async def end_schedule(self, interaction:discord.Interaction):
        """
        [admin専用]一週間に1回のスコアアタックを中止するコマンド
        """
        #cancel_saを呼び出す
        await interaction.response.send_message("現在のスコアタを中止します\n")
        task1 = asyncio.create_task(self.end_sa(SA_INFO))
        await task1
        self.managesa.stop()

        


    @app_commands.command()
    @app_commands.check(is_sachan)
    @app_commands.default_permissions(manage_guild=True)
    async def lock(self, interaction:discord.Interaction,member:Optional[discord.Member]):
        """
        [admin専用]ルールに違反したプレイヤーのスコアを0にロックするコマンド
        """
        await interaction.response.defer()
        with su.MogiSA(SA_INFO) as mogi:
            mogi.register_score(member.id,"l",0)
            mogi.register_score(member.id,"h",0)

        SA_LOCKED.append(member.id)

        await interaction.followup.send("Successfully locked  " + member.name)
        

        
    #error
    @app_commands.command()
    @app_commands.check(is_sachan)
    @app_commands.default_permissions(manage_guild=True)
    async def ls(self, interaction:discord.Interaction):
        """
        [admin専用]スコアタ課題の再掲示
        """
        await interaction.response.defer()
        llist = []
        hlist = []
        with su.MogiSA(SA_INFO) as mogi:
            hlist , llist = mogi.get_songs()

        embed = discord.Embed(
                                            title = "今週のスコアタ課題曲",
                                        )
        embed.add_field(name="課題h[対象者:16000<=MR]",value=str(hlist[0]),inline=False)
        embed.add_field(name="課題h[対象者:16000<=MR]",value=str(hlist[1]),inline=False)
        embed.add_field(name="課題l",value=str(llist[0]),inline=False)
        embed.add_field(name="課題l",value=str(llist[1]),inline=False)
        
        await interaction.followup.send(embed = embed)
           


    #debugged
    @schedule.error
    @end_schedule.error
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

        if message.channel.id in [SA_CHANNEL]:
            if message.author.id in SA_LOCKED:
                await channel.send("あなたは提出をロックされています")
                return 
            
            #submit関数の定義---------------
            if  tlist[0] == "!submit":
                if len(tlist) != 3:
                    await channel.send("!submit [課題記号(l or h)] [スコア]\nとして送信してください")
                    return
    
                if not(tlist[1] == "l" or tlist[1] == "h"):
                    await channel.send("!submitの次の文字は課題曲記号です。存在しない記号を入力してます\n lかhのいずれかを入力してください")
                    return
                
                if int(tlist[2]) < 0 or int(tlist[2]) > 1010000:
                    await channel.send("存在しないスコアを記入しています")
                    return
                
                #処理を書く-----------------------------------
    
                with su.MogiSA(SA_INFO) as mogi:
                    if mogi.is_in_sa(message.author.id):
                        if mogi.register_score(message.author.id,tlist[1],int(tlist[2])):
                            await message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
                        else:
                            await channel.send("提出種別を確認してください")
                        
                    else:
                        mogi.add_player(message.author.id)
                        if mogi.register_score(message.author.id,tlist[1],int(tlist[2])):
                            await message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
    
                        else:
                            await channel.send("提出種別を確認してください")
    

        elif message.channel.id in [MOGI_REGI_CHANNEL]:
            if  tlist[0] == "!init_all_mogi":
                guild = self.bot.get_guild(int(settings.GUILD_ID))
                member = guild.get_member(message.author.id)
                adminrole = guild.get_role(int(settings.ADMIN_ROLE))

                if adminrole in member.roles:
                    season = mou.init_all()
                    await channel.send("[mogiregister][mogi_2v2] initialized.\nシーズン"+str(season)+"が始まりました")

            elif tlist[0] == "!init_mogi_season":
                guild = self.bot.get_guild(int(settings.GUILD_ID))
                member = guild.get_member(message.author.id)
                adminrole = guild.get_role(int(settings.ADMIN_ROLE))

                if adminrole in member.roles:
                    season = mou.init_season()
                    await channel.send("シーズン"+str(season)+"が始まりました。")




     


    #debugged
    @tasks.loop(minutes = 20)
    async def managesa(self):
    # 現在の時刻
        now = dt.datetime.now()
        for chan_id in [SA_INFO]:
            #スコアタが開催されていたら
            if su.is_on_sa(chan_id):
                #終了日時を過ぎているかチェック
                canfin = False
                with su.MogiSA(chan_id) as mogi:
                    print("sa_end:\t"+mogi.end)
                    print("now:\t"+now.strftime('%Y/%m/%d %H:%M:%S.%f'))
                    canfin =  dt.datetime.strptime(mogi.end, '%Y/%m/%d %H:%M:%S.%f') < now
                    print("sa_end_can:\t"+str(canfin))
                    day_before = (dt.datetime.strptime(mogi.end, '%Y/%m/%d %H:%M:%S.%f') - dt.timedelta(days=1) < now) and (dt.datetime.strptime(mogi.end, '%Y/%m/%d %H:%M:%S.%f') - dt.timedelta(hours=23,minutes= 40) > now)

                
                if canfin:
                    #スコアタを終了し
                    task1 = asyncio.create_task(self.end_sa(chan_id))
                    await task1

                    #新しく開始する
                    task2 = asyncio.create_task(self.start_sa(chan_id))
                    await task2

                if day_before:
                    guild = self.bot.get_guild(int(settings.GUILD_ID))
                    role = guild.get_role(int(MOGI_ROLE_ID))
                    channel = self.bot.get_channel(chan_id)
                    await channel.send(role.mention + " 提出締め切り1日前です。")
                    
            else:
                #スコアタが開催されていなかったら開始する
                task2 = asyncio.create_task(self.start_sa(chan_id))
                await task2
        return 
        


    async def start_sa(self, chan_id):
        """
        このスレッドでスコアタを始める
        """
        SA_LOCKED = []
        guild = self.bot.get_guild(int(settings.GUILD_ID))
        channel2 = guild.get_channel(SA_CHANNEL)
        channel = self.bot.get_channel(chan_id)
        if su.is_on_sa(chan_id):
            await channel.send("このチャンネルは既にスコアタを開催中です。")
        
        else:
            with su.MogiSA(chan_id) as mogi:
                await channel.send("スコアタを開催します。\n このスコアタは"+mogi.end+"に終了します\n")
                await channel2.send("ただいまより提出を開始します----------\n写真を載せた後、!submit [課題種別] [スコア]として送信してください\n例: !submit h 1010000")

                #曲決め
                hl = [14.6,
                      14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,14.7,
                      14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,14.8,
                      14.9,14.9,14.9,14.9,14.9,14.9,14.9,14.9,14.9,14.9,14.9,
                      15.0,15.0,15.0,
                      15.1,
                      15.2,
                      15.3,
                      15.4
                      ]
                ll = [13.2,
                      13.3,
                      13.4,
                      13.5,13.5,
                      13.6,13.6,
                      13.7,13.7,
                      13.8,13.8,
                      13.9,13.9,
                      14.0,14.0,
                      14.1,14.1,
                      14.2,14.2,
                      14.3,14.3,
                      14.4,
                      14.5,
                      14.6
                      ]
                

                hlev = random.choice(hl)
                llev = random.choice(ll)

                hsong1 , _ = mu.randompick(level=hlev)
                lsong1 , _ = mu.randompick(level=llev)

                hsong2 , _ = mu.randompick(level=hlev)
                lsong2 , _ = mu.randompick(level=llev)


                while (hsong1.id  ==  hsong2.id):
                    hsong2,_ = mu.randompick(level=hlev)

                while (lsong1.id  ==  lsong2.id):
                    lsong2,_ = mu.randompick(level=llev)

                mogi.register_song(hsong1.id,hsong2.id,"h")
                mogi.register_song(lsong1.id,lsong2.id,"l")

                embed = discord.Embed(
                                            title = "今週のスコアタ課題曲",
                                        )
                embed.add_field(name="課題h[対象者:16000<=MR]",value=str(hsong1),inline=False)
                embed.add_field(name="課題h[対象者:16000<=MR]",value=str(hsong2),inline=False)
                embed.add_field(name="課題l",value=str(lsong1),inline=False)
                embed.add_field(name="課題l",value=str(lsong2),inline=False)

                
                await channel.send(embed = embed)
                                    
                




    #debugged
    async def end_sa(self,channel_id:int):
        guild = self.bot.get_guild(int(settings.GUILD_ID))
        channel = guild.get_channel(channel_id)
        channel2 = guild.get_channel(SA_CHANNEL)
        with su.MogiSA(channel_id) as mogi:
            if (mogi.finish()):
                #終了処理
                hrank = (mogi.stable[mogi.stable["assign"] == "h"]).sort_values(["p_rank"],ascending=True)
            
                embed = discord.Embed(title="結果発表[h]")
                for row in hrank.itertuples():
                    player = guild.get_member(row.player_id)
                    pname = mou.id_to_username(row.player_id)
                    if pname is None :
                        embed.add_field(name=str(int(row.p_rank))+"位 " + "ゲスト"+"(" +player.mention+")", value="score:"+str(row.score),inline=False)
                    else:
                        embed.add_field(name=str(int(row.p_rank))+"位 " + pname+"(" +player.mention+")", value="score:"+str(row.score)+"\n"
                                        +"MR:"+str(row.player_mr)+"->"+str(row.new_mr)+"(Delta:"+str(row.new_mr - row.player_mr)+")",inline=False)
                        
                await channel.send(embed = embed)


                lrank = (mogi.stable[mogi.stable["assign"] == "l"]).sort_values(["p_rank"],ascending=True)
            
                embed = discord.Embed(title="結果発表[l]")
                for row in lrank.itertuples():
                    player = guild.get_member(row.player_id)
                    pname = mou.id_to_username(row.player_id)
                    if pname is None :
                        embed.add_field(name=str(int(row.p_rank))+"位 " +"ゲスト"+"(" +player.mention+")", value="score:"+str(row.score),inline=False)
                    else:
                        embed.add_field(name=str(int(row.p_rank))+"位 " + pname+"(" +player.mention+")", value="score:"+str(row.score)+"\n"
                                        +"MR:"+str(row.player_mr)+"->"+str(row.new_mr)+"(Delta:"+str(row.new_mr - row.player_mr)+")",inline=False)
                
                await channel.send(embed = embed)

                mentionstr = ""
                for player in mogi.get_players():
                    mentionstr = mentionstr + guild.get_member(player).mention +" "
                await channel.send(mentionstr)

                await channel.send("スコアタを終了します。お疲れさまでした!!\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n-")

                await channel2.send("提出を締め切ります--------\n-\n-\n-\n-\n-\n-\n-\n-\n-\n-\n")

            else:
                await channel.send("[Error] Bot Staffを呼んでください")
        return




        

async def setup(bot: commands.Bot):
    await bot.add_cog(
        SA(bot),
        guilds = [MY_GUILD],
        override=True
    )
    




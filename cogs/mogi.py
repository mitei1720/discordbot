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


MOGI_CHANNELS = [
    1191380486090666065,
    1191380562993229845
] 
MOGI_REGI_CHANNEL = 1191380350404923462

MY_GUILD = discord.Object(id=settings.GUILD_ID)
MOGI_ROLE_ID = settings.MOGI_ROLE



def is_mogichan(interaction: discord.Interaction):
    return interaction.channel_id in  MOGI_CHANNELS
    
def is_regichan(interaction: discord.Interaction):
    return interaction.channel_id == MOGI_REGI_CHANNEL





class Mogi(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.is_fin.start()



    #debugged
    @app_commands.command()
    @app_commands.check(is_regichan)
    async def register(self, interaction: discord.Interaction, username:str="username",maxrate:float=16.00):
        """スコアタ登録コマンド,username(英数字のみ)とmaxrateは必須"""

        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。

        #await interaction.response.defer()
        #上を使わない場合はawait interaction.response.send_messageで返す
        #上を使う場合はawait interaction.followup.send(message, ephemeral=hidden) (返り値webhook注意)

        #登録
        suc,rate = mou.player_register(username,interaction.user.id,maxrate)

        if suc is True:
            #成功した場合はmogi権限を与え、成功と初期MRを知らせる
            
            #mogiの権限を与える
            guild = self.bot.get_guild(int(settings.GUILD_ID))
            member = guild.get_member(interaction.user.id)
            role = guild.get_role(int(MOGI_ROLE_ID))

            await member.add_roles(role)
        

            #成功と初期レートを知らせる
            await interaction.response.send_message("Successfully registerd as["+username+"].\n"+username+"の初期股濡レートは["+str(rate)+"]です。" )
        else:
            #失敗した場合はエラーを通告
            await interaction.response.send_message("[Error] Try again.",ephemeral=True)

   

    #debugged
    @app_commands.command()
    @app_commands.check(is_regichan)
    async def fix_rate(self, interaction: discord.Interaction, username:str=None,maxrate:float=None):
        """プロフィール更新コマンド"""

        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。

        #await interaction.response.defer()
        #上を使わない場合はawait interaction.response.send_messageで返す
        #上を使う場合はawait interaction.followup.send(message, ephemeral=hidden) (返り値webhook注意)

        

        if username is None and maxrate is None:
            #エラー
            await interaction.response.send_message("変更要素がありません.")
        else:
            #変更
            if mou.fix_player(username,interaction.user.id,maxrate):
                await interaction.response.send_message("Successfully fixed.")
            else:
                await interaction.response.send_message("[Error] Try again.",ephemeral=True)

    

    #Debugged
    @app_commands.command()
    @app_commands.check(is_regichan)
    #@app_commands.checks.has_any_role(1054345096620945408, 1054345230389882980)
    @app_commands.default_permissions(administrator=True)
    async def mute_player(self, interaction:discord.Interaction,member:Optional[discord.Member] = None):
        """
        [admin専用コマンド]mogi_playerロールの剥奪
        member: mogi権利を剥奪したいプレイヤー
        """
        guild = self.bot.get_guild(int(settings.GUILD_ID))
        role = guild.get_role(int(MOGI_ROLE_ID))
        await member.remove_roles(role)
        await interaction.response.send_message("[Mute]" + member.name +".")

   
    #Debugged
    @app_commands.command()
    @app_commands.check(is_regichan)
    @app_commands.default_permissions(administrator=True)
    async def activate_player(self, interaction:discord.Interaction,member:Optional[discord.Member] = None):
        """
        [admin専用コマンド]mogi_playerロールの復帰
        [※]muteされた人のみにコマンドを使用してください
        member: mogi権利を付与したいプレイヤー
        """
        guild = self.bot.get_guild(int(settings.GUILD_ID))
        role = guild.get_role(int(MOGI_ROLE_ID))
        await member.add_roles(role)
        await interaction.response.send_message("[UnMute]" + member.name +".")

    

    #Debugged
    @app_commands.command()
    @app_commands.check(is_regichan)
    @app_commands.default_permissions(administrator=True)
    async def init_all_mogi(self, interaction:discord.Interaction):
        """
        [admin専用コマンド]mogiの全情報リセット
        """
        season = mou.init_all()
        await interaction.response.send_message("[mogiregister][mogi_2v2] initialized.\nシーズン"+str(season)+"が始まりました")
        

    #Debugged
    @app_commands.command()
    @app_commands.check(is_regichan)
    @app_commands.default_permissions(administrator=True)
    async def init_mogi_season(self, interaction:discord.Interaction):
        """
        [admin専用コマンド]mogiの新シーズンを開始
        """
        season = mou.init_season()
        await interaction.response.send_message("シーズン"+str(season)+"が始まりました。")


    #debugged
    @register.error
    @fix_rate.error
    @mute_player.error
    @activate_player.error
    @init_all_mogi.error
    @init_mogi_season.error
    async def chan_error(self, interaction, error):
        if isinstance(error, discord.app_commands.errors.CheckFailure):
            await interaction.response.send_message("このチャンネルでは使用できません",ephemeral=True)

    
    #debugged
    @app_commands.command()
    @app_commands.check(is_mogichan)
    async def start(self, interaction:discord.Interaction):
        """
        このスレッドで2v2模擬を始める
        """
        if mou.is_on_mogi(interaction.channel_id):
            await interaction.response.send_message("このチャンネルは既に模擬戦を開催中です。")
        
        else:
            with mou.Mogi2v2(interaction.channel_id) as mogi:
                await interaction.response.send_message("2v2模擬戦を開催します。\n この模擬は"+mogi.enddate+"に終了します\n /cを押して参加してください。現在0/4人")



    
    #[Todo]
    @app_commands.command()
    @app_commands.check(is_mogichan)
    async def c(self, interaction:discord.Interaction):
        """
        このスレッドの2v2模擬に参加する
        """
        ###TO_DO
        ##########同じプレイヤーが2人以上参加しないようにはじく###########

        if not mou.is_on_mogi(interaction.channel_id):
            await interaction.response.send_message("模擬が開催されていません。/startコマンドで開催を宣言してください")

        elif mou.id_to_username(interaction.user.id) is None:
            await interaction.response.send_message("mogiregisterで登録を済ませてください")
        

        else:
            with mou.Mogi2v2(interaction.channel_id) as mogi:
                if interaction.user.id in mogi.players:
                    await interaction.response.send_message("すでに参加しています")
                elif mogi.player_add(interaction.user):
                    await interaction.response.send_message(mou.id_to_username(interaction.user.id)+" さんが参加\n現在"+str(mogi.n_player)+"/4人")
                    

                    #respondを使わないように書き換える -> 変えた
                    if mogi.n_player == 4:
                        channel = self.bot.get_channel(interaction.channel_id)
                        guild = self.bot.get_guild(int(settings.GUILD_ID))
                        mentionstr = ""
                        for player in mogi.players:
                            mentionstr = mentionstr + guild.get_member(player).mention +" "
                        await channel.send(mentionstr+"\n参加者が集まりました")
                        

                        if mogi.register_teams():
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

                            printstr = printstr + "\n課題曲を決定します。チーム1→チーム2の順で/spickを使って曲を選択してください\n"
                            await channel.send(printstr)

                            await channel.send("まずはチーム1の方お願いします。")

                else:
                    await interaction.response.send_message("満員です。次の模擬をお待ちください")

    #debugged
    @app_commands.command()
    @app_commands.check(is_mogichan)
    async def l(self, interaction:discord.Interaction):
        """
        mogiの課題曲,playerリストを表示するコマンド
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
    @app_commands.check(is_mogichan)
    @app_commands.default_permissions(administrator=True)
    async def end(self, interaction:discord.Interaction):
        """
        [admin専用コマンド]模擬を強制的に中断します。
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
    @app_commands.command()
    @app_commands.check(is_mogichan)
    @app_commands.describe( title='曲タイトル(部分一致)',genre='曲のジャンル',level='譜面定数',level_from='譜面定数下限',level_to='譜面定数上限',diff='難易度')
    async def spick(self, 
                    interaction:discord.Interaction,
                    title:str = None,
                    genre:str = None,
                    level:float = None,
                    level_from:float = None,
                    level_to:float =None,
                    diff:str=None):
        """
        2v2mogi用課題曲決定コマンド   mogi開催時以外では「意味ない」ので注意
        levelはlevel_to,fromより優先される
        """
        #模擬があるかチェック
        if mou.is_on_mogi(interaction.channel_id):
            with mou.Mogi2v2(interaction.channel_id) as mogi:
                #模擬参加者かチェック
                if interaction.user.id in mogi.players:
                    #チームをチェック
                    if mogi.teams[mogi.players.index(interaction.user.id)] == 1:
                        #課題曲が既に登録済みかをチェック
                        if mogi.songs[0] == "_":
                            #課題決定処理

                            channel = self.bot.get_channel(interaction.channel_id)
                            slist, mes =  mu.searchpick(title,genre,level,level_from,level_to,diff)
                            if(slist is None):
                                await channel.send(mes)
                            elif(mes is not None):
                                await channel.send(mes)
                                print_mes = ""
                                for song in slist:
                                    print_mes = print_mes + str(song) +"\n"

                                await channel.send(print_mes)
                            else:
                                mogi.register_song(slist[0].id)
                                await channel.send("チーム1選出の課題曲は以下に決定されました。")
                                embed = slist[0].make_embed()
                                await channel.send(embed = embed)
                                await channel.send("次にチーム2の方お願いします。")

                        else:
                            await interaction.response.send_message("チーム1選出の課題曲は決定済みです\n\n")
                    else:
                        #課題曲が既に登録済みかをチェック
                        if mogi.songs[1] == "_":
                            if mogi.songs[0] == "_":
                                await interaction.response.send_message("チーム1選出の課題曲が決定されるまでお待ちください\n\n")
                            else:
                                #課題決定処理

                                channel = self.bot.get_channel(interaction.channel_id)
                                slist, mes =  mu.searchpick(title,genre,level,level_from,level_to,diff)
                                if(slist is None):
                                    await channel.send(mes)
                                elif(mes is not None):
                                    await channel.send(mes)
                                    print_mes = ""
                                    for song in slist:
                                        print_mes = print_mes + str(song) +"\n"

                                    await channel.send(print_mes)
                                else:
                                    mogi.register_song(slist[0].id)
                                    await channel.send("チーム2選出の課題曲は以下に決定されました。")
                                    embed = slist[0].make_embed()
                                    await channel.send(embed = embed)

                                    if mogi.n_song == 2:
                                        await channel.send("全課題曲が出揃いました。")
                                        while True:
                                            mdata,errtxt = mu.randompick(level_from=13.5, level_to=15.0)

                                            if not (mdata.id in mogi.songs):
                                                break
                                        
                                        mogi.register_song(mdata.id)
                                        
                                        n_song,songs= mogi.get_songs()
                                        embed = discord.Embed(
                                            title = "課題曲",
                                        )
                                        embed.add_field(name="課題1",value=str(songs[0]))
                                        embed.add_field(name="課題2",value=str(songs[1]))
                                        embed.add_field(name="課題3",value=str(songs[2]))
                                    

                                        await channel.send("曲が未解禁等の場合はBot Staffを呼んでください\nスコアの提出は、リザルトの写真を送信した後、\n!submit [課題番号] [点数]\nを送信することで完了します。\n\n4人全員が全課題曲のスコアを提出し終えたとき、\n"+mogi.enddate+"になったとき模擬を終了しますのでご注意ください。")
                                        await channel.send(embed = embed)

                        else:
                            await interaction.response.send_message("チーム2選出の課題曲は決定済みです\n\n")
                
                else:
                    await interaction.response.send_message("あなたは模擬参加者ではありません")
        
        else:
            await interaction.response.send_message("模擬が開催されていません")


    #debugged
    @start.error
    @c.error
    @l.error
    @end.error
    @spick.error
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

        if not (message.channel.id) in MOGI_CHANNELS:
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
            
            #未提出数
            can_fin = 12
            with mou.Mogi2v2(message.channel.id) as mogi:
                if mogi.register_score(message.author.id,mogi.songs[int(tlist[1])-1],int(tlist[2])):
                    await message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

                    #全員提出が終わったときの処理-----------------------------
                    tmpt = mogi.stable.loc[:,['song1','song2','song3']]
                    tmpt_bool = (tmpt == 0)
                    can_fin = tmpt_bool.sum().sum()

            if can_fin == 0:
                await channel.send("全員のスコアが提出されました。")
                task1 = asyncio.create_task(self.mogiend(message.channel.id))
                await task1
                    #------------------------------------------------------

        else:
            await channel.send("[Error] Try again")

    #debugged
    @tasks.loop(minutes = 1)
    async def is_fin(self):
    # 現在の時刻
        now = dt.datetime.now()
        print(now.strftime('%Y/%m/%d %H:%M:%S.%f'))
        for chan_id in MOGI_CHANNELS:
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
    async def mogiend(self,channel_id:int):
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
        Mogi(bot),
        guilds = [MY_GUILD],
        override=True
    )
    




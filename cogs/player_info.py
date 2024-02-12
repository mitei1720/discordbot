import discord
from discord import app_commands
from discord.ext import commands
import settings
from typing import Optional
from libs import player_util as pu
from libs import mogi_util as mu
from libs import music_util as mou
import pandas as pd

#あとでログを出すようにする...かも

#提出チャンネル
SA_CHANNEL = 1199777689054228550

#模擬情報、結果報告チャンネル(開催判定はこっち)
SA_INFO = 1199777603721105478
MOGI_REGI_CHANNEL = 1199777370954010734

MY_GUILD = discord.Object(id=settings.GUILD_ID)
MOGI_ROLE_ID = settings.MOGI_ROLE

SA_LOCKED = []


MY_GUILD = discord.Object(id=settings.GUILD_ID)



def is_sachan(interaction: discord.Interaction):
    return interaction.channel_id == SA_INFO


def is_subchan(interaction: discord.Interaction):
    return interaction.channel_id == SA_CHANNEL

def is_regichan(interaction: discord.Interaction):
    return interaction.channel_id == MOGI_REGI_CHANNEL


class Player_info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #debugged
    @app_commands.command()
    async def mr(self, interaction: discord.Interaction, username: str = None):
        """
        レート確認
        他人の確認->usernameを入力
        """
        await interaction.response.defer()
        if username is None:
            rate  =  pu.get_mr(interaction.user.id)
            if rate == -1:
                await interaction.followup.send("Playerに登録されていません")
            else:
                
                embed = discord.Embed(
                    title = "MR",
                )
                embed.add_field(name=str(rate),value="")
                await interaction.followup.send(embed=embed)
            
        else:
            rate  =  pu.get_mr(username)
            if rate == -1:
                await interaction.followup.send("Playerに登録されていません")
            else:
                
                embed = discord.Embed(
                    title = username +" さんのMR",
                )
                embed.add_field(name=str(rate),value="")
                await interaction.followup.send(embed=embed)




    #debugged
    @app_commands.command()
    @app_commands.check(is_regichan)
    async def register(self, interaction: discord.Interaction, username:str,maxrate:float):
        """スコアタ登録コマンド,username(英数字のみ)とmaxrateは必須"""

        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。

        #await interaction.response.defer()
        #上を使わない場合はawait interaction.response.send_messageで返す
        #上を使う場合はawait interaction.followup.send(message, ephemeral=hidden) (返り値webhook注意)

        #登録
        
        if username is None:
            await interaction.response.send_message("usernameを入力してください",ephemeral=True)
            return
        
        if maxrate is None:
            await interaction.response.send_message("maxrateを入力してください",ephemeral=True)
            return
        
        if not (username.isalnum()):
            await interaction.response.send_message("usernameに記号を含めないでください",ephemeral=True)
            return


        await interaction.response.defer()
        suc,rate = mou.player_register(username,interaction.user.id,maxrate)

        if suc is True:
            #成功した場合はmogi権限を与え、成功と初期MRを知らせる
            
            #mogiの権限を与える
            guild = self.bot.get_guild(int(settings.GUILD_ID))
            member = guild.get_member(interaction.user.id)
            role = guild.get_role(int(MOGI_ROLE_ID))

            await member.add_roles(role)
        

            #成功と初期レートを知らせる
            await interaction.followup.send("Successfully registerd as["+username+"].\n"+username+"の初期股濡レートは["+str(rate)+"]です。" )
        else:
            #失敗した場合はエラーを通告
            await interaction.followup.send("[Error] Try again.",ephemeral=True)

    

    #debugged
    @app_commands.command()
    @app_commands.check(is_regichan)
    async def renew(self, interaction: discord.Interaction, username:str=None,maxrate:float=None):
        """プロフィール更新コマンド"""

        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。

        #await interaction.response.defer()
        #上を使わない場合はawait interaction.response.send_messageで返す
        #上を使う場合はawait interaction.followup.send(message, ephemeral=hidden) (返り値webhook注意)

        if username is not None and not (username.isalnum()):
            await interaction.response.send_message("usernameに記号を含めないでください",ephemeral=True)
            return
        

        if username is None and maxrate is None:
            #エラー
            await interaction.response.send_message("変更要素がありません.")
        else:
            await interaction.response.defer()
            #変更
            if mou.fix_player(username,interaction.user.id,maxrate):
                name = mou.id_to_username(interaction.user.id)
                await interaction.followup.send("Successfully fixed. -> ["+name+"]")
            else:
                await interaction.followup.send("[Error] Try again.",ephemeral=True)

    

    #Debugged
    @app_commands.command()
    @app_commands.check(is_regichan)
    #@app_commands.checks.has_any_role(1054345096620945408, 1054345230389882980)
    @app_commands.default_permissions(manage_guild=True)
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
    @app_commands.default_permissions(manage_guild=True)
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
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.choices(
        reason=[
            discord.app_commands.Choice(name="ペナルティ(DROP)",value="ペナルティ(DROP)"),
            discord.app_commands.Choice(name="ペナルティ(虚偽スコア申告)",value="ペナルティ(虚偽スコア申告)"),
            discord.app_commands.Choice(name="ペナルティ(虚偽レート申告)",value="ペナルティ(虚偽レート申告)"),
            discord.app_commands.Choice(name="ペナルティ(荒らし)",value="ペナルティ(荒らし)"),
            discord.app_commands.Choice(name="補正(レート増加調整)",value="補正(レート増加調整)"),
            discord.app_commands.Choice(name="補正(mogiキャンセル)",value="補正(mogiキャンセル)")
        ]
    )
    async def fix_rate(self, interaction:discord.Interaction,username:str,delta:int,reason:str):
        """
        [admin専用コマンド]rateの手動変更
        [※]補正が必要なときのみ使用可能
        username: MRを付与/剥奪したいプレイヤー
        delta: 変動MR
        reason: 変更理由
        """
        await interaction.response.defer()
        guild = self.bot.get_guild(int(settings.GUILD_ID))
        setter = guild.get_member(interaction.user.id)
        player = guild.get_member(mu.username_to_id(username))
        
        if pu.fix(username,delta):
            embed = discord.Embed(
                                            title = "MR変更通知"
                                        )
            embed.add_field(name="対象者",value=player.mention)
            embed.add_field(name="MR変更差分",value=delta)
            embed.add_field(name="変更理由",value=reason)
            embed.add_field(name="変更者",value=setter.mention)
            embed.add_field(name="補足",value="不服は変更者およびadminにご連絡ください")
            
            
            await interaction.followup.send(embed=embed)


            await player.send(embed=embed)
        
        return



    #debugged
    @register.error
    @renew.error
    @fix_rate.error
    @mute_player.error
    @activate_player.error
    async def chan_error(self, interaction, error):
        if isinstance(error, discord.app_commands.errors.CheckFailure):
            await interaction.response.send_message("このチャンネルでは使用できません",ephemeral=True)
            
                


            
        


                


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Player_info(bot),
        guilds = [MY_GUILD],
        override=True
    )


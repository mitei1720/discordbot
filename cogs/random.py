import discord
from discord import app_commands
from discord.ext import commands
import random
import settings
from typing import Optional
from libs import music_util as mu

#あとでログを出すようにする


MY_GUILD = discord.Object(id=settings.GUILD_ID)


class CRandom(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command()
    @app_commands.rename(member='user') #memerをuserに変更
    @app_commands.describe(
        member='指定するとuserにメンションをつけて占いの結果を返します。指定がないときは自分を占います',
    )
    async def gemusen(self, interaction: discord.Interaction, member:Optional[discord.Member] = None):
        """ゲムセン行くかおみくじ"""

        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。

        #await interaction.response.defer()
        #上を使わない場合はawait interaction.response.send_messageで返す
        #上を使う場合はawait interaction.followup.send(message, ephemeral=hidden) (返り値webhook注意)

        
        #おみくじ値の決定
        value = random.random()
        #自分を占うとゲムセン確率アップ
        if (member is None) or (member is interaction.user): 
            if value < 0.001:
                await interaction.response.send_message(f'モナ恋')
            elif value > 0.2:
                await interaction.response.send_message(f'{interaction.user.mention},ゲムセン行け！！！！')
            else:
                await interaction.response.send_message(f'{interaction.user.mention},モブは帰れ！！！！')
        #自分以外がゲムセンから追い出す
        else:
            if value > 0.6:
                await interaction.response.send_message(f'{member.mention},ゲムセン行け！！！！')
            else:
                await interaction.response.send_message(f'{member.mention},お前はもうゲムセン行くな')

    
    @app_commands.command()
    @app_commands.choices(
        diff=[
            discord.app_commands.Choice(name="BAS",value="BAS"),
            discord.app_commands.Choice(name="ADV",value="ADV"),
            discord.app_commands.Choice(name="EXP",value="EXP"),
            discord.app_commands.Choice(name="MAS",value="MAS"),
            discord.app_commands.Choice(name="ULT",value="ULT")
        ],
        genre=[
            discord.app_commands.Choice(name="POPS&ANIME",value="POPS&ANIME"),
            discord.app_commands.Choice(name="niconico",value="niconico"),
            discord.app_commands.Choice(name="VARIETY",value="VARIETY"),
            discord.app_commands.Choice(name="東方Project",value="東方Project"),
            discord.app_commands.Choice(name="イロドリミドリ",value="イロドリミドリ"),
            discord.app_commands.Choice(name="ORIGINAL",value="ORIGINAL"),
            discord.app_commands.Choice(name="ゲキマイ",value="ゲキマイ")
        ]
    )
    @app_commands.describe( genre='曲のジャンル',level='譜面定数',level_from='譜面定数下限',level_to='譜面定数上限',diff='難易度',username='mogiの名前,入力するとスコア目標を追加で表示します')
    async def rpick(self, interaction: discord.Interaction, 
                      genre:str = None,
                      level:float = None,
                      level_from:float = None,
                      level_to:float =None,
                      diff:str=None,
                      username:str = None
                    ):
        """課題曲をランダムに1曲出力 levelはlevel_to,fromより優先される"""

        #usernameがあっているか、mogiに問い合わせる

        #一曲引き抜いてくる
        await interaction.response.defer()
        mdata,errtxt = mu.randompick(genre=genre,level=level,level_from=level_from,level_to=level_to,diff=diff)


        if username is None:
            if errtxt is not None:
                await interaction.followup.send(errtxt)
            else:
                #成功処理
                embed = mdata.make_embed()
                await interaction.followup.send(embed = embed)
        else:
            if errtxt is not None:
                await interaction.followup.send(errtxt)
            else:
                #成功処理
                mdata.add_goals(username)
                embed = mdata.make_embed()
                await interaction.followup.send(embed = embed)

    @app_commands.command()
    @app_commands.default_permissions(manage_guild=True)
    async def song_import(self, interaction:discord.Interaction):
        """[admin専用コマンド]song_dataを更新。ウニのアプデの日に使ってください"""
        await interaction.response.defer()
        mu.import_music_data()
        await interaction.followup.send("Successfully updated!!")
    
        

async def setup(bot: commands.Bot):
    await bot.add_cog(
        CRandom(bot),
        guilds = [MY_GUILD],
        override=True
    )



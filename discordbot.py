# インストールした discord.py を読み込む
import discord
from discord import app_commands
import settings


TOKEN = settings.BOT_TOKEN



intents = discord.Intents.all()  # デフォルトのIntentsオブジェクトを生成


# 接続に必要なオブジェクトを生成
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')
    await tree.sync()#スラッシュコマンドを同期

@tree.command(name="test",description="テストコマンドです。")
async def test_command(interaction: discord.Interaction,text:str):
    await interaction.response.send_message("てすと！",ephemeral=True)#ephemeral=True→「これらはあなただけに表示されています」

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/neko':
        await message.channel.send('にゃーん')



# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
from typing import Optional
import discord
from discord import app_commands
from functools import wraps
import random
import settings


#settingから読み込み
TOKEN = settings.BOT_TOKEN
MY_GUILD = discord.Object(id=settings.GUILD_ID)  # replace with your guild id


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


#デコレータ例
def message_decorator(f):
    @wraps(f)
    def message_wrapper(*args, **kwargs):
        """デコレータのDocstringだよ"""
        print("デコレータだよ")
        return f(*args, **kwargs)
    return message_wrapper


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


#RandomTest
#コマンド使用userに対するメンション
#引数に指定した人のメンション
@client.tree.command()
@app_commands.rename(member='user') #memerをuserに変更
@app_commands.describe(
member='指定するとuserにメンションをつけて占いの結果を返します。指定しない場合、ユーザが存在しない場合は自分を占います',
)
async def gemusen(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """ゲムセン行くかおみくじ"""
    #おみくじ値の決定
    value = random.random()
    #自分を占うとゲムセン確率アップ
    if (member is None) or (member is interaction.user): 
        if value < 0.001:
            await interaction.response.send_message(f'モナ恋')
        elif value > 0.2:
            await interaction.response.send_message(f'{interaction.user.mention},ゲムセン行け！！！！')
        else:
            await interaction.response.send_message(f'{interaction.user.mention},ゲムセン行くな！！！！帰れ！！！！')
    #モブは帰れ
    else:
        if value > 0.6:
            await interaction.response.send_message(f'{member.mention},ゲムセン行け！！！！')
        else:
            await interaction.response.send_message(f'{member.mention},モブだから帰れ！！！！')



@client.tree.command()
@app_commands.describe(
    first_value='The first value you want to add something to ',
    second_value='The value you want to add to the first value',
)
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')


# The rename decorator allows us to change the display of the parameter on Discord.
# In this example, even though we use `text_to_send` in the code, the client will use `text` instead.
# Note that other decorators will still refer to it as `text_to_send` in the code.
@client.tree.command()
@app_commands.rename(text_to_send='text')
@app_commands.describe(text_to_send='Text to send in the current channel')
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends the text into the current channel."""
    await interaction.response.send_message(text_to_send)


# To make an argument optional, you can either give it a supported default argument
# or you can mark it as Optional from the typing standard library. This example does both.
@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Says when a member joined."""
    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user

    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


# A Context Menu command is an app command that can be run on a member or on a message by
# accessing a menu within the client, usually via right clicking.
# It always takes an interaction as its first parameter and a Member or Message as its second parameter.

# This context menu command only works on members
@client.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')


# This context menu command only works on messages
@client.tree.context_menu(name='Report to Moderators')
async def report_message(interaction: discord.Interaction, message: discord.Message):
    # We're sending this response message with ephemeral=True, so only the command executor can see it
    await interaction.response.send_message(
        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
    )

    # Handle report by sending it into a log channel
    log_channel = interaction.guild.get_channel(0)  # replace with your channel id

    embed = discord.Embed(title='Reported Message')
    if message.content:
        embed.description = message.content

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(embed=embed, view=url_view)


client.run(TOKEN)
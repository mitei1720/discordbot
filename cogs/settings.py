import os 
from dotenv import load_dotenv
from os.path import join, dirname



#アクセストークン読み込み
load_dotenv(verbose = True)
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GUILD_ID = os.environ.get("GUILD_ID")
UNI_TOKEN = os.environ.get("UNIREC_TOKEN")
BOT_PATH = os.environ.get("BOT_PATH")
MOGI_ROLE = os.environ.get("MOGI_ROLE")
SA_ROLE = os.environ.get("SA_ROLE")

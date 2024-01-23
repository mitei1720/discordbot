import os 
from dotenv import load_dotenv
from os.path import join, dirname



#アクセストークン読み込み
load_dotenv(verbose = True)
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
UNI_TOKEN = os.getenv("UNIREC_TOKEN")
MOGI_ROLE = os.getenv("MOGI_ROLE")
SA_ROLE = os.getenv("SA_ROLE")
SQL_URL = os.getenv("SQL_URL")
SQL_HOST = os.getenv("SQL_HOST")
SQL_USER = os.getenv("SQL_USER")
SQL_PORT = int(os.getenv("SQL_PORT"))
SQL_PASS = os.getenv("SQL_PASS")
SQL_DBNM = os.getenv("SQL_DBNM")
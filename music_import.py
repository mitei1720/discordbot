import requests
import pandas as pd
import settings
import sqlite3 as sq


TOKEN = settings.UNI_TOKEN
url1 = "https://api.chunirec.net/2.0/music/showall.json"


def makedb(dbname: "str|None"):
    con = sq.connect("./DB/"+dbname+".db")
    return con



def get_all_music_data(version: "str|None") -> None:
    """
    chunirecから全データを持ってきてdatabaseを作成or更新
    databaseは"./DB"
    --------------------------
    引数version 
    "jp1"→ new以前
    "jp2"→ new以降を含む
    """
    params = {'token': TOKEN, 'region': 'jp2'}
    response = requests.get(url1,params)
    if response.status_code == 200:
        # データを加工するなどの処理を行う
        df = pd.read_json(response.text)
        flattable = pd.json_normalize(df)
        #--------------------------------- 
    else:
        print("Error: ", response.status_code)


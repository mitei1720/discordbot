import requests
import pandas as pd
from typing import Tuple,Union
import settings
from . import db_util as du
import random
import discord
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

TOKEN = settings.UNI_TOKEN

#なぜかわからないけどこれで動く
DATABASE = "./DB/Randombase.db"


url1 = "https://api.chunirec.net/2.0/music/showall.json"
url2 = "https://api.chunirec.net/2.0/music/stat.json"

DIFF = ["BAS","ADV","EXP","MAS","ULT"]
GENRES = ["POPS&ANIME","niconico","VARIETY","東方Project","イロドリミドリ","ORIGINAL","ゲキマイ"]
CONST_MAX = 20.0
CONST_MIN = 0.0


#[ToDo]add_goals
class Music_data:
    def __init__(self,id:str,name:str,artist:str,genre:str,diff:str,level:int,lconst:float):
        self.id = id
        self.name = name
        self.artist = artist
        self.genre = genre
        self.diff = diff
        self.level = level
        self.lconst = lconst 
        self.goals = []


    #debugged
    def add_goals(self,username:str):
        with du.DBwrapper(DATABASE) as db:
            rows  = db.get("mogiregister",{"username":username})
            for row in rows:
                cr = row["maxrate"]
                #mr = rows[0]["rate"]
                diff = self.diff[0]
                self.goals = get_score_goals(self.id[:-2],diff.lower(),cr)

        
    #debugged
    def make_embed(self):
        embed = discord.Embed(
            title = "課題曲",
            description=self.name
        )
        embed.add_field(name="アーティスト",value=self.artist)
        embed.add_field(name="ジャンル",value=self.genre)
        embed.add_field(name="難易度",value=self.diff)
        embed.add_field(name="レベル",value=str(self.level).replace('.5','+').replace('.0',''))
        embed.add_field(name="譜面定数",value=self.lconst)

        if(len(self.goals) != 0):
            embed.add_field(name="目標1",value=self.goals[0])
            embed.add_field(name="目標2",value=self.goals[1])
            embed.add_field(name="目標3",value=self.goals[2])


        return embed


    #debugged
    def __str__(self):
        return f"タイトル:\t{ self.name }\nジャンル:\t{ self.genre }\n難易度:\t{ (str(self.level)).replace('.5','+').replace('.0','')}\n定数:\t{self.lconst}"
    
    

#debugged
#chunithm全曲をデータベースに挿入、更新するスクリプト。
#定期的に実行すること(あとで自動化するかも)
def import_music_data(version: str = "jp2") -> None:
    """
    chunirecから全データを持ってきてdatabaseを作成or更新
    databaseは"./DB"
    --------------------------
    引数version 
    "jp1"→ new以前
    "jp2"→ new以降を含む
    """
    #HTTPでchunirecにrequestを送る
    params = {'token': TOKEN, 'region': version}
    response = requests.get(url1,params)


    if response.status_code == 200:
        #ネストjsonをフラットにする処理-----
        data = response.json()
        flattable = pd.json_normalize(data)
        #csvをデータベースに落とし込む
        
        flattable =flattable.rename(columns=lambda s: s.replace('.','_'))

        #basテーブルへ分割
        tbl_bas = flattable[["meta_id","meta_title","meta_genre","meta_artist","meta_release","meta_bpm","data_BAS_level","data_BAS_const","data_BAS_maxcombo","data_BAS_is_const_unknown"]]
        tbl_bas = tbl_bas.rename(columns=lambda s: s.replace('data_BAS_',''))
        tbl_bas["diff"] = "BAS"
        tbl_bas = tbl_bas[tbl_bas["is_const_unknown"] == 0]
        tbl_bas["meta_id"] = tbl_bas["meta_id"] +"_B"

        #advテーブルへ分割
        tbl_adv = flattable[["meta_id","meta_title","meta_genre","meta_artist","meta_release","meta_bpm","data_ADV_level","data_ADV_const","data_ADV_maxcombo","data_ADV_is_const_unknown"]]
        tbl_adv = tbl_adv.rename(columns=lambda s: s.replace('data_ADV_',''))
        tbl_adv["diff"] = "ADV"
        tbl_adv = tbl_adv[tbl_adv["is_const_unknown"] == 0] 
        tbl_adv["meta_id"] = tbl_adv["meta_id"] +"_A"

        #expテーブルへ分割
        tbl_exp = flattable[["meta_id","meta_title","meta_genre","meta_artist","meta_release","meta_bpm","data_EXP_level","data_EXP_const","data_EXP_maxcombo","data_EXP_is_const_unknown"]]
        tbl_exp = tbl_exp.rename(columns=lambda s: s.replace('data_EXP_',''))
        tbl_exp["diff"] = "EXP"
        tbl_exp = tbl_exp[tbl_exp["is_const_unknown"] == 0]
        tbl_exp["meta_id"] = tbl_exp["meta_id"] +"_E"

        #masテーブルへ分割
        tbl_mas = flattable[["meta_id","meta_title","meta_genre","meta_artist","meta_release","meta_bpm","data_MAS_level","data_MAS_const","data_MAS_maxcombo","data_MAS_is_const_unknown"]]
        tbl_mas = tbl_mas.rename(columns=lambda s: s.replace('data_MAS_',''))
        tbl_mas["diff"] = "MAS"
        tbl_mas = tbl_mas[tbl_mas["is_const_unknown"] == 0]
        tbl_mas["meta_id"] = tbl_mas["meta_id"] +"_M"


        #ultテーブルへ分割
        tbl_ult = flattable[["meta_id","meta_title","meta_genre","meta_artist","meta_release","meta_bpm","data_ULT_level","data_ULT_const","data_ULT_maxcombo","data_ULT_is_const_unknown"]]
        tbl_ult = tbl_ult.rename(columns=lambda s: s.replace('data_ULT_',''))
        tbl_ult["diff"] = "ULT"
        tbl_ult = tbl_ult[tbl_ult["is_const_unknown"] == 0]
        tbl_ult["meta_id"] = tbl_ult["meta_id"] +"_U"

        #テーブル統合
        tbl_all = pd.concat([tbl_bas, tbl_adv, tbl_exp, tbl_mas, tbl_ult],axis=0,ignore_index=True)

        
        #統合テーブルをデータベース化
        with du.DBwrapper(DATABASE) as db:
            db.cursor.execute("DROP TABLE IF EXISTS all_music")
            db.connection.commit()

            db.set_from_pd(tbl_all)

        #--------------------------------- 
    else:
        print("Error: ", response.status_code)




#debugged
def randompick(genre:str = None,level:float = None,level_from:float = None,level_to:float =None,diff:str=None)-> Tuple["Music_data|None","str|None"]:
    """
    全曲データから指定条件で曲を一曲ランダムピック
    ------------------------------------------
    引数を指定しない場合は絞り込まない。
    genre:      ジャンル
    level:      譜面定数
    level_from: 下限の譜面定数
    level_to:   上限の譜面定数
    diff:       難易度 BAS.ADV.EXP.MAS.ULT
    ---
    ※levelはlevel_to,level_fromより優先される
    """

    #エラー処理
    if not(genre in GENRES) and (genre is not None):
        errm = "Genre not found!! Select from here:\n"
        ex_ger = ",".join(GENRES)
        print(errm+ex_ger)
        return None , errm+ex_ger
    
    if not(diff in DIFF) and (diff is not None):
        errm = "DIFF not found!! Select from here:\n"
        ex_dif = ",".join(DIFF)
        print(errm+ex_dif)
        return None , errm+ex_dif

    
    #条件で探しに行く
    with du.DBwrapper(DATABASE) as db:
        dat = {}

        #ジャンルのsql指定
        if(genre is not None):
            dat["meta_genre"] = genre
        
        #レベルのsql指定
        if(level is not None):
            dat["const"] = level

        elif(level_from is not None) and (level_to is None):
            dat["const"] = (level_from,CONST_MAX)
        
        elif(level_from is None) and (level_to is not None):
            dat["const"] = (CONST_MIN,level_to)
        
        elif(level_from is not None) and (level_to is not None):
            dat["const"] = (level_from,level_to)

        #難易度の指定(非推奨)
        if(diff is not None):
            dat["diff"] = diff

        print("finding...")
        

        print(dat)
        
        #Music_dataリスト  
        song_list = []

        for row in db.get("all_music",dat):
            song_list.append(row)

        imax = len(song_list)

        #抽出結果があるならその中からランダムピック
        if imax != 0:
            rr = song_list[random.randint(0, imax - 1)]
            return Music_data(rr["meta_id"],rr["meta_title"],rr["meta_artist"],rr["meta_genre"],rr["diff"],rr["level"],rr["const"]), None
        else:
            return None,"No such songs!!"


#debugged
def searchpick(title:str = None, genre:str = None,level:float = None,level_from:float = None,level_to:float =None,diff:str=None)-> Tuple[Union[list,None],Union[str,None]]:
    """
    全曲データから指定条件で曲を一曲ランダムピック
    ------------------------------------------
    引数を指定しない場合は絞り込まない。
    genre:      ジャンル
    level:      譜面定数
    level_from: 下限の譜面定数
    level_to:   上限の譜面定数
    diff:       難易度 BAS.ADV.EXP.MAS.ULT
    ---
    ※返り値
    len(list) = 1 かつ str = Noneのとき →一曲ヒット。そのまま出力すればおｋ
    len(list) >=2 かつ str = "Select from here"のとき → 複数曲ヒット。選択肢から選ばせる。
    len(list) = None かつ str = "Too many songs hit. retry please" → ヒット件数が多すぎ、もう一度searchさせる
    """

    #エラー処理
    if not(genre in GENRES) and (genre is not None):
        errm = "Genre not found!! Select from here:\n"
        ex_ger = ",".join(GENRES)
        print(errm+ex_ger)
        return None , errm+ex_ger
    
    if not(diff in DIFF) and (diff is not None):
        errm = "DIFF not found!! Select from here:\n"
        ex_dif = ",".join(DIFF)
        print(errm+ex_dif)
        return None , errm+ex_dif

    
    #条件で探しに行く
    with du.DBwrapper(DATABASE) as db:
        dat = {}

        #曲名のsql指定
        if(title is not None):
            dat["like_ph"] = "(meta_title like  '%"+title+"%')" 

        #ジャンルのsql指定
        if(genre is not None):
            dat["meta_genre"] = genre
        
        #レベルのsql指定
        if(level is not None):
            dat["const"] = level

        elif(level_from is not None) and (level_to is None):
            dat["const"] = (level_from,CONST_MAX)
        
        elif(level_from is None) and (level_to is not None):
            dat["const"] = (CONST_MIN,level_to)
        
        elif(level_from is not None) and (level_to is not None):
            dat["const"] = (level_from,level_to)

        #難易度の指定(非推奨)
        if(diff is not None):
            dat["diff"] = diff

        print("finding...")
        

        print(dat)
        
        #Music_dataリスト  
        song_list = []

        for row in db.get("all_music",dat):
            song_list.append(Music_data(row["meta_id"],row["meta_title"],row["meta_artist"],row["meta_genre"],row["diff"],row["level"],row["const"]))

        imax = len(song_list)

        #抽出結果
        if imax >= 6:
            return None,"ヒット数が多すぎます。条件を絞ってください"
        elif imax == 0:
            return None,"No such songs!!"
        elif imax == 1:
            return song_list, None
        else:
            return song_list,"下記のいずれかの曲をtitleに入れてもう一度コマンドを実行してください"
        

#debugged
def get_score_goals(music_id:str,diff:str,rate:Union[float,int],version:str="jp2")-> Union[list,None]:
    glist = []
    params = {'id':music_id,'diff':diff,'token': TOKEN, 'region': version}
    response = requests.get(url2,params)
    print("API get is runnning")
    if type(rate) is int:
        rate = rate / 1000
        rate = float(Decimal(str(rate)).quantize(Decimal('0.1'), ROUND_HALF_UP))
    else:
        rate = float(Decimal(str(rate)).quantize(Decimal('0.1'), ROUND_HALF_UP))
        
            
    if response.status_code == 200:
        #ネストjsonをフラットにする処理-----
        data = response.json()
        flattable = pd.json_normalize(data)
        flattable =flattable.rename(columns=lambda s: s.replace('.','_'))
        print(flattable)
        if(rate > 17.29):
            gscore = flattable.at[0,"avg_17_30"]

            gscore1 = gscore + (gscore - flattable.at[0,"avg_17_20"]) // 2
            if(gscore1 > 1010000):
                gscore1 = 1010000      
            
            gscore2 = gscore1 + (flattable.at[0,"avg_17_30"] - flattable.at[0,"avg_17_20"]) // 4
            if(gscore2 > 1010000):
                gscore2 = 1010000
                
            
            if(gscore == 1010000):
                gscore1 = 1010001
                gscore2 = 1010001
            elif(gscore1 == 1010000):
                gscore2 = 1010001
            
            glist.append(gscore)
            glist.append(gscore1)
            glist.append(gscore2)


        
        elif (rate > 17.19):
            gscore = flattable.at[0,"avg_17_20"]
            gscore1 = flattable.at[0,"avg_17_30"]
            
            gscore2 = gscore1 + (gscore1 - gscore) // 2
            if(gscore2 > 1010000):
                gscore2 = 1010000

            if(gscore == 1010000):
                gscore1 = 1010001
                gscore2 = 1010001
            elif(gscore1 == 1010000):
                gscore2 = 1010001
            
            glist.append(gscore)
            glist.append(gscore1)
            glist.append(gscore2)
            

        else:
            gscore = flattable.at[0,"avg_"+('{:.2f}'.format(rate)).replace(".","_")]
            gscore1 = flattable.at[0,"avg_"+('{:.2f}'.format(rate+0.1)).replace(".","_")]
            gscore2 = flattable.at[0,"avg_"+('{:.2f}'.format(rate+0.2)).replace(".","_")]
            if(gscore == 1010000):
                gscore1 = 1010001
                gscore2 = 1010001
            elif(gscore1 == 1010000):
                gscore2 = 1010001
            glist.append(gscore)
            glist.append(gscore1)
            glist.append(gscore2)
            
        
        return glist

    else:
        return []


#get_score_goals("acb144b64b966911","m",16.80)





                        


    

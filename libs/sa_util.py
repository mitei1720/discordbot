import pandas as pd
from typing import Tuple
import settings
from . import db_util as du
from . import music_util as mu
from . import mogi_util as mou
import random
import discord
import datetime as dt
import numpy as np
import math
from typing import Optional, Union


#なぜかわからないけどこれで動く
DATABASE = "./DB/Randombase.db"


#[Todo] debug
def is_on_sa(chan_id:discord.Interaction.channel_id)->bool:
    with du.DBwrapper(DATABASE) as db:
        dat = {"chan_id":chan_id}
        rows = db.count("sa_cur",dat)
        if rows == 1:
            return True
        else:
            return False
        




class MogiSA(du.DBwrapper):
    def __init__(self,channel:discord.Interaction.channel_id, filePath:str = DATABASE):
        super().__init__(filePath)
        self.ev_id:int = 0
        self.start:str = ""
        self.end:str = ""
        self.chan_id = channel
        self.hsongs = []
        self.lsongs = []
        self.p_amount:int = 0
        self.ph_amount:int = 0
        self.pl_amount:int = 0
        self.stable =  pd.DataFrame(columns = [
            "id",
            "ev_id",
            "is_regi",
            "player_id",
            "assign",
            "score",
            "p_rank",
            "player_maxrate",
            "player_mr",
            "new_mr"
            ])

        self.is_new = False
        self.is_finish = False
        self.is_cancel = False
    
        
    
    def open(self):
        super().open()
        dat = {"chan_id":self.chan_id}
        nsa = self.count("sa_cur",dat)


        if nsa == 1:
            for row in self.get("sa_cur",dat):
                self.ev_id = row["id"]
                self.start = row["start"]
                self.end = row["end"]
                self.hsongs = [row["h_song1"],row["h_song2"]]
                self.lsongs = [row["l_song1"],row["l_song2"]]
                self.p_amount = row["p_amount"]
                self.ph_amount = row["ph_amount"]
                self.pl_amount = row["pl_amount"]

            dat2 = {"ev_id":self.ev_id}
            for i,row in enumerate(self.get("all_sa",dat2)):
                if(mou.id_to_username(row["player_id"]) is None):
                    self.stable.loc[i] = [
                        row["id"],
                        row["ev_id"],
                        False,
                        row["player_id"],
                        row["assign"],
                        row["score"],
                        row["p_rank"],
                        -1,
                        -1,
                        -1
                    ]
                else:
                    self.stable.loc[i] = [
                        row["id"],
                        row["ev_id"],
                        True,
                        row["player_id"],
                        row["assign"],
                        row["score"],
                        row["p_rank"],
                        row["player_maxrate"],
                        row["player_mr"],
                        row["new_mr"]
                    ]

                

        elif nsa ==0:
            self.is_new = True
            tmp_dt = dt.datetime.now()
            self.start = tmp_dt.strftime('%Y/%m/%d %H:%M:%S.%f')
            self.end = (tmp_dt + dt.timedelta(weeks=1)).strftime('%Y/%m/%d %H:%M:%S.%f')
            self.hsongs = ["_","_"]
            self.lsongs = ["_","_"]
            self.p_amount = 0
            self.ph_amount = 0
            self.pl_amount = 0

            try:
                dat = {
                   "start":self.start,
                   "end":self.end,
                   "chan_id":self.chan_id,
                   "h_song1":self.hsongs[0],
                   "h_song2":self.hsongs[1],
                   "l_song1":self.lsongs[0],
                   "l_song2":self.lsongs[1],
                   "p_amount":self.p_amount,
                   "ph_amount":self.ph_amount,
                   "pl_amount":self.pl_amount
                }
                self.set("sa_cur",dat)
                self.commit()
                tmpm = self.get("sa_cur",{"chan_id":self.chan_id})
                for tmp in tmpm:
                    self.ev_id = tmp["id"]
                
            except Exception as e:
                print("----------------rollback------------------\n")
                print("make new mogi")
                print(e)
                self.rollback()

        else:
            print("error--      Check Database")



    def get_players(self)->list:
        return self.stable["player_id"].to_list()
    
    def register_song(self,song_id1:str,song_id2:str,dset:str) -> bool:
        """
        SAの課題曲を登録する関数
        引数 
        song_id 2つ
        dset "h"または"l"

        返り値 ->成功したらTrue
        """
        if dset != "h" and dset != "l":
            return False
        
        elif dset == "h":
            if self.hsongs[0] != "_":
                return False
            else:
                self.hsongs[0] = song_id1
                self.hsongs[1] = song_id2
                return True

        else:
            if self.lsongs[0] != "_":
                return False
            else:
                self.lsongs[0] = song_id1
                self.lsongs[1] = song_id2
                return True
            
    def get_songs(self) -> Tuple[list,list]:
        """
        返り値 → h課題曲リスト,l課題曲リスト

        課題曲リスト-----
        いる場合はMusic_data
        いない場合は"_"
        --------------------
        """
        ldatalist = []
        hdatalist = []
        for hsong in self.hsongs:
            for row in self.get("all_music",{"meta_id":hsong}):
                hdatalist.append(mu.Music_data(row["meta_id"],row["meta_title"],row["meta_artist"],row["meta_genre"],row["diff"],row["level"],row["const"]))
        
        for lsong in self.lsongs:
            for row in self.get("all_music",{"meta_id":lsong}):
                ldatalist.append(mu.Music_data(row["meta_id"],row["meta_title"],row["meta_artist"],row["meta_genre"],row["diff"],row["level"],row["const"]))

        return hdatalist,ldatalist
    
    def is_in_sa(self,d_id)->bool:
        """
        d_idがスコアタに参加済みかどうか
        """
        players = self.stable["player_id"].to_list()
        return d_id in players
    

    def add_player(self,d_id)->bool:
        """
        d_idの新規プレイヤーをスコアタに追加する。
        """
        if mou.id_to_username(d_id) is None:
            self.stable.loc[self.p_amount] = [
                -1,
                self.ev_id,
                False,
                d_id,
                "yet",
                0,
                -1,
                -1,
                -1,
                -1
            ]
            self.p_amount += 1
            return True
        else:
            for row in self.get("mogiregister",{"d_id":d_id}):
                self.stable.loc[self.p_amount] = [
                    -1,
                    self.ev_id,
                    True,
                    d_id,
                    "yet",
                    0,
                    -1,
                    row["maxrate"],
                    row["rate"],
                    -1
                ]
            self.p_amount += 1
            return True
    

    def register_score(self,d_id,assign,score)->bool:
        """
        曲のスコア登録
        d_id:       playerのDiscordID
        song_id:    課題曲ID
        score:      登録されたスコア
        """

        if mou.id_to_username(d_id) is None:
            #模擬に登録していない人はlowしか提出できない.
            if assign == "h":
                return False
            
            elif(assign == "l"):
                #スコア記入処理
                self.stable.at[self.stable[self.stable['player_id'] == d_id].index[0],"score"] = score
                self.stable.at[self.stable[self.stable['player_id'] == d_id].index[0],"assign"] = assign
                self.stable["p_rank"] = self.stable.groupby(["assign"])["score"].rank(ascending=False,method='min')
                

                return True
            else:
                return False

        else:
            tmprate = 0
            dat = {"d_id":d_id}
            prows = self.get("mogiregister",dat)
            for prow in prows:
                tmprate = prow["rate"]
            
            if tmprate < 16000:
                if assign == "h":
                    return False

                elif(assign == "l"):
                    #スコア記入処理
                    self.stable.at[self.stable[self.stable['player_id'] == d_id].index[0],"score"] = score
                    self.stable.at[self.stable[self.stable['player_id'] == d_id].index[0],"assign"] = assign
                    self.stable["p_rank"] = self.stable.groupby(["assign"])["score"].rank(ascending=False,method='min')

                    return True
                else:
                    return False

            else:
                if assign == "h" or assign == "l":
                    #スコア記入処理
                    self.stable.at[self.stable[self.stable['player_id'] == d_id].index[0],"score"] = score
                    self.stable.at[self.stable[self.stable['player_id'] == d_id].index[0],"assign"] = assign
                    self.stable["p_rank"] = self.stable.groupby(["assign"])["score"].rank(ascending=False,method='min')

    
                    return True
            
                else:
                    return False
                       

    def cansel_sa(self)->bool:
        self.is_finish = True
        self.is_cancel = True
        return True
    

    def finish(self) -> bool:
        #フラグセット
        self.is_finish = True

        #人数総計
        self.pl_amount = (self.stable == 'l').sum().sum()
        self.ph_amount = (self.stable == 'h').sum().sum()

        if self.pl_amount == 0:
            self.pl_amount = 1
        
        if self.ph_amount == 0:
            self.ph_amount = 1

        #New_mmr計算
        for index, row in self.stable.iterrows():
            if row["is_regi"] is True:
                if int(row["p_rank"]) == 1:
                    if row["assign"] == "l":
                        self.stable.at[index, 'new_mr'] = row['player_mr'] + int(1000/self.pl_amount)
                    elif row["assign"] == "h":
                        self.stable.at[index, 'new_mr'] = row['player_mr'] + int(1000/self.ph_amount)

                
                elif int(row["p_rank"]) == 2:
                    if row["assign"] == "l":
                        self.stable.at[index, 'new_mr'] = row['player_mr'] + int(500/self.pl_amount)
                    elif row["assign"] == "h":
                        self.stable.at[index, 'new_mr'] = row['player_mr'] + int(500/self.ph_amount)
                
                elif int(row["p_rank"]) == 3:
                    if row["assign"] == "l":
                        self.stable.at[index, 'new_mr'] = row['player_mr'] + int(250/self.pl_amount)
                    elif row["assign"] == "h":
                        self.stable.at[index, 'new_mr'] = row['player_mr'] + int(250/self.ph_amount)

                else:
                    if row["assign"] == "l":
                        self.stable.at[index, 'new_mr'] = row['player_mr'] + int(100/self.pl_amount)
                    elif row["assign"] == "h":
                        self.stable.at[index, 'new_mr'] = row['player_mr'] + int(100/self.ph_amount)

                
                try:
                    sql = f"UPDATE all_sa SET new_mr = {self.stable.at[index, 'new_mr']} where player_id = {self.stable.at[index, 'player_id']} and ev_id = {self.ev_id};"
                    self.query(sql)
                    self.commit()
                except Exception as e:
                    print("put_new_mr")
                    print("----------------rollback------------------\n")
                    print(e)
                    self.rollback()
                    
       
            


        #データ移行 sa_cur -> sa_info
        row = {}
        for trow in self.get("sa_cur",{"id":self.ev_id}):
            row = trow
            
        row["ev_id"] = row["id"]
        row["pl_amount"] = self.pl_amount
        row["ph_amount"] = self.ph_amount
        row.pop("id")
        try:
            self.set("sa_info",row)
            self.commit()

        except Exception as e:
            print("move_data")
            print("----------------rollback------------------\n")
            print(e)
            self.rollback()
            return False

        #player_historyに追加
        try:
            for row in self.stable.itertuples():
                if row.is_regi is True:
                    dat = {"end":self.end,"kind":"sa","ev_id":self.ev_id,"new_mr":row.new_mr}
                    self.set("Player_"+str(row.player_id)+"_history",dat)
                    self.commit()
        except Exception as e:
            print("add_history")
            print("----------------rollback------------------\n")
            print(e)
            self.rollback()
            return False


        #mogiregisterの更新
        for row in self.stable.itertuples():
            if row.is_regi is True:
                try:
                    sql = f"update mogiregister set rate = {row.new_mr} where d_id = {row.player_id};"
                    self.query(sql)
                    self.commit()
                except Exception as e:
                    print("update_mogiregister")
                    print("----------------rollback------------------\n")
                    print(e)
                    self.rollback()
                    return False
        return True



    def __enter__(self):
        self.open()
        return self



    def __exit__(self, exctype, excvalue, traceback):
        if self.is_finish:
            #データの引っ越しはfinishが担当
            #ここではデータベース情報の破棄
            try:
                sql =f"delete from sa_cur where id = {self.ev_id};"
                self.query(sql)
                self.commit()
            except Exception as e:
                print("----------------rollback------------------")
                print(e)
                self.rollback()
            print("sa _ended")

            if self.is_cancel:
                try:
                    sql =f"delete from all_sa where ev_id = {self.ev_id};"
                    self.query(sql)
                    self.commit()
                except Exception as e:
                    print("----------------rollback------------------")
                    print(e)
                    self.rollback()
                print("sa _cancelled")

        else:
            #sa_cur更新
            try:
                dat = {
                   "id":self.ev_id,
                   "start":self.start,
                   "end":self.end,
                   "chan_id":self.chan_id,
                   "h_song1": self.hsongs[0],
                   "h_song2": self.hsongs[1],
                   "l_song1": self.lsongs[0],
                   "l_song2": self.lsongs[1],
                   "p_amount": self.p_amount,
                   "ph_amount": self.ph_amount,
                   "pl_amount": self.pl_amount
                }

                self.set("sa_cur",dat)
                self.commit()

            except Exception as e:
                print("----------------rollback------------------")
                print("mogi_con_close")
                print(e)
                self.rollback()

            #all_sa更新
            try:
                for row in self.stable.itertuples():
                    if row.id != -1:
                        dat = {
                            "id":row.id,
                            "ev_id":row.ev_id,
                            "start":self.start,
                            "end":self.end,
                            "p_amount":self.p_amount,
                            "p_rank":row.p_rank,
                            "player_id":row.player_id,
                            "score":row.score,
                            "player_maxrate":row.player_maxrate,
                            "player_mr":row.player_mr,
                            "new_mr":row.new_mr,
                            "assign":row.assign
                        }
                        self.set("all_sa",dat)
                    else:
                        dat = {
                            "ev_id":row.ev_id,
                            "start":self.start,
                            "end":self.end,
                            "p_amount":self.p_amount,
                            "p_rank":row.p_rank,
                            "player_id":row.player_id,
                            "score":row.score,
                            "player_maxrate":row.player_maxrate,
                            "player_mr":row.player_mr,
                            "new_mr":row.new_mr,
                            "assign":row.assign
                        }
                        self.set("all_sa",dat)
                
                self.commit()

            except Exception as e:
                print("----------------rollback------------------")
                print(e)
                self.rollback()
            print("sa _update")


        self.close()

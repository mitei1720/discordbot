import pandas as pd
from typing import Tuple
import settings
from . import db_util as du
from . import music_util as mu
import random
import discord
import datetime as dt
import numpy as np
import math
from typing import Optional, Union


#なぜかわからないけどこれで動く
#内部にDBをおいてた時の残骸、気にしなくてよい
DATABASE = "./DB/Randombase.db"


#   cur_2v2        全2v2mogi情報
#   カラム名
#       id              PRIMARY KEY
#       start           イベント開始日時
#       end             イベント終了日時
#       chan_id         使用したチャンネルid
#       song1           課題曲1のid             "_"で初期化
#       song2           課題曲2のid
#       song3           課題曲3のid
#       player_id[0-3]  参加者のid情報         0で初期化
#       player_team[0-3]参加者の所属team       0で初期化→[1,2]振り分け
#       pl1_score[0-3]  参加者のスコア(課題曲1) 0で初期化
#       pl2_score[0-3]  参加者のスコア(課題曲2) 0で初期化
#       pl3_score[0-3]  参加者のスコア(課題曲3) 0で初期化  
#       new_mr[0-3]     参加者の新MR


#   all_2v2        全2v2mogi情報
#   カラム名
#       id              PRIMARY KEY
#       start           イベント開始日時
#       end             イベント終了日時
#       song1           課題曲1のid
#       song2           課題曲2のid
#       song3           課題曲3のid
#       player_id[0-3]  参加者のid情報
#       player_team[0-3]参加者の所属team       0で初期化→[1,2]振り分け
#       pl1_score[0-3]  参加者のスコア(課題曲1)
#       pl2_score[0-3]  参加者のスコア(課題曲2)   
#       pl3_score[0-3]  参加者のスコア(課題曲3)   
#       new_mr[0-3]     参加者の新MR
#       season          行われたシーズン


#   mogiregister    mogi情報登録
#   カラム名
#       id              PRIMARY KEY
#       username        登録したusername
#       playername      スコアタに提出用のプレイヤーネーム
#       d_id            discord_ID
#       register_date   登録日時
#       maxrate         最後に登録されたmaxrate
#       rate            股濡レート

#debugged
def is_on_mogi(chan_id:discord.Interaction.channel_id)->bool:
    with du.DBwrapper(DATABASE) as db:
        dat = {"chan_id":chan_id}
        rows = db.count("cur_2v2",dat)
        if rows == 1:
            return True
        else:
            return False


#debugged
def id_to_username(user_id:int) -> Union[str,None]:
    username = None
    with du.DBwrapper(DATABASE) as db:
        dat = {"d_id":user_id}
        for row in db.get("mogiregister",dat):
            username = row["username"]
    
    return username


def username_to_id(username:str) -> Union[int,None]:
    uid = None
    with du.DBwrapper(DATABASE) as db:
        dat = {"username":username}
        for row in db.get("mogiregister",dat):
            uid = row["d_id"]
        
    return uid
    
            
        

#Debugged
def init_all() -> int:
    with du.DBwrapper(DATABASE) as db:
       
        #debugged
        table_sql = "show tables;"
        db.query(table_sql)
        tables = db.cursor.fetchall()
        print(tables)
        
        
        try:
            for table in tables:
                if(table[0] != "all_music"):
                    db.cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
            db.commit()
        except Exception as e:
            print("----------------rollback------------------\n")
            print("table delete")
            print(e)
            db.rollback()
        sql_r = """
            CREATE TABLE if not exists mogiregister
        (
            id INTEGER AUTO_INCREMENT,
            username TEXT,
            playername TEXT,
            d_id BIGINT,
            register_date TEXT,
            maxrate REAL,
            rate INTEGER,
            PRIMARY KEY(id)
        );
            """
        db.query(sql_r)
        sql = """
            CREATE TABLE if not exists cur_2v2
        (
            id INTEGER AUTO_INCREMENT,
            start TEXT,
            end TEXT,
            chan_id BIGINT,
            song1 TEXT,
            song2 TEXT,
            song3 TEXT,
            player_id0 BIGINT,
            player_id1 BIGINT,
            player_id2 BIGINT,
            player_id3 BIGINT,
            player_team0 INTEGER,
            player_team1 INTEGER,
            player_team2 INTEGER,
            player_team3 INTEGER,
            pl1_score0 INTEGER,
            pl1_score1 INTEGER,
            pl1_score2 INTEGER,
            pl1_score3 INTEGER,
            pl2_score0 INTEGER,
            pl2_score1 INTEGER,
            pl2_score2 INTEGER,
            pl2_score3 INTEGER,
            pl3_score0 INTEGER,
            pl3_score1 INTEGER,
            pl3_score2 INTEGER,
            pl3_score3 INTEGER,
            new_mr0 INTEGER,
            new_mr1 INTEGER,
            new_mr2 INTEGER,
            new_mr3 INTEGER,
            PRIMARY KEY(id)
        );
            """
        db.query(sql)
        sql1 = """
            CREATE TABLE if not exists all_2v2
        (
            id INTEGER AUTO_INCREMENT,
            start TEXT,
            end TEXT,
            song1 TEXT,
            song2 TEXT,
            song3 TEXT,
            player_id0 BIGINT,
            player_id1 BIGINT,
            player_id2 BIGINT,
            player_id3 BIGINT,
            player_team0 INTEGER,
            player_team1 INTEGER,
            player_team2 INTEGER,
            player_team3 INTEGER,
            pl1_score0 INTEGER,
            pl1_score1 INTEGER,
            pl1_score2 INTEGER,
            pl1_score3 INTEGER,
            pl2_score0 INTEGER,
            pl2_score1 INTEGER,
            pl2_score2 INTEGER,
            pl2_score3 INTEGER,
            pl3_score0 INTEGER,
            pl3_score1 INTEGER,
            pl3_score2 INTEGER,
            pl3_score3 INTEGER,
            new_mr0 INTEGER,
            new_mr1 INTEGER,
            new_mr2 INTEGER,
            new_mr3 INTEGER,
            season INTEGER,
            PRIMARY KEY(id)
        );
            """
        db.query(sql1)
        sql2 = """
            CREATE TABLE if not exists all_sa
        (
            id INTEGER AUTO_INCREMENT,
            ev_id INTEGER,
            start TEXT,
            end TEXT,
            p_amount INTEGER,
            p_rank INTEGER,
            player_id BIGINT,
            score INTEGER,
            player_maxrate REAL,
            player_mr INTEGER,
            new_mr INTEGER,
            assign TEXT,
            PRIMARY KEY(id)
        );
            """
        db.query(sql2)
        sql3 = """
            CREATE TABLE if not exists sa_info
        (
            ev_id INTEGER AUTO_INCREMENT,
            start TEXT,
            end TEXT,
            chan_id BIGINT,
            h_song1 TEXT,
            h_song2 TEXT,
            l_song1 TEXT,
            l_song2 TEXT,
            p_amount INTEGER,
            ph_amount INTEGER,
            pl_amount INTEGER,
            PRIMARY KEY(ev_id)
        );
            """
        db.query(sql3)
        sql4 = """
            CREATE TABLE if not exists sa_cur
        (
            id INTEGER AUTO_INCREMENT,
            start TEXT,
            end TEXT,
            chan_id BIGINT,
            h_song1 TEXT,
            h_song2 TEXT,
            l_song1 TEXT,
            l_song2 TEXT,
            p_amount INTEGER,
            ph_amount INTEGER,
            pl_amount INTEGER,
            PRIMARY KEY(id)
        );
            """
        db.query(sql4)
        dat =  {"season":0}
        db.set("all_2v2",dat)
        db.commit()
        return 0


#Debugged
#模擬シーズンの変更
def init_season()->int:
    """
    新しいmogiシーズンを始める関数
    返り値int -> 新しいシーズン番号
    """
    with du.DBwrapper(DATABASE) as db:
        db.cursor.execute("DROP TABLE IF EXISTS cur_2v2")
        db.connection.commit()
        sql = """
            CREATE TABLE if not exists cur_2v2
        (
            id INTEGER AUTO_INCREMENT,
            start TEXT,
            end TEXT,
            chan_id BIGINT,
            song1 TEXT,
            song2 TEXT,
            song3 TEXT,
            player_id0 BIGINT,
            player_id1 BIGINT,
            player_id2 BIGINT,
            player_id3 BIGINT,
            player_team0 INTEGER,
            player_team1 INTEGER,
            player_team2 INTEGER,
            player_team3 INTEGER,
            pl1_score0 INTEGER,
            pl1_score1 INTEGER,
            pl1_score2 INTEGER,
            pl1_score3 INTEGER,
            pl2_score0 INTEGER,
            pl2_score1 INTEGER,
            pl2_score2 INTEGER,
            pl2_score3 INTEGER,
            pl3_score0 INTEGER,
            pl3_score1 INTEGER,
            pl3_score2 INTEGER,
            pl3_score3 INTEGER,
            new_mr0 INTEGER,
            new_mr1 INTEGER,
            new_mr2 INTEGER,
            new_mr3 INTEGER,
            PRIMARY KEY(id)
        );
            """
        db.query(sql)
        #ここにrateの初期化処理を入れる------------------------------------------------------


        #----------------------------------------------------------------------------------
        db.commit()
        rows = db.get("all_2v2",{"id":1})
        season_a = 0
        for row in rows:
            season_b = row["season"]
            season_a = season_b + 1
            print(season_a)
            db.set("all_2v2",{"id":1,"season":season_a})
        
        db.commit()
        return season_a


#debugged            
#mogi情報にプレイヤーを登録する        
def player_register(username:str,user_id:discord.User.id,maxrate:float) -> Tuple[bool,int]:
    """
    player 登録関数
    username: playerが登録したい名前(str)
    user_id: Discordのユーザid(int)
    maxrate: playerが申告したmaxrate(float)

    返り値 bool
    成功 → True
    失敗 → False

    返り値 int
    初期レート

    """
    with du.DBwrapper(DATABASE) as db:
        #データベースに登録されているかチェック。
        dat = {"d_id":user_id}
        nm = db.count("mogiregister",dat)

        #同じusernameが使われていないかチェック
        dat = {"username":username}
        nn = db.count("mogiregister",dat)
        
        if nm == 0:
            if nn >= 1:
                return False,0

            #されていなかったら→　mogiregisterに登録。初期レートを計算,Player_historyを作る。
            #初期股濡レートの計算
            tmp_r = math.floor(maxrate)
            if tmp_r > 17:
                tmp_r = 17
            if tmp_r < 14:
                tmp_r = 14
            initrate = tmp_r * 1000

            #登録
            tmp_dt = dt.datetime.now()

            dat = {
                "username":username,
                "playername":"",
                "d_id":user_id,
                "register_date":tmp_dt.strftime('%Y/%m/%d %H:%M:%S.%f'),
                "maxrate":maxrate,
                "rate":initrate
                }
            
            try:
                db.set("mogiregister",dat)
                db.commit()

                #player historyの作成
                sql = f" CREATE TABLE if not exists Player_{user_id}_history (id INTEGER AUTO_INCREMENT, end TEXT,kind TEXT,ev_id INTEGER, new_mr INTEGER ,PRIMARY KEY(id));"
                db.query(sql)
                db.commit()
                return True, initrate
        
            except Exception as e:
                print(e)
                db.rollback()
                print("mogi_register------rollback")
                return False,0

        else:
            #されていたら→ False
            return False,0


#debugged
#mogi情報にプレイヤーを登録する        
def fix_player(username:str,user_id:discord.User.id,maxrate:float) -> bool:
    """
    player 登録関数
    username: playerが登録したい名前(str)
    user_id: Discordのユーザid(int)
    maxrate: playerが申告したmaxrate(float)

    返り値 bool
    成功 → True
    失敗 → False

    """
    with du.DBwrapper(DATABASE) as db:
        #データベースに登録されているかチェック。
        dat = {"d_id":user_id}
        nm = db.count("mogiregister",dat)

        if nm == 0:
            #されていなかったら→　False。
            return False

        else:
            #されていたら→ 更新
            
            try:
                sql = f"UPDATE mogiregister SET " 
                if(username is not None):
                    dat = {"username":username}
                    nn = db.count("mogiregister",dat)
                    if(nn >= 1):
                        return False
                    sql = sql + f"username = '{username}',"
                
                if(maxrate is not None):
                    sql = sql + f"maxrate = {maxrate} ,"
                
                sql = sql[:-1] + f"WHERE d_id = {user_id};"
                db.query(sql)
                db.commit()
                return True
        
            except Exception as e:
                db.rollback()
                print("fix_register------rollback")
                print(e)
                return False


class Mogi2v2(du.DBwrapper):
    #debgged
    def __init__(self,channel:discord.Interaction.channel_id,filePath:str = DATABASE,tablename:str = "cur_2v2"):
        """
        filePath    →データベースのディレクトリ
        tablename   →"cur_2v2"
        channel     →発信されたチャンネルid
        -----------------------------------
        
        """
        
        self.mogi_id = 0
        self.startdate = ""
        self.enddate = ""
        self.n_song = 0
        self.songs =[]
        self.chan_id = channel
        self.n_player=0
        self.players = []
        self.teams = []
        self.stable =  pd.DataFrame(columns = ["player_id","team","song1","song2","song3"])
        self.tablename = tablename
        self.winner = 0
        self.total1 = 0
        self.total2 = 0

        self.mrs = [-1,-1,-1,-1]

    

        #mogi新規登録時のみTrueにすること
        self.is_new = False

        #mogi終了時にはTrueにすること
        self.is_finish = False


        #データベースにアクセス
        super().__init__(filePath)
        

    #debugged
    def open(self):
        """
        Databaseを開いて現在模擬情報(cur_2v2)にアクセス。
        チャンネル idに模擬がなかったら模擬の開催を登録する。
        それ以外の場合はDatabaseから情報を持ってくる。
        """
        super().open()
        dat = {"chan_id":self.chan_id}
        nmogi = self.count(self.tablename,dat)
        if nmogi == 1:
            #もし模擬データがあった場合はデータを取り寄せる
            for row in self.get(self.tablename,dat):
           
                self.mogi_id = row["id"]
                self.startdate = row["start"]
                self.enddate = row["end"]
                self.songs.append(row["song1"])
                if(row["song1"] != "_"):
                    self.n_song = 1
                self.songs.append(row["song2"])
                if(row["song2"] != "_"):
                    self.n_song = 2
                self.songs.append(row["song3"])
                if(row["song3"] != "_"):
                    self.n_song = 3


                #player処理
                for i,player in enumerate([row["player_id0"],row["player_id1"],row["player_id2"],row["player_id3"]]):
                    self.players.append(player)
                    if player != 0:
                        self.n_player = i + 1

                #teams処理
                for team in [row["player_team0"],row["player_team1"],row["player_team2"],row["player_team3"]]:
                    self.teams.append(team)


                #score処理
                for i,player in enumerate([row["player_id0"],row["player_id1"],row["player_id2"],row["player_id3"]]):
                    self.stable.loc[str(i)] = [self.players[i],self.teams[i],row["pl1_score"+str(i)],row["pl2_score"+str(i)],row["pl3_score"+str(i)]]


                #MR取得処理
                for i,player in enumerate(self.players):
                    dat = {"d_id":player}
                    prows = self.get("mogiregister",dat)
                    for prow in prows:
                        self.mrs[i] = prow["rate"]
                  
                        




        elif nmogi == 0:
            #模擬データがない場合は作成->データベースに突っ込む
            self.is_new = True
            tmp_dt = dt.datetime.now()
            self.startdate = tmp_dt.strftime('%Y/%m/%d %H:%M:%S.%f')
            self.enddate = (tmp_dt + dt.timedelta(days = 1)).strftime('%Y/%m/%d %H:%M:%S.%f')
            self.players = [0,0,0,0]
            self.songs = ["_","_","_"]
            self.teams = [0,0,0,0]
            self.n_song = 0
            dat = {"start":self.startdate,
                   "end":self.enddate,
                   "chan_id":self.chan_id,
                   "song1":self.songs[0],
                   "song2":self.songs[1],
                   "song3":self.songs[2],
                   "player_id0":0,
                   "player_id1":0,
                   "player_id2":0,
                   "player_id3":0,
                   "player_team0":0,
                   "player_team1":0,
                   "player_team2":0,
                   "player_team3":0,
                   "pl1_score0":0,
                   "pl1_score1":0,
                   "pl1_score2":0,
                   "pl1_score3":0,
                   "pl2_score0":0,
                   "pl2_score1":0,
                   "pl2_score2":0,
                   "pl2_score3":0,
                   "pl3_score0":0,
                   "pl3_score1":0,
                   "pl3_score2":0,
                   "pl3_score3":0,
                   "new_mr0":0,
                   "new_mr1":0,
                   "new_mr2":0,
                   "new_mr3":0
                   }
            try:
                self.set(self.tablename,dat)
                self.commit()
                tmpm = self.get(self.tablename,{"chan_id":self.chan_id})
                for tmp in tmpm:
                    self.mogi_id = tmp["id"]
                
            except Exception as e:
                print("----------------rollback------------------\n")
                print("make new mogi")
                print(e)
                self.rollback()
        else:
            print("error--      Check Database")

    #debugged
    #課題曲登録
    def register_song(self,song_id) -> bool:
        """
        mogiの課題曲を登録する関数
        song_id -> プレイヤーが提示した曲のsong_id
        返り値 ->成功したらTrue
        """
        if self.n_song >= 3:
            return False
        
        elif self.n_song == 0:
            self.songs[0] = song_id
            self.n_song += 1
            return True
        
        elif self.n_song == 1:
            self.songs[1] = song_id
            self.n_song += 1
            return True
        
        else:
            self.songs[2] = song_id
            self.n_song += 1
            return True



    #課題曲リストを返す関数
    def get_songs(self)-> Tuple[int,list]:
        """
        返り値 → 登録された曲数,課題曲リスト

        課題曲リスト-----
        いる場合はMusic_data
        いない場合は"_"
        --------------------
        """
        mdatalist = []
        for song in self.songs:
            for row in self.get("all_music",{"meta_id":song}):
                mdatalist.append(mu.Music_data(row["meta_id"],row["meta_title"],row["meta_artist"],row["meta_genre"],row["diff"],row["level"],row["const"]))

        return self.n_song,mdatalist
    
    
    #debugged
    #playerlist,teamlist,mrlistを返す関数
    def get_players(self)-> Tuple[list,list,list,list]:
        """
        返り値 → usernamelist,プレイヤーリスト,チームリスト,MRリスト

        usernamelist-------
        いる場合はusername
        いない場合は""
        -------------------

        プレイヤーリスト-----
        いる場合はd_id
        いない場合は0
        --------------------
        チームリスト-----
        いる場合は {1,2}
        いない場合は0
        --------------------
        MRリスト-----
        いる場合は MR(int)
        いない場合は-1
        """
        usernamelist = ["","","",""]
        for i ,player in enumerate(self.players):
            if(player != 0):
                for row in self.get("mogiregister",{"d_id":player}):
                    usernamelist[i] = row["username"]


        return usernamelist,self.players,self.teams,self.mrs

    #debugged
    #score登録関数
    def register_score(self,d_id,song_id,score)->bool:
        """
        曲のスコア登録
        d_id:       playerのDiscordID
        song_id:    課題曲ID
        score:      登録されたスコア
        """
        
        if d_id in self.players:
            #何番目に登録された人か
            tmpin = self.players.index(d_id)
            if song_id in self.songs:
                #何番目に登録された曲か
                tmp = self.songs.index(song_id) + 1
                self.stable.at[str(tmpin),"song"+str(tmp)] = score
                return True
            else:
                return False

        else:
            return False

    #debugged
    #チーム決め
    def register_teams(self)->bool:
        """
        登録されたプレイヤーからランダムにチームを決定する
        成功 -> True
        失敗 -> False
        """
        if self.n_player != 4:
            return False
        else:
            l = [0,1,2,3]
            random.shuffle(l)
            self.teams[l[0]] = 1
            self.teams[l[1]] = 1
            self.teams[l[2]] = 2
            self.teams[l[3]] = 2

            self.stable.at[str(l[0]),"team"] = 1
            self.stable.at[str(l[1]),"team"] = 1
            self.stable.at[str(l[2]),"team"] = 2
            self.stable.at[str(l[3]),"team"] = 2
            return True


    #debugged
    def cancel_mogi(self) ->bool:
        """
        mogiキャンセル関数、カレントデータベースからの削除
        """
        self.is_finish = True
        return True
        

    #MOGI終了処理。ここではデータベースと値の計算のみ扱う
    def finish(self) -> bool:
        """
        mogi終了時処理
        返り値bool 成功->True
        """
        self.is_finish = True
        #勝ち負け処理
        
        df_result = self.stable.groupby('team').sum()
        print(df_result)
        self.total1 = df_result.at[1,"song1"] + df_result.at[1,"song2"] + df_result.at[1,"song3"]
        self.total2 = df_result.at[2,"song1"] + df_result.at[2,"song2"] + df_result.at[2,"song3"]

        if self.total2 > self.total1:
            self.winner = 2
        elif self.total2 < self.total1:
            self.winner = 1 

        #new MR 計算
        inpoints = [0,0,0,0]
        if self.winner != 0:
            for i,player in enumerate(self.teams):
                if player == self.winner:
                    inpoints[i] = 40
                else:
                    inpoints[i] = 10
        else:
            inpoints = [25,25,25,25]

        
        team1_mr = 0
        team2_mr = 0
        for i in range(0,4):
            if(self.teams[i] == 1):
                team1_mr += self.mrs[i]
            else:
                team2_mr += self.mrs[i]


        #レート格差補正
        for i in range(0,4):
            if(self.teams[i] == 1):
                inpoints[i] = round(inpoints[i] * (team2_mr / team1_mr)**4)
            else:
                inpoints[i] = round(inpoints[i] * (team1_mr / team2_mr)**4)

        #出来栄え補正
        
        for i in range(0,4):
            for j,song in enumerate(self.songs):
                glist = mu.get_score_goals(song[:-2],song[-1].lower(),self.mrs[i])
                if(self.stable.at[str(i),"song"+str(j+1)] < glist[0]):
                    inpoints[i] -= 2
                elif(self.stable.at[str(i),"song"+str(j+1)] > glist[2]):
                    inpoints[i] += 2
                else:
                    inpoints[i] += 1
                    
        
        #レート変動
        inpoints_sum = sum(inpoints)
        mr_delta = [-600,-600,-600,-600]
        for  i in range(0,4):
            mr_delta[i] += round(2400 * (inpoints[i]/inpoints_sum))
            if self.teams[i] == self.winner and mr_delta[i] <= 0:
                mr_delta[i] = 10
            self.mrs[i] += mr_delta[i]
            try:
                sql = f"UPDATE cur_2v2 SET new_mr0 = {self.mrs[0]} , new_mr1 = {self.mrs[1]} , new_mr2 = {self.mrs[2]} , new_mr3 = {self.mrs[3]} where id = {self.mogi_id};"
                self.query(sql)
                self.commit()
            except Exception as e:
                print("put_new_mr")
                print("----------------rollback------------------\n")
                print(e)
                self.rollback()
                return False

        

        #データ移行 cur_2v2 -> all_2v2
        
        row = {}
        for trow in self.get("cur_2v2",{"id":self.mogi_id}):
            row = trow
            season = 0
            for s_tmp in self.get("all_2v2",{"id":1}):
                season = s_tmp["season"]
        row["season"] = season
        row.pop("id")
        row.pop("chan_id")
        try:
            self.set("all_2v2",row)
            self.commit()

        except Exception as e:
            print("move_data")
            print("----------------rollback------------------\n")
            print(e)
            self.rollback()
            return False


        #player_historyの登録
        try:
            lastdata = self.cursor.execute("SELECT * FROM all_2v2 WHERE rowid = last_insert_rowid()").fetchall()
        except Exception as e:
            print("get_latest_index")
            print("----------------rollback------------------\n")
            print(e)
            self.rollback()
            return False
        
        latest_mogi_id = lastdata[0][0]
        try:
            for i,player in enumerate(self.players):
                dat = {"end":row["end"],"kind":"2v2","ev_id":latest_mogi_id,"new_mr":row["new_mr"+str(i)]}
                self.set("Player_"+str(player)+"_history",dat)
            self.commit()
        except Exception as e:
            print("add_history")
            print("----------------rollback------------------\n")
            print(e)
            self.rollback()
            return False

        #mogiregisterの更新
        for i in range(0,4):
            try:
                sql = f"update mogiregister set rate = {self.mrs[i]} where d_id = {self.players[i]};"
                self.query(sql)
                self.commit()
            except Exception as e:
                print("update_mogiregister")
                print("----------------rollback------------------\n")
                print(e)
                self.rollback()
                return False
        return True
        
        
    #debugged
    #player登録
    def player_add(self,user:discord.Interaction.user) -> bool:
        """
        mogi権限を持つユーザを対象とした関数
        """
        if self.n_player < 4:
            self.players[self.n_player] = user.id
            self.stable.at[str(self.n_player),"player_id"] = user.id
            for pl in self.get("mogiregister",{"d_id":user.id}):
                self.mrs[self.n_player] = pl["rate"]
            
            self.n_player += 1
            return True
        else:
            return False
        
    
    #with構文でデータベースを開く、mogiに関するコマンドが打たれたらデータベースから引っこ抜いてくる。
    #debugged
    def __enter__(self):
        self.open()
        return self
    
    #debugged
    def __exit__(self, exctype, excvalue, traceback):
        if self.is_finish:
            #all_2v2のデータ移行はfinishが担当してる
            #データベース情報の破棄
            try:
                print("delte"+str(self.mogi_id))
                sql =f"delete from cur_2v2 where id = {self.mogi_id};"
                self.query(sql)
                self.commit()
            except Exception as e:
                print("----------------rollback------------------")
                print(e)
                self.rollback()
            print("mogi _ended")
        else:
            #ここで変更を保存する
            try:
                dat =  {
                   "id": self.mogi_id, 
                   "start":self.startdate,
                   "end":self.enddate,
                   "chan_id":self.chan_id,
                   "song1":self.songs[0],
                   "song2":self.songs[1],
                   "song3":self.songs[2],
                   "player_id0":self.players[0],
                   "player_id1":self.players[1],
                   "player_id2":self.players[2],
                   "player_id3":self.players[3],
                   "player_team0":self.teams[0],
                   "player_team1":self.teams[1],
                   "player_team2":self.teams[2],
                   "player_team3":self.teams[3],
                   "pl1_score0":self.stable.at["0","song1"],
                   "pl1_score1":self.stable.at["1","song1"],
                   "pl1_score2":self.stable.at["2","song1"],
                   "pl1_score3":self.stable.at["3","song1"],
                   "pl2_score0":self.stable.at["0","song2"],
                   "pl2_score1":self.stable.at["1","song2"],
                   "pl2_score2":self.stable.at["2","song2"],
                   "pl2_score3":self.stable.at["3","song2"],
                   "pl3_score0":self.stable.at["0","song3"],
                   "pl3_score1":self.stable.at["1","song3"],
                   "pl3_score2":self.stable.at["2","song3"],
                   "pl3_score3":self.stable.at["3","song3"],
                   "new_mr0":0,
                   "new_mr1":0,
                   "new_mr2":0,
                   "new_mr3":0
                   }
                self.set(self.tablename,dat)
                self.commit()
            except Exception as e:
                print("----------------rollback------------------")
                print("mogi_con_close")
                print(e)
                self.rollback()
            print("mogi _connection_closed")    
        self.close()


        





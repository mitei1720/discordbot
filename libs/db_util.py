import pymysql
import pandas as pd
import os
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.types import Float,Integer,String,Text,BigInteger
import settings



#データベースのtable名
#   all_music   chunithm全曲データ(WE除く)
#   カラム名[確定]
#       meta_id,           --->"meta_id"_難易度頭文字大文字
#       meta_title,
#       meta_genre,
#       meta_artist,
#       meta_release,
#       meta_bpm,
#       diff,              ---> 難易度 BAS.ADV.EXP,MAS,ULT
#       level,
#       const,             ---> 譜面定数
#       maxcombo,
#       is_const_unknown,  ---> 譜面定数がわかってないとき,それ以外0
#       
#
#   mogiregister    mogi情報登録
#   カラム名
#       id              PRIMARY KEY
#       username        登録したusername
#       playername      スコアタに提出用のプレイヤーネーム
#       d_id            discord_ID
#       register_date   登録日時
#       maxrate         最後に登録されたmaxrate
#       rate            股濡レート
#
#
#   all_sa        全スコアタ情報
#   カラム名
#       id              PRIMARY KEY
#       ev_id           スコアタ識別ID  (sa_infoを連携)
#       start           イベント開始日時
#       end             イベント終了日時
#       p_amount        プレイヤー参加数
#       p_rank          順位           -1で初期化          
#       player_id       プレイヤーID    
#       score           スコア 0で初期化     
#       player_maxrate  プレイヤーのレート最高到達点    未登録は-1
#       player_mr       プレイヤーのMR  未登録は-1　   登録はplayerのmrで初期化(終了時のMRをもう一度取得忘れずに!)
#       new_mr          スコアタ後のMR  未登録は-1 
#       assign          取り組んだ課題種別 ["l","h","yet"]　"yet"で初期化
#       
#       
#       
#
#   all_2v2        全2v2mogi情報
#   カラム名
#       id              PRIMARY KEY
#       start           イベント開始日時
#       end             イベント終了日時
#       song1           課題曲1のid
#       song2           課題曲2のid
#       song3           課題曲3のid
#       player_id[0-3]  参加者のid情報
#       pl1_score[0-3]  参加者のスコア(課題曲1)
#       pl2_score[0-3]  参加者のスコア(課題曲2)   
#       pl3_score[0-3]  参加者のスコア(課題曲3)   
#       new_mr[0-3]     参加者の新MR



#   sa_info        過去のスコアタ情報
#   カラム名
#       ev_id           PRIMARY KEY(cur_saのIDを継ぐ)
#       start           イベント開始日時
#       end             イベント終了日時
#       chan_id         使用したチャンネルid
#       h_song1         高課題曲1のid "_"で初期化
#       h_song2         高課題曲2のid
#       l_song1         低課題曲1のid
#       l_song2         低課題曲2のid
#       p_amount        イベント参加者 0で初期化
#       ph_amount       高難易度提出数　
#       pl_amount       低難易度提出数
#       
#   sa_cur        現在のスコアタ情報
#   カラム名
#       id              PRIMARY KEY
#       start           イベント開始日時
#       end             イベント終了日時
#       chan_id         使用したチャンネルid
#       h_song1         高課題曲1のid　"_"で初期化
#       h_song2         高課題曲2のid
#       l_song1         低課題曲1のid
#       l_song2         低課題曲2のid
#       p_amount        イベント参加者　0で初期化
#       ph_amount       高難易度提出数
#       pl_amount       低難易度提出数
#
#   cur_2v2        全2v2mogi情報
#   カラム名[確定]
#       id              PRIMARY KEY
#       start           イベント開始日時
#       end             イベント終了日時
#       chan_id         使用したチャンネルid
#       song1           課題曲1のid
#       song2           課題曲2のid
#       song3           課題曲3のid
#       player_id[0-3]  参加者のid情報
#       player_team[0-3]参加者の所属team       0で初期化→[1,2]振り分け
#       pl1_score[0-3]  参加者のスコア(課題曲1)
#       pl2_score[0-3]  参加者のスコア(課題曲2)   
#       pl3_score[0-3]  参加者のスコア(課題曲3)   
#       new_mr[0-3]     参加者の新MR
#
#
#
#
#   Player_[id]_history 
#   カラム名
#       id              PrimaryKey
#       end             イベント終了日時
#       kind            イベント種別(fix,sa,2v2)            
#       ev_id           イベントid
#       new_mr          新MR          



#filePath ->内部にDBをおいてた時の残骸。気にしなくてよい。（外部DBにしてから使っていない）

class DB:
    def __init__(self, filePath=None):
        self.filePath = filePath
        self.dbname = settings.SQL_DBNM

    def open(self, filePath=None):
        if filePath != None:
            self.filePath = filePath
            print("Successfully connect to"+filePath)            
        self.connection = pymysql.connect(
            host=settings.SQL_HOST,
            user=settings.SQL_USER,
            port=settings.SQL_PORT,
            passwd=settings.SQL_PASS,
            db=settings.SQL_DBNM,
            charset='utf8'
        )
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def fetch(self, sql):
        self.cursor.execute(sql)
        for row in self.cursor:
            yield row

    def query(self, sql):
        self.cursor.execute(sql)

    def execute_query(self,sql):
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()


    #with構文でデータベースを開く想定
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exctype, excvalue, traceback):
        self.close()


class DBwrapper(DB):

    GET_TABLE_LIST_QUERY = "SELECT table_name,type FROM (SELECT table_name,table_schema,CASE table_type WHEN 'VIEW' THEN 'view' ELSE 'table' END AS type FROM information_schema.tables) t WHERE table_name LIKE '{0}' AND table_schema LIKE '{1}' AND type like '{2}'"
    GET_COLUMN_LIST_QUERY = "SELECT TABLE_NAME,COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME like LOWER('{0}') and TABLE_SCHEMA like LOWER('{1}') ORDER BY ORDINAL_POSITION"
    GET_ALTER_TABLE_QUERY = "ALTER TABLE {0} ADD {1}"
    GET_RENAME_TABLE_QUERY = "RENAME TABLE {0} TO {1}"


    def __init__(self, filePath=None):
        super().__init__(filePath)

    #debugged
    def set(self, tablename, args={}):
        """
        DBに値をセットする関数argsには入れる内容を辞書型で記入
        args = {カラム:内容, カラム:内容...}
        
        """
    
        if len(args) == 0:
            return False
        cols = list(args.keys())
        vals = []
        for col in cols:
            if type(args[col]) == str:
                vals.append("'%s'" % args[col])
            else:
                vals.append(str(args[col]))
        columns = ",".join(cols)
        values = ",".join(vals)
        sql = f"replace into {tablename} ({columns}) values ({values})"
        self.query(sql)
        return True,


    #danger  
    #to_sqlを使いたいのにエラーを吐くのでこの実装
    def set_from_pd(self, unidata:pd.DataFrame,tablename:str="all_music") -> None:
        """
        dfからDBにデータ移行
        """
        self.query("DROP TABLE IF EXISTS all_music")
        self.commit()
        sql = """
            CREATE TABLE if not exists all_music(
                id INTEGER AUTO_INCREMENT,
                meta_id TEXT,
                meta_title TEXT,
                meta_genre TEXT,
                meta_artist TEXT,
                meta_release TEXT,
                meta_bpm INTEGER,
                level REAL,
                const REAL,
                maxcombo REAL,
                is_const_unknown REAL,
                diff TEXT,
                PRIMARY KEY(id)
            )
        """
        self.query(sql)
        self.commit()

        #try:
        #    ind = 0
        #    for row in unidata.itertuples():
        #        dat = {
        #            "meta_id":          row.meta_id,
        #            "meta_title":       row.meta_title.replace("'","’"),
        #            "meta_genre":       row.meta_genre,
        #            "meta_artist":      row.meta_artist.replace("'","’"),
        #            "meta_release":     row.meta_release,
        #            "meta_bpm":         row.meta_bpm,
        #            "level":            row.level,
        #            "const":            row.const,
        #            "maxcombo":         row.maxcombo,
        #            "is_const_unknown": row.is_const_unknown,
        #            "diff":             row.diff
        #        }
        #        self.set("all_music",dat)
        #        if(ind == 20):
        #            break
        #        ind += 1
#
        #    
        #    self.commit()
        #except Exception as e:
        #    print("----------------rollback------------------\n")
        #    print("song_import")
        #    print(e)
        #    self.rollback()
        engine = create_engine(settings.SQL_URL)
        unidata.to_sql(tablename,con=engine,if_exists="append",index=False)
        #dtype={'meta_id': Text,
        #                                                                           "meta_title":Text,
        #                                                                           "meta_genre":Text,
        #                                                                           "meta_artist":Text,
        #                                                                           "meta_release":Text,
        #                                                                           "meta_bpm":Integer,
        #                                                                           "level":Float,
        #                                                                           "const":Float,
        #                                                                           "maxcombo":Float,
        #                                                                           "is_const_unknown":Float,
        #                                                                           "diff":Text}
        #        
    

    def get(self, tablename, args={}):
        """
        DBからデータを引っこ抜く.argsには抽出したい条件を辞書で記入
        args = {カラム:内容, カラム:内容...}
        例: 
        Xがhogeのカラム                 X:hoge
        1 <= X < 3のカラム              X:(1,3)
        XがhogeまたはYがhugaのカラム     "or":{X:hoge, Y:huga}
        """
        columns = self._getColumns(tablename)
        columnNames = ",".join(columns.keys())
        if len(args) > 0:
            wh = self._keyValue(args)
            sql = f"select {columnNames} from {tablename} where {' and '.join(wh)}"
        else:
            sql = f"select {columnNames} from {tablename}"
        print(sql)
        for row in self.fetch(sql):
            buf = {}
            for idx, col in enumerate(columns):
                buf[col] = row[idx]
            yield buf

    def del_table(self,tablename):
        self.cursor.execute(f"DROP TABLE IF EXISTS {tablename};")

    def get_all_table(self):
        self.cursor.execute("show tables")
        # 結果を取得
        tables = self.cursor.fetchall()
        # テーブルの一覧を表示
        tlist = []
        for table in tables:
            tlist.append(table[0])
        return tlist

    #danger
    def get_latest_id(self, tablename:str = None, id_column_name:str = None) -> int:
        
        sql = f"select max({id_column_name}) from {tablename}"
        row = self.fetch(sql)

        return row.__next__()[0]


    def count(self, tablename, args={}):
        if len(args) > 0:
            wh = self._keyValue(args)
            sql = f"select count(*) from {tablename} where {' and '.join(wh)}"
        else:
            sql = f"select count(*) from {tablename}"
        print(sql)
        row = self.fetch(sql)
        return row.__next__()[0]

    

    
    def _getColumns(self,tablename):
        '''
        指定したテーブルのカラムと型を一覧で取得する
        Parameters
        ----------
        tablename : str
            テーブル名
        Returns
        ----------
        res:str
            リスト形式でカラム名と型のタプルを返す
            <例>  [('column1','int'),('column2','text'),('column3',real)]
        '''
        res = self.execute_query(self.GET_COLUMN_LIST_QUERY.format(tablename,self.dbname))
        return {name[1]:name[2] for name in res}


    #debugged
    def _keyValue(self, args={}) -> str:
        keys = list(args.keys())
        wh = []
        for key in keys:
            if key == "like_ph":
                if not("like" in args[key]):
                    print("意図しない挙動です。該当箇所のargsのvalueはlikeを含むようにしてください。")
                    return None
                else:
                    wh.append("%s" % (args[key]))
            elif type(args[key]) == str:
                wh.append("%s = '%s'" % (key, args[key]))
            elif type(args[key]) == tuple:
                wh.append("(%s <= %s) and (%s <= %s)" % (args[key][0], key, key, args[key][1]))
            elif type(args[key]) == dict:
                if not("or" in key):
                    print("意図しない挙動です。該当箇所のargsのkeyはorを含むようにしてください。")
                    return None
                tmp =[]
                for akey,aitem in args[key].items():
                    if type(aitem) == str:
                        tmp.append("%s = '%s'" % (akey, aitem))
                    elif type(aitem) == tuple:
                        tmp.append("(%s <= %s) and (%s <= %s)" % (aitem[0], akey, akey, aitem[1]))
                    else:
                        tmp.append("%s = %s" % (akey, aitem))
                tmpsql = " or ".join(tmp)
                tmpsql = "(" + tmpsql + ")"
                wh.append(tmpsql)
            else:
                wh.append("%s = %s" % (key, args[key]))
        return wh





    

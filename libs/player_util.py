import discord
from . import db_util as du
from typing import Optional, Union
import datetime as dt



def get_mr(user:Union[str,int]) -> int:
    """
    UserID, Username -> MR

    ---
    登録されているプレイヤーならそのレートが
    されていないプレイヤーなら-1が返る。
    """
    if type(user) is int:
        rate = -1
        with du.DBwrapper() as db:
            dat = {"d_id":user}
            for row in db.get("mogiregister",dat):
                rate = row["rate"]

        return rate
    else:
        rate = -1
        with du.DBwrapper() as db:
            dat = {"username":user}
            for row in db.get("mogiregister",dat):
                rate = row["rate"]

        return rate

def fix(username:str, delta:int)-> bool:
    with du.DBwrapper() as db:
        tmp = []
        for row in db.get("mogiregister",{"username":username}):
            tmp.append(row)
        
        if len(tmp) != 1:
            return False
        
        id = tmp[0]["d_id"]
        crate = tmp[0]["rate"]

        playertable = "Player_"+str(id)+"_history"

        tmp_dt = dt.datetime.now()
        end = tmp_dt.strftime('%Y/%m/%d %H:%M:%S.%f')

        try:
            db.set(playertable,{
                "end":end,
                "kind":"fix",
                "ev_id":-1,
                "new_mr":crate+delta
            })
            db.commit()
            sql = f"update mogiregister set rate = {crate + delta} where d_id = {id};"
            db.query(sql)
            db.commit()
        
        except Exception as e:
            print("update_Playerhistory")
            print("----------------rollback------------------\n")
            print("update_mogiregister")
            print("----------------rollback------------------\n")
            print(e)
            db.rollback()
            return False
    
    return True

        
            
        
        



import pandas as pd
from typing import Tuple,Union
import settings
from . import db_util as du
import random
import discord

#なぜかわからないけどこれで動く
#内部にDBをおいてた時の残骸、気にしなくてよい
DATABASE = "./DB/Randombase.db"


class Todo(du.DBwrapper):
    def __init__(self):
        super().__init__(DATABASE)
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exctype, excvalue, traceback):
        self.close()
    
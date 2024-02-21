import sqlite3
import json 

class DB:
    def __init__(self, filePath=None):
        if filePath != None:
            self.filePath = filePath

    def open(self, filePath=None):
        if filePath != None:
            self.filePath = filePath
        self.connection = sqlite3.connect(self.filePath)
        self.cursor = self.connection.cursor()


    def close(self):
        self.cursor.close()
        self.connection.close()

    def fetch(self, sql):
        for row in self.cursor.execute(sql):
            yield row

    def query(self, sql):
        self.cursor.execute(sql)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exctype, excvalue, traceback):
        self.close()


class DBwrapper(DB):

    def set(self, tablename, args={}):
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
        return True

    def get(self, tablename, args={}):
        columns = self._getColumns(tablename)
        columnNames = ",".join(columns.keys())
        if len(args) > 0:
            wh = self._keyValue(args)
            sql = f"select {columnNames} from {tablename} where {' and '.join(wh)}"
        else:
            sql = f"select {columnNames} from {tablename}"
        for row in self.fetch(sql):
            buf = {}
            for idx, col in enumerate(columns):
                buf[col] = row[idx]
            yield buf

    def count(self, tablename, args={}):
        if len(args) > 0:
            wh = self._keyValue(args)
            sql = f"select count(*) from {tablename} where {' and '.join(wh)}"
        else:
            sql = f"select count(*) from {tablename}"
        row = self.fetch(sql)
        return row.__next__()[0]

    def _getColumns(self, tablename):
        sql = f"pragma table_info('{tablename}')"
        columns = {x[1]: x[2] for x in self.fetch(sql)}
        return columns

    def _keyValue(self, args={}):
        keys = list(args.keys())
        wh = []
        for key in keys:
            if type(args[key]) == str:
                wh.append("%s = '%s'" % (key, args[key]))
            else:
                wh.append("%s = %s" % (key, args[key]))
        return wh
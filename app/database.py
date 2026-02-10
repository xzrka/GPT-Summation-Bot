import sqlite3
import time
from datetime import datetime
from zoneinfo import ZoneInfo


# 유저 개별 데이터를 저장하는 DB

class user_db:
    def __init__(self, filename, tablename):
        self.conn = sqlite3.connect(filename)
        self.table_name = tablename
        self.create_db()
        
    def __del__(self):
        self.conn.close()

    def create_db(self):
        try:
            self.conn.execute(f'CREATE TABLE {self.table_name}(user_chat_id INTEGER, username TEXT, reserved_time TEXT, last_summation_timestamp INTEGER, target_chat_id INTEGER, insert_time TEXT, timestamp INTEGER)')
            self.conn.commit()
        except:
            pass

    def add_data_db(self, user_chat_id:str, username:str, reserved_time:str, last_summation_timestamp):
        cur = self.conn.cursor()
        cur.executemany(
            f'INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?, ?, ?)',
            [(user_chat_id, username, reserved_time, last_summation_timestamp, 0, datetime.fromtimestamp(time.time(), tz=ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S'), int(time.time() * 1000))]
        )#
        self.conn.commit()

    def getalldata_db_user(self, user_chat_id):
        """
            특정 유저의 모든 데이터를 가져오는 함수
        """
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {self.table_name} WHERE user_chat_id=?", (user_chat_id,))
        rows = cur.fetchall()
        return rows
    
    def getalldata_db(self):
        """
            모든 유저 데이터를 가져오는 함수
        """
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {self.table_name}")
        rows = cur.fetchall()
        return rows

    def get_data_db(self, user_chat_id):
        cur = self.conn.cursor()
        cur.execute(f'SELECT * FROM {self.table_name} WHERE user_chat_id=?', (user_chat_id,))
        return cur.fetchone()

    def delete_data_db(self, user_chat_id):
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM {self.table_name} WHERE user_chat_id=?", (user_chat_id,))
        self.conn.commit()
        

    def delete_all_db(self):
        excuted_num = (self.conn.execute(f"DELETE FROM {self.table_name}").rowcount)
        self.conn.commit()
        return excuted_num

    def update_data_db(self, user_chat_id, last_summation_timestamp):
        cur = self.conn.cursor()
        cur.execute(f"UPDATE {self.table_name} SET last_summation_timestamp=? WHERE user_chat_id=?", (last_summation_timestamp, user_chat_id,))
        self.conn.commit()

    def update_username_data_db(self, user_chat_id, username):
        cur = self.conn.cursor()
        cur.execute(f"UPDATE {self.table_name} SET username=? WHERE user_chat_id=?", (username, user_chat_id,))
        self.conn.commit()

    def update_target_chat_id_data_db(self, user_chat_id, target_chat_id):
        cur = self.conn.cursor()
        cur.execute(f"UPDATE {self.table_name} SET target_chat_id=? WHERE user_chat_id=?", (target_chat_id, user_chat_id,))
        self.conn.commit()


# 유저들이 구독한 채널을 저장하는 DB
class subscribe_db:
    def __init__(self, filename, tablename):
        self.conn = sqlite3.connect(filename)
        self.table_name = tablename
        self.create_db()
        
    def __del__(self):
        self.conn.close()

    def create_db(self):
        try:
            self.conn.execute(f'CREATE TABLE {self.table_name}(chat_id INTEGER, channel_link TEXT, insert_time TEXT, timestamp INTEGER)')
            self.conn.commit()
        except:
            pass

    def add_data_db(self, chat_id:str, channel_link:str):
        cur = self.conn.cursor()
        cur.executemany(
            f'INSERT INTO {self.table_name} VALUES (?, ?, ?, ?)',
            [(chat_id, channel_link, datetime.fromtimestamp(time.time(), tz=ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S'), int(time.time() * 1000))]
        )#
        self.conn.commit()

    def getalldata_db(self, chat_id):
        """
            특정 유저의 모든 데이터를 가져오는 함수
        """
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {self.table_name} WHERE chat_id=?", (chat_id,))
        rows = cur.fetchall()
        return rows
    
    def get_data_db(self, chat_id, channel_link):
        cur = self.conn.cursor()
        cur.execute(f'SELECT * FROM {self.table_name} WHERE chat_id=? AND channel_link=?', (chat_id, channel_link,))
        return cur.fetchone()

    def delete_data_db(self, chat_id, channel_link):
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM {self.table_name} WHERE chat_id=? AND channel_link=?", (chat_id, channel_link,))
        self.conn.commit()
        
    def delete_all_db(self):
        excuted_num = (self.conn.execute(f"DELETE FROM {self.table_name}").rowcount)
        self.conn.commit()
        return excuted_num

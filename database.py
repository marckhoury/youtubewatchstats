import sqlite3

sql_create_videos_table = """ CREATE TABLE IF NOT EXISTS videos (
                                        id text PRIMARY KEY,
                                        title text,
                                        duration text,
                                        valid integer 
                                    ); """ 

def create_connection(filename):
    conn = None
    try:
        conn = sqlite3.connect(filename)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn, sql_cmd=sql_create_videos_table):
    try:
        cursor = conn.cursor()
        cursor.execute(sql_cmd)
    except sqlite3.Error as e:
        print(e)

def create_video(conn, video):
    sql_cmd = ''' INSERT INTO videos(id,title,duration,valid) VALUES(?,?,?,?) '''
    cursor = conn.cursor()
    cursor.execute(sql_cmd, video)

def select_video(conn, vid):
    sql_cmd = '''SELECT * FROM videos WHERE id=?'''
    cursor = conn.cursor()
    cursor.execute(sql_cmd, (vid,))
    
    return cursor.fetchone()

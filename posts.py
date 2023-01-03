import datetime
import json
import logging
import sqlite3 as sl

logging.basicConfig(level=logging.INFO)

database = 'db/posts.db'


def create_database_and_tables():
    logging.debug("Setting up the database")
    with sl.connect(database) as conn:
        conn.execute("""
                CREATE TABLE IF NOT EXISTS RAOCPOSTS (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT NOT NULL,
                    author TEXT NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    mentioned_users_post TEXT,
                    multiple_mentions BINARY,
                    mystery_user BINARY,
                    timestamp REAL
                );
            """)
        # conn.execute("""
        #         CREATE TABLE IF NOT EXISTS HISTORICAL_DATA (
        #             variable TEXT NOT NULL PRIMARY KEY,
        #             value REAL
        #         );
        #     """)
        # conn.execute("INSERT OR IGNORE INTO HISTORICAL_DATA (variable, value) VALUES ('total_value', 0.0)")
        # conn.execute("INSERT OR IGNORE INTO HISTORICAL_DATA (variable, value) VALUES ('value_baseline', 0.0)")
        # conn.execute("INSERT OR IGNORE INTO HISTORICAL_DATA (variable, value) VALUES ('total_bought_sold', 0.0)")
        # conn.execute("INSERT OR IGNORE INTO HISTORICAL_DATA (variable, value) VALUES ('trigger_value', 0.0)")
        # conn.execute("INSERT OR IGNORE INTO HISTORICAL_DATA (variable, value) VALUES ('amount_to_sell', 0.0)")


def create_first_entry(post_id: str, author: str, title: str, url: str, timestamp: float):
    with sl.connect(database) as conn:
        data = conn.execute("SELECT post_id FROM RAOCPOSTS")
        post_found = False
        for row in data:
            if row[0] == post_id:
                post_found = True
                break

        if post_found:
            return post_id + " already present in database"

        sql = 'INSERT INTO RAOCPOSTS (post_id, author, title, url, timestamp) values(?, ?, ?, ?, ?)'
        data = [
            (post_id, author, title, url, timestamp)
        ]
        conn.executemany(sql, data)
        return "First entry for " + post_id + " created"


def insert_to_db(post_id: str, author: str, title: str, url: str, timestamp: float, mentioned_users_post: list,
                 mystery_user: bool, multiple_mentions: bool):
    with sl.connect(database) as conn:
        data = conn.execute("SELECT post_id FROM RAOCPOSTS")
        post_found = False
        for row in data:
            if row[0] == post_id:
                post_found = True
                break

        if post_found:
            return post_id + " already present in database"

        mentioned_users_post_json = json.dumps(mentioned_users_post)
        sql = 'INSERT INTO RAOCPOSTS (post_id, author, title, url, mentioned_users_post, multiple_mentions, mystery_user, timestamp) values(?, ?, ?, ?, ?, ?, ?, ?)'
        data = [
            (post_id, author, title, url, mentioned_users_post_json, multiple_mentions, mystery_user, timestamp)
        ]
        conn.executemany(sql, data)
        return post_id + " created"


def delete_entry(post_id: str):
    with sl.connect(database) as conn:
        conn.execute("DELETE FROM RAOCPOSTS WHERE post_id='" + post_id + "'")
        return post_id + " deleted"


def delete_old_entries():
    with sl.connect(database) as conn:
        data = conn.execute("SELECT post_id, timestamp FROM RAOCPOSTS")
        for row in data:
            if datetime.datetime.fromtimestamp(row[1]) < datetime.datetime.now() - datetime.timedelta(days=7):
                delete_entry(row[0])


def check_if_post_in_database(post_id: str):
    with sl.connect(database) as conn:
        data = conn.execute("SELECT post_id FROM RAOCPOSTS")
        post_found = False
        for row in data:
            if row[0] == post_id:
                post_found = True
                break
        return post_found


def get_posts():
    posts = {}
    with sl.connect(database) as conn:
        sql = "SELECT post_id, author, title, url, mentioned_users_post, multiple_mentions, mystery_user, timestamp FROM RAOCPOSTS ORDER BY timestamp DESC;"
        data = conn.execute(sql)
        for row in data:
            values = {
                "author": row[1],
                "title": row[2],
                "url": row[3],
                "mentioned_users_post": json.loads(row[4]),
                "multiple_mentions": row[5],
                "mystery_user": row[6],
                "timestamp": row[7]
            }
            posts[row[0]] = values

    return posts

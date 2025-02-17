import sqlite3

DB_NAME = "database.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            tg_id INTEGER UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS twitter_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            twitter_username TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE (twitter_username, user_id)  -- Уникальные Twitter-аккаунты для одного пользователя
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS following (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            twitter_username TEXT UNIQUE NOT NULL,
            following TEXT NOT NULL  -- JSON-строка с подписками
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()

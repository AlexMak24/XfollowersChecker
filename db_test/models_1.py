import sqlite3
import json
from twitter import get_twitter_followers
DB_NAME = "database.db"


class User:
    @staticmethod
    def add_user(username, tg_id):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (username, tg_id) VALUES (?, ?)", (username, tg_id))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id

    @staticmethod
    def get_user_id_by_tg_id(tg_id):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE tg_id = ?", (tg_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None  # Если пользователь найден — возвращаем user_id, иначе None

    @staticmethod
    def get_all_users():
        """Получить список всех пользователей из БД."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, tg_id FROM users")
        users = cursor.fetchall()  # Получаем всех пользователей
        conn.close()
        return [{"user_id": user[0], "username": user[1], "tg_id": user[2]} for user in users]

    @staticmethod
    def get_tg_id_by_user_id(user_id):
        """Получить tg_id по user_id."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT tg_id FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None  # Если пользователь найден — возвращаем tg_id, иначе None
class TwitterUser:
    @staticmethod
    def add_twitter_users_bulk(user_id, usernames):
        """Добавляет сразу несколько Twitter-аккаунтов в список пользователя (без дубликатов)."""
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Получаем уже существующих пользователей, чтобы не добавлять их дважды
        cursor.execute("SELECT twitter_username FROM twitter_users WHERE user_id = ?", (user_id,))
        existing_users = {row[0] for row in cursor.fetchall()}  # Множество существующих имен

        new_users = [(username, user_id) for username in usernames if username not in existing_users]

        if new_users:
            cursor.executemany("INSERT INTO twitter_users (twitter_username, user_id) VALUES (?, ?)", new_users)

        conn.commit()
        conn.close()

    @staticmethod
    def remove_twitter_users_bulk(user_id, usernames):
        """Удаляет список Twitter-аккаунтов у пользователя."""
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.executemany(
            "DELETE FROM twitter_users WHERE user_id = ? AND twitter_username = ?",
            [(user_id, username) for username in usernames]
        )

        conn.commit()
        conn.close()

    @staticmethod
    def clear_user_list(user_id):
        """Полностью очищает список подписок пользователя."""
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM twitter_users WHERE user_id = ?", (user_id,))

        conn.commit()
        conn.close()

    @staticmethod
    def get_user_following(user_id):
        """Получает список всех Twitter-аккаунтов, на которых подписан пользователь."""
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT twitter_username FROM twitter_users WHERE user_id = ?", (user_id,))
        following_list = [row[0] for row in cursor.fetchall()]

        conn.close()
        return following_list

    @staticmethod
    def get_user_ids_for_twitter_username(twitter_username):
        """Получает все user_id, которые подписаны на определенный twitter_username."""
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Выполняем SQL-запрос для получения всех user_id для указанного twitter_username
        cursor.execute("SELECT user_id FROM twitter_users WHERE twitter_username = ?", (twitter_username,))
        user_ids = [row[0] for row in cursor.fetchall()]

        conn.close()
        return user_ids

class Following:
    @staticmethod
    def add_following(twitter_username, following_list):
        """Добавляет пользователей в список подписок (following)."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT following FROM following WHERE twitter_username = ?", (twitter_username,))
        row = cursor.fetchone()


        if row:
            existing_following = set(json.loads(row[0]))
            updated_following = existing_following.union(set(following_list))
            cursor.execute("UPDATE following SET following = ? WHERE twitter_username = ?",
                           (json.dumps(list(updated_following)), twitter_username))
        else:
            cursor.execute("INSERT INTO following (twitter_username, following) VALUES (?, ?)",
                           (twitter_username, json.dumps(following_list)))

        conn.commit()
        conn.close()

    @staticmethod
    def remove_following(twitter_username, following_list):
        """Удаляет конкретных пользователей из списка подписок (following)."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT following FROM following WHERE twitter_username = ?", (twitter_username,))
        row = cursor.fetchone()

        if row:
            existing_following = set(json.loads(row[0]))
            updated_following = existing_following - set(following_list)
            cursor.execute("UPDATE following SET following = ? WHERE twitter_username = ?",
                           (json.dumps(list(updated_following)), twitter_username))

        conn.commit()
        conn.close()

    @staticmethod
    def clear_following(twitter_username):
        """Полностью очищает список подписок пользователя (following)."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM following WHERE twitter_username = ?", (twitter_username,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_following(twitter_username):
        """Возвращает список пользователей, на которых подписан данный Twitter-аккаунт."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT following FROM following WHERE twitter_username = ?", (twitter_username,))
        row = cursor.fetchone()
        conn.close()

        if row and row[0]:
            return json.loads(row[0])
        return []

    @staticmethod
    def get_followers(twitter_username):
        """Возвращает список пользователей, которые подписаны на данный Twitter-аккаунт."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT twitter_username FROM following WHERE following LIKE ?", (f'%"{twitter_username}"%',))
        followers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return followers
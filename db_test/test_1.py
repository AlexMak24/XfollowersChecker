import sqlite3
from db_1 import create_tables
from models_1 import User, TwitterUser, Following

def reset_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Проверим, что таблицы существуют
    cursor.execute("DROP TABLE IF EXISTS twitter_users")
    cursor.execute("DROP TABLE IF EXISTS following")
    cursor.execute("DROP TABLE IF EXISTS users")

    conn.commit()
    conn.close()

def run_tests():
    print("🔄 Пересоздаём базу данных...")
    reset_db()  # Удаляем старую БД
    create_tables()  # Создаём новую БД со структурой

    print("✅ Тест 1: Добавляем Telegram пользователей")
    vasya_id = User.add_user("Vasya", 12345)
    petya_id = User.add_user("Petya", 67890)
    huilo_id = User.add_user("Huilo", 4353534)
    print(f"Vasya ID: {vasya_id}, Petya ID: {petya_id}, Huilo ID: {huilo_id}")

    print("✅ Тест 2: Добавляем Twitter-аккаунты для пользователей")
    TwitterUser.add_twitter_users_bulk(vasya_id, ["elonmusk", "vitalikbuterin"])
    TwitterUser.add_twitter_users_bulk(huilo_id, ["elonmusk", "vitalikbuterin", "jamorant", "jessipinkman"])
    TwitterUser.add_twitter_users_bulk(petya_id, ["jamorant", "elonmusk"])

    print("🔍 Проверяем, что в БД есть Twitter-аккаунты:")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM twitter_users")
    print(cursor.fetchall())
    conn.close()

    print("✅ Тест 3: Добавляем подписки для Twitter-аккаунтов")
    Following.add_following("elonmusk", ["boba", "bibg", "bubga"])
    Following.add_following("vitalikbuterin", ["dfsafas", "sdfaf", "dsfafda"])
    Following.add_following("jamorant", ["dsffd", "bisgdfgsgfbg", "sggffsgf"])
    print("🔍 Проверяем подписки:")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM following")
    print(cursor.fetchall())
    conn.close()

    print("✅ Тест 4: Получаем список подписок пользователя")
    print("📌 Вася подписан на:", TwitterUser.get_user_following(vasya_id))
    print("📌 Петя подписан на:", TwitterUser.get_user_following(petya_id))
    print("📌 Хуило подписан на:", TwitterUser.get_user_following(huilo_id))

    print("✅ Тест 5: Добавляем новых людей в список Васи")
    TwitterUser.add_twitter_users_bulk(vasya_id, ["jamorant", "jessipinkman"])
    print("📌 Обновленный список Васи:", TwitterUser.get_user_following(vasya_id))

    print("✅ Тест 6: Удаляем из списка Васи 'elonmusk'")
    TwitterUser.remove_twitter_users_bulk(vasya_id, ["elonmusk"])
    print("📌 Список Васи после удаления 'elonmusk':", TwitterUser.get_user_following(vasya_id))

    print("✅ Тест 7: Полностью очищаем список Васи")
    TwitterUser.clear_user_list(vasya_id)
    print("📌 Список Васи после очистки:", TwitterUser.get_user_following(vasya_id))

    # 🔥 НОВЫЕ ТЕСТЫ ДЛЯ FOLLOWING 🔥

    print("✅ Тест 8: Добавляем подписчиков к 'elonmusk'")
    Following.add_following("elonmusk", ["glsdjglfsdjgflsjg", "new_fan2","new_fan3"])
    print("📌 Подписчики 'elonmusk':", Following.get_followers("elonmusk"))

    print("✅ Тест 9: Удаляем подписчика 'boba' у 'elonmusk'")
    Following.remove_following("elonmusk", ["new_fan2"])
    print("📌 Подписчики 'elonmusk' после удаления 'boba':", Following.get_followers("elonmusk"))

    print("✅ Тест 10: Полностью очищаем подписчиков у 'elonmusk'")
    #Following.clear_following("elonmusk")
    print("📌 Подписчики 'elonmusk' после очистки:", Following.get_followers("elonmusk"))

if __name__ == "__main__":
    run_tests()

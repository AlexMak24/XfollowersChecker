import telebot
import logging
import time
import threading
from db_test.models_1 import User, TwitterUser, Following  # Импортируем модель User из папки database
from db_test.db_1 import create_tables
from twitter import get_twitter_followers,get_twitter_handle_by_id
import requests
import re


API_TOKEN = ''

# Создаем объект бота
bot = telebot.TeleBot(API_TOKEN)

create_tables()
# Логирование
logging.basicConfig(level=logging.INFO)

def extract_username(url_or_username):
    match = re.search(r"(?:https?://)?(?:www\.)?(?:x\.com|twitter\.com)/([\w\d_]+)", url_or_username)
    return match.group(1) if match else url_or_username.strip()

def get_main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item_add = telebot.types.KeyboardButton("Добавить список")
    item_remove = telebot.types.KeyboardButton("Удалить список")
    item_show = telebot.types.KeyboardButton("Показать список подписок")
    item_remove_all = telebot.types.KeyboardButton("Удалить все подписки")
    item_check_followers = telebot.types.KeyboardButton("Проверить подписки")
    markup.add(item_add, item_remove, item_show, item_remove_all, item_check_followers)
    return markup


def send_message_with_retry( chat_id, text, retries=5, delay=5):
    for attempt in range(retries):
        try:
            bot.send_message(chat_id, text, reply_markup=get_main_menu())
            return  # Успешно отправлено
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Ошибка соединения: {e}. Попытка {attempt + 1} из {retries}")
            time.sleep(delay)
        except Exception as e:
            logging.error(f"Неизвестная ошибка при отправке сообщения: {e}")
            bot.send_message(chat_id, f"Неизвестная ошибка при отправке сообщения: {e}", reply_markup=get_main_menu())
            break  # Выход при неизвестной ошибке
    logging.error("Не удалось отправить сообщение после нескольких попыток.")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    # Добавляем пользователя в базу данных, если его там нет
    User.add_user(message.from_user.username, user_id)

    # Отправляем приветственное сообщение с кнопками
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item_add = telebot.types.KeyboardButton("Добавить список")
    item_remove = telebot.types.KeyboardButton("Удалить список")
    item_show = telebot.types.KeyboardButton("Показать список подписок")
    item_remove_all = telebot.types.KeyboardButton("Удалить все подписки")  # Кнопка для удаления всех подписок
    item_check_followers = telebot.types.KeyboardButton("Проверить подписки")
    markup.add(item_add, item_remove, item_show, item_remove_all, item_check_followers)

    bot.send_message(user_id, "Привет! Я бот для управления подписками. Выберите действие:",
                     reply_markup=get_main_menu())


# Обработчик "Добавить список"
@bot.message_handler(func=lambda message: message.text == "Добавить список")
def add_list(message):
    user_id = message.from_user.id
    send_message_with_retry(message.chat.id,"Пожалуйста, отправьте список людей, на которых вы подписаны, разделяя их новой строкой.")

    # Переходим в режим ожидания подписок
    bot.register_next_step_handler(message, process_add_list)


# Обработчик добавления подписок
def process_add_list(message):
    tg_id = message.from_user.id
    # Разделяем строки по новой строке
    subscriptions = message.text.strip().split("\n")

    # Преобразуем каждый элемент в нормальный формат
    subscriptions = [extract_username(sub.strip()) for sub in message.text.strip().split("\n")]
    # Добавляем подписки в базу данных
    for i in range(0,len(subscriptions)):
        following_list = get_twitter_followers(subscriptions[i],"f5c92b79-a20e-4804-a409-0dc6d712a93c" )
        Following.add_following(subscriptions[i], following_list)

    db_user_id = User.get_user_id_by_tg_id(tg_id)

    TwitterUser.add_twitter_users_bulk(db_user_id, subscriptions)

    # Получаем обновленный список подписок
    user_subscriptions = TwitterUser.get_user_following(db_user_id)

    # Отправляем обновленный список пользователю
    send_message_with_retry(message.chat.id, f"Ваш список подписок обновлен:\n" + "\n".join(user_subscriptions))


    # Логируем обновление
    logging.info(f"User {tg_id} added subscriptions: {user_subscriptions}")


# Обработчик "Удалить список"
@bot.message_handler(func=lambda message: message.text == "Удалить список")
def remove_list(message):
    tg_id = message.from_user.id
    db_user_id = User.get_user_id_by_tg_id(tg_id)
    user_subscriptions = TwitterUser.get_user_following(db_user_id)
    if not user_subscriptions:

        send_message_with_retry(message.chat.id, "У вас нет подписок для удаления.")
        return

    # Выводим список подписок для удаления
    subscriptions = "\n".join(user_subscriptions)
    send_message_with_retry(message.chat.id,
                     f"Ваш список подписок:\n{subscriptions}\nНапишите, что хотите удалить (по одной строке на каждого человека).")

    # Переходим в режим ожидания удаления
    bot.register_next_step_handler(message, process_remove_list)


# Обработчик удаления подписок
def process_remove_list(message):
    user_id = message.from_user.id
    db_user_id = User.get_user_id_by_tg_id(user_id)

    user_subscriptions = TwitterUser.get_user_following(db_user_id)
    print(user_subscriptions,"Удаление подписок по одной")
    if not user_subscriptions:
        send_message_with_retry(message.chat.id, "У вас нет подписок для удаления.")
        return

    # Разделяем строки по новой строке и удаляем подписки
    subscriptions_to_remove = message.text.strip().split("\n")
    initial_count = len(user_subscriptions)
    print(subscriptions_to_remove)
    TwitterUser.remove_twitter_users_bulk(db_user_id, subscriptions_to_remove)

    # Проверка, были ли удалены подписки
    user_subscriptions = TwitterUser.get_user_following(db_user_id)
    removed_count = initial_count - len(user_subscriptions)

    if removed_count > 0:
        send_message_with_retry(message.chat.id, f"Удалено {removed_count} подписок. Ваш обновленный список:\n" + "\n".join(
            user_subscriptions))
        logging.info(f"User {db_user_id} removed subscriptions: {subscriptions_to_remove}. Updated list: {user_subscriptions}")
    else:
        send_message_with_retry(message.chat.id, "Подписки не были найдены в вашем списке. Попробуйте еще раз.")


# Обработчик "Удалить все подписки"
@bot.message_handler(func=lambda message: message.text == "Удалить все подписки")
def remove_all_subscriptions(message):
    user_id = message.from_user.id
    db_user_id = User.get_user_id_by_tg_id(user_id)

    # Удаляем все подписки пользователя
    TwitterUser.clear_user_list(db_user_id)

    send_message_with_retry(message.chat.id, "Все подписки были удалены.")

    # Логируем удаление всех подписок
    logging.info(f"User {db_user_id} removed all subscriptions.")


# Обработчик "Показать список подписок"
@bot.message_handler(func=lambda message: message.text == "Показать список подписок")
def show_subscriptions(message):
    user_id = message.from_user.id
    db_user_id = User.get_user_id_by_tg_id(user_id)

    user_subscriptions = TwitterUser.get_user_following(db_user_id)

    if user_subscriptions:
        send_message_with_retry(message.chat.id, "Ваш список подписок:\n" + "\n".join(user_subscriptions))
    else:
        send_message_with_retry(message.chat.id, "У вас нет подписок.")


@bot.message_handler(func=lambda message: message.text == "Проверить подписки")
def check_followers(message):
    user_id = message.from_user.id
    send_message_with_retry(message.chat.id,  "Проверка пошла, ожидайте")

    print('Пошла проверка подписок дя пользователя с user_id',user_id)
    db_user_id = User.get_user_id_by_tg_id(user_id)
    print('db_user_id',db_user_id)
    user_subscriptions = TwitterUser.get_user_following(db_user_id)
    print('user_subsctiptions', user_subscriptions)

    if not user_subscriptions:
        send_message_with_retry(message.chat.id, "У вас нет подписок для проверки.")
        return

    for username in user_subscriptions:
        followers = Following.get_following(username)
        new_followers = get_twitter_followers(username, "f5c92b79-a20e-4804-a409-0dc6d712a93c")

        mega_new_followers = set(new_followers) - set(followers)
        Following.add_following(username, list(mega_new_followers))

        if mega_new_followers:
            new_follower_links = [
                f"https://twitter.com/{get_twitter_handle_by_id(follower_id, 'f5c92b79-a20e-4804-a409-0dc6d712a93c')}"
                for follower_id in mega_new_followers
            ]
            send_message_with_retry(message.chat.id, f"У {username} новые подписки:\n" + "\n".join(new_follower_links))
        else:
            send_message_with_retry(message.chat.id, f"У {username} нет новых подписок.")




def get_twitter_username_by_id(user_id, api_key):
    url = f"https://api.tweetscout.io/v2/user/{user_id}"
    headers = {"Accept": "application/json", "ApiKey": api_key}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data.get('username')  # Возвращаем username
        else:
            print(f"Ошибка при получении username для ID {user_id}: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе username для ID {user_id}: {e}")
        return None



def update_following():
    while True:
        try:
            users = User.get_all_users()
            print(users)
            for user in users:
                tg_id = user['tg_id']
                print(tg_id)
                db_user_id = user['user_id']
                user_subscriptions = TwitterUser.get_user_following(db_user_id)
                print('User subscriptions:',user_subscriptions)
                for username in user_subscriptions:
                    print(username)
                    followers = Following.get_following(username)
                    print("Старые фоловеры", len(followers))
                    new_followers = get_twitter_followers(username, "f5c92b79-a20e-4804-a409-0dc6d712a93c")
                    print("Новые фолловеры", len(new_followers))
                    mega_new_followers = set(new_followers)-set(followers)
                    print('Самые новые подписки', list(mega_new_followers))
                    Following.add_following(username, list(mega_new_followers))
                    new_follower_links = [f"https://twitter.com/{get_twitter_handle_by_id(follower_id,"f5c92b79-a20e-4804-a409-0dc6d712a93c")}" for follower_id in mega_new_followers]

                    if new_follower_links:
                        telegram_ids = TwitterUser.get_user_ids_for_twitter_username(username)
                        print(telegram_ids)
                        for id in range(0, len(telegram_ids)):
                            print(User.get_tg_id_by_user_id(telegram_ids[id]))
                            send_message_with_retry(User.get_tg_id_by_user_id(telegram_ids[id]), f"У {username} новые подписки:\n" + "\n".join(new_follower_links))
                    else:
                        send_message_with_retry(tg_id, f"У {username} нет новых подписок.")

                send_message_with_retry(tg_id, "Ваш список подписок был обновлен.",)

            logging.info("Обновление подписок завершено.")
        except Exception as e:
            logging.error(f"Ошибка при обновлении подписок: {e}")
        time.sleep(12 * 60 * 60)  # 5 минут



# Запускаем поток для обновления подписок
threading.Thread(target=update_following, daemon=True).start()

if __name__ == '__main__':
    print('Bot is running')

    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as e:
            logging.error(f"Бот упал с ошибкой: {e}")
            print(f"Бот упал с ошибкой: {e}, перезапускаю...")
            time.sleep(5)  # Пауза перед рестартом

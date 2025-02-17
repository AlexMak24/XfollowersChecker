import requests
import time

def get_twitter_followers(username, api_key, delay=2, retries=3, timeout=500):
    url = "https://api.tweetscout.io/v2/follows"
    params = {"link": username}
    headers = {"Accept": "application/json", "ApiKey": api_key}

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)

            if response.status_code == 200:
                data = response.json()
                return [user["id"] for user in data]  # Возвращаем список ID подписчиков
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return []  # Возвращаем пустой список при ошибке запроса

        except requests.exceptions.Timeout as e:
            print(f"Ошибка при запросе (попытка {attempt + 1}): Тайм-аут - {e}")
            if attempt < retries - 1:
                print("Повторная попытка...")
                time.sleep(delay)
            else:
                print("Все попытки неудачны, возвращаем пустой список.")
                return []  # Возвращаем пустой список при неудачных попытках

        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка соединения (попытка {attempt + 1}): {e}")
            if attempt < retries - 1:
                print("Повторная попытка...")
                time.sleep(delay)
            else:
                print("Все попытки неудачны, возвращаем пустой список.")
                return []  # Возвращаем пустой список при неудачных попытках

        except requests.exceptions.RequestException as e:
            print(f"Неизвестная ошибка при запросе (попытка {attempt + 1}): {e}")
            if attempt < retries - 1:
                print(f"Задержка перед повторной попыткой... ({delay} секунд)")
                time.sleep(delay)  # Задержка между попытками
            else:
                print("Все попытки неудачны, возвращаем пустой список.")
                return []  # Возвращаем пустой список при других ошибках

    return []  # Возвращаем пустой список, если все попытки неудачны

def get_twitter_handle_by_id(user_id, api_key, delay=2, retries=3, timeout=500):
    url = f"https://api.tweetscout.io/v2/id-to-handle/{user_id}"
    headers = {
        "Accept": "application/json",
        "ApiKey": api_key
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)

            if response.status_code == 200:
                data = response.json()
                return data.get("handle")
            elif response.status_code == 429:
                print("Превышен лимит запросов. Подождем немного...")
                time.sleep(60)  # Задержка на 1 минуту в случае превышения лимита
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None  # Возвращаем None при ошибке запроса

        except requests.exceptions.Timeout as e:
            print(f"Ошибка при запросе (попытка {attempt + 1}): Тайм-аут - {e}")
            if attempt < retries - 1:
                print("Повторная попытка...")
                time.sleep(delay)
            else:
                print("Все попытки неудачны, возвращаем None.")
                return None  # Возвращаем None при неудачных попытках

        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка соединения (попытка {attempt + 1}): {e}")
            if attempt < retries - 1:
                print("Повторная попытка...")
                time.sleep(delay)
            else:
                print("Все попытки неудачны, возвращаем None.")
                return None  # Возвращаем None при неудачных попытках


        except requests.exceptions.RequestException as e:
            print(f"Неизвестная ошибка при запросе (попытка {attempt + 1}): {e}")
            if attempt < retries - 1:
                print(f"Задержка перед повторной попыткой... ({delay} секунд)")
                time.sleep(delay)  # Задержка между попытками
            else:
                print("Все попытки неудачны, возвращаем None.")
                return None  # Возвращаем None при других ошибках

    return None  # Возвращаем None, если все попытки неудачны

# Пример использования:
API_KEY = ""  # Замени на свой API-ключ

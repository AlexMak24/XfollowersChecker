from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    button1 = KeyboardButton(text="🚀 Запустить бота")
    button2 = KeyboardButton(text="📋 Показать список")
    button3 = KeyboardButton(text="➕ Расширить список")
    button4 = KeyboardButton(text="➖ Уменьшить список")
    button5 = KeyboardButton(text="🗑 Удалить список")

    keyboard.add(button1, button2, button3, button4, button5)
    return keyboard

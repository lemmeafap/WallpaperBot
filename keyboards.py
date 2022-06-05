from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton,InlineKeyboardMarkup

def generate_categories(categories):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = []
    for category in categories:
        btn = KeyboardButton(text=category[0])
        buttons.append(btn)
    markup.add(*buttons)
    return markup


def download_button(image_id):
    markup = InlineKeyboardMarkup()
    download_d = InlineKeyboardButton(text='Скачать для десктоп', callback_data=f'downloadd_{image_id}')
    download_m = InlineKeyboardButton(text='Скачать для мобильного', callback_data=f'downloadm_{image_id}')
    markup.add(download_d, download_m)
    return markup

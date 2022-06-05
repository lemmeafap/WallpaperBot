from aiogram import Dispatcher, executor, Bot
# Тот кто следит за сигналами, 2 - тот кто запускает бота, 3 - сам бот
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
from keyboards import *
import os
import sqlite3
import random
import re
import requests
from utils import watermark_text, crop_image_to_mobile


load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(TOKEN)

dp = Dispatcher(bot=bot)

@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, 'Привет. Тут ты найдешь обои на любой вкус!')
    await show_categories(message)

async def show_categories(message: Message):
    chat_id = message.chat.id
    database = sqlite3.connect('wallpapers.db')
    cursor = database.cursor()

    cursor.execute('''
    SELECT category_name FROM categories;
    ''')
    categories = cursor.fetchall()

    database.close()
    await bot.send_message(chat_id, 'Выберите категорию: ', reply_markup=generate_categories(categories))

# Сделать реакцию на текст

@dp.message_handler(content_types=['text'])
async def get_image(message):
    chat_id = message.chat.id
    category = message.text
    datebase = sqlite3.connect('wallpapers.db')
    cursor = datebase.cursor()
    cursor.execute('''
    SELECT category_id FROM categories WHERE category_name = ?;
    ''', (category,))

    category_id = cursor.fetchone()[0]

    cursor.execute('''
    SELECT image_link FROM images WHERE category_id = ?;
    ''', (category_id,))

    image_links = cursor.fetchall()

    random_index = random.randint(0, len(image_links)-1) #100  0-99
    random_image_link = image_links[random_index][0]

    resolution = re.search(r'[0-9]+x[0-9]+', random_image_link)[0]

    cursor.execute('''
    SELECT image_id FROM images WHERE image_link = ?;
    ''', (random_image_link,))


    responseImage = requests.get(random_image_link).content
    image_name = random_image_link.replace('https://images.wallpaperscraft.ru/image/single/', '')
    with open(file=f'{image_name}', mode='wb') as file:
        file.write(responseImage)

    crop_image_to_mobile(image_name)
    watermark_text(image_name)
    #os.remove(image_name) # Удалит скаченную картинку

    image_id = cursor.fetchone()[0]

    img = open(f'water_{image_name}', 'rb')

    try:
        await bot.send_photo(chat_id=chat_id,
                       photo=img,
                       caption=f'Разрешение {resolution}',
                       reply_markup=download_button(image_id)
                       )
        img.close()
        os.remove(image_name)
        os.remove(f'water_{image_name}')
        os.remove(f'crop_{image_name}')
    except Exception as e:
        new_image_link = random_image_link.replace(resolution, '1920x1080')
        await bot.send_photo(chat_id=chat_id,
                       photo=new_image_link,
                       caption=f'Разрешение 1920x1080 Заменили',
                       reply_markup=download_button(image_id)
                       )
        img.close()
        os.remove(image_name)
        os.remove(f'water_{image_name}')
        os.remove(f'crop_{image_name}')
    await show_categories(message)

@dp.callback_query_handler(lambda call: 'downloadd' in call.data)
async def downloadd_reaction(call):
    _, image_id = call.data.split('_')
    database = sqlite3.connect('wallpapers.db')
    cursor = database.cursor()
    cursor.execute(
        '''
        SELECT image_link FROM images WHERE image_id = ?;
        ''', (image_id,)
    )
    image_link = cursor.fetchone()[0]
    await bot.send_document(chat_id=call.message.chat.id, document=image_link)
    await bot.answer_callback_query(call.id, show_alert=False)

@dp.callback_query_handler(lambda call: 'downloadm' in call.data)
async def downloadm_reaction(call):
    _, image_id = call.data.split('_')
    database = sqlite3.connect('wallpapers.db')
    cursor = database.cursor()
    cursor.execute(
        '''
        SELECT image_link FROM images WHERE image_id = ?;
        ''', (image_id,)
    )
    image_link = cursor.fetchone()[0]

    responseImage = requests.get(image_link).content
    image_name = image_link.replace('https://images.wallpaperscraft.ru/image/single/', '')
    with open(file=f'{image_name}', mode='wb') as file:
        file.write(responseImage)

    crop_image_to_mobile(image_name)

    img = open(f'crop_{image_name}', mode='rb')
    await bot.send_document(chat_id=call.message.chat.id, document=img)
    img.close()
    os.remove(image_name)
    os.remove(f'crop_{image_name}')
    await bot.answer_callback_query(call.id, show_alert=False)


executor.start_polling(dp, skip_updates=True)


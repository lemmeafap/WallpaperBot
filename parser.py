from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
import sqlite3
import re

load_dotenv()

URL = os.getenv('URL')
HOST = os.getenv('HOST')

db = sqlite3.connect('wallpapers.db')
cursor = db.cursor()


class Category_parser:
    def __init__(self, url, name, category_id, pages=3, download=False):
        self.url = url
        self.name = name
        self.category_id = category_id
        self.pages = pages
        self.download = download

    def get_html(self, i):
        try:
            html = requests.get(self.url + f'/page{i}').text
            return html
        except:
            print('Не удалось получить страницу')


    def get_soup(self, i):
        html = self.get_html(i)
        soup = BeautifulSoup(html, 'html.parser')
        return soup


    def get_data(self):

        for i in range(1, self.pages + 1):
            soup = self.get_soup(i)
            images_blocks = soup.find_all('a', class_='wallpapers__link')
            for block in images_blocks:
                page_link = HOST + block.get('href')
                print(page_link)
                page_html = requests.get(page_link).text
                page_soup = BeautifulSoup(page_html, 'html.parser')
                resolution = page_soup.find_all('span', class_='wallpaper-table__cell')[1].get_text(strip=True)
                print(resolution)
                image_link = block.find('img', class_='wallpapers__image').get('src')
                image_link = image_link.replace('300x168', resolution)
                print(image_link)

                cursor.execute('''
                INSERT OR IGNORE INTO images(image_link, category_id)
                VALUES (?,?);
                ''', (image_link, self.category_id))
                db.commit()

                if self.download:
                    if self.name not in os.listdir(): # Вернет список файлов и папок в текущей папке
                        os.mkdir(str(self.name))

                    responseImage = requests.get(image_link).content
                    image_name = image_link.replace('https://images.wallpaperscraft.ru/image/single/', '')
                    with open(file=f'{self.name}/{image_name}', mode='wb') as file:
                        file.write(responseImage)

def parsing():
    html = requests.get(URL).text
    soup = BeautifulSoup(html, 'html.parser')
    filters_list = soup.find('ul', class_='filters__list')
    filters = filters_list.find_all('a', class_='filter__link')
    for filt in filters:
        link = HOST + filt.get('href')
        print(link)
        name = filt.get_text(strip=True)
        print(name)

        true_name = re.findall(r'[3]*[a-zA-Zа-яА-Яё]+', name)[0]
        print(true_name)

        pages = int(re.findall(r'[0-9][0-9]+', name)[0]) // 15
        print(pages)

        cursor.execute('''
        INSERT OR IGNORE INTO categories(category_name) VALUES (?);
        ''', (true_name, ))
        db.commit()

        cursor.execute('''
        SELECT category_id FROM categories WHERE category_name = ?;
        ''', (true_name,))
        category_id = cursor.fetchone()[0]
        print(category_id)

        parser = Category_parser(url=link,
                                 name=true_name,
                                 category_id=category_id
                                 )
        parser.get_data()
parsing()

db.close()

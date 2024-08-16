import requests
from bs4 import BeautifulSoup
from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time, re
import datetime
import random
import psycopg2
from sqlite3 import Error
import datetime
from datetime import timedelta
from lorem.text import TextLorem
from selenium import webdriver
from yandex_geocoder import Client

def getCoordinate(address):
    try:
        client = Client("")
        coordinates = client.coordinates(address)
        return (str(coordinates[0]), str(coordinates[1]))
    except:
        return (None, None)

def reviews_generate():
    time.sleep(0.5)
    try:
        params = f'&type={'sentence'}&number={random.randint(1, 9)}'
        response = requests.get(f'https://fish-text.ru/get?{params}')
        if response.status_code == 200:
            data = response.json()['text']
            return data
        else:
            print("Ошибка при получении ответа")
            return '7 бобров из 13 выдр и того 4 Динозавра Абрамовича'
    except:
        return '7 бобров из 13 выдр и того 4 Динозавра Абрамовича'
    

LIST_RULES = {
    'animal_check': 'можно с питомцами',
    'smoking_check': 'курение разрешено',
    'party_check': 'вечеринки и мероприятия по согласованию с хозяином жилья',
    'docs_check': 'владелец предоставляет отчетные документы о проживании по согласованию',
    'kids_check': 'можно с детьми любого возраста',
}

LIST_PROPERTIES = {
    'wifi': 'беспроводной интернет Wi-Fi',
    'drier': 'фен',
    'towel': 'полотенца',
    'bed_linen': 'постельное белье',
    'tv': 'телевизор',
    'microwave': 'микроволновка',
    'electric_kettle': 'электрический чайник',
    'balcony': 'балкон / лоджия',
}

def html_validate(html_elem, type_validate):
        if not html_elem: return None

        if type_validate == 'text':
            text = html_elem.text
            text = text.replace('скрыть', '')
            text = text.replace('"', ' ')
            text = text.replace("'", ' ')
            return ' '.join(filter(None, text.split()))
        
        elif type_validate == 'number':
            num = ''.join(re.findall(r'(\d+)', html_elem.text))
            return int(num) if num != '' else None
        
        elif type_validate == 'src':
            return html_elem['src']
        
        elif type_validate == 'list':
            if len(html_elem) > 0:
                text = ''
                for elem in html_elem:
                    text += f'{elem.text}, '
                text = text[:-2]
                return ' '.join(filter(None, text.split()))
            return None

        return 0

class Parser:
    count_page_parsed = 0
    count_page_all = 0

    links_to_parse = [
    ]

    def get_flats_by_link(self, link):
        driver = webdriver.Firefox()
        driver.get(link)

        time.sleep(7)
        current_page = 1
        
        while current_page < 11:
            page_height = driver.execute_script("return document.body.scrollHeight")
            curr_pos = 0
            while curr_pos < page_height:
                driver.execute_script(f"window.scrollTo({curr_pos}, {curr_pos+300});")
                curr_pos += 300
                time.sleep(1)

            time.sleep(1)

            to_parse = BeautifulSoup(driver.page_source, 'lxml')

            originalWindow = driver.current_window_handle
            driver.switch_to.new_window('tab')
            
            flats_items = []

            for elem in to_parse.find_all('div', class_='card'):
                flats_items.append(elem)

            for item in flats_items:
                dict_ = {}

                elem = item.find('a', class_='card-content')
                href = elem['href']

                # получение страницы с полной инфой объявления
                driver.get(f'https://sutochno.ru{href}')
                time.sleep(4)

                try:
                    driver.find_element(By.CLASS_NAME, 'link-more').click()
                except NoSuchElementException:
                    pass

                page_height = driver.execute_script("return document.body.scrollHeight")
                curr_pos = 0
                while curr_pos < page_height:
                    driver.execute_script(f"window.scrollTo({curr_pos}, {curr_pos+700});")
                    curr_pos += 700
                    time.sleep(1)

                to_parse = BeautifulSoup(driver.page_source, 'lxml')

                # полное описание
                try:
                    dict_['description'] = html_validate(to_parse.find('div', class_='object-data--desk'), 'text')
                except:
                    dict_['description'] = reviews_generate()
                if not dict_['description']:
                    dict_['description'] = reviews_generate()

                # изображение
                try:
                    img_list = []
                    imgs = to_parse.find_all('img', class_='navigation__img')
                    for img in imgs:
                        img_list.append(img['src'])
                    dict_['img_src'] = img_list
                except:
                    dict_['img_src'] = ['https://i.pinimg.com/564x/ed/33/88/ed33881d061a566da9f4e43ba7d6ec18.jpg']


                # время заезда и отъезда
                try:
                    clock = html_validate(to_parse.find('div', class_='clock'), 'text')
                    pos = clock.find('Отъезд')
                    dict_['clock_entry'] = clock[:pos][-5:]
                    dict_['clock_leave'] = clock[pos:][-5:]
                except:
                    dict_['clock_entry'] = datetime.datetime.strptime('13:00', '%H:%M')
                    dict_['clock_leave'] = datetime.datetime.strptime('11:00', '%H:%M')


                # слава матану...
                variants = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1],
                            [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1],
                            [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1],
                            [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], 
                            [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3],
                            [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3],
                            [1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [1, 2],
                            [1, 5], [1, 5],
                            [1, 7], [1, 7], [1, 7], [1, 7],
                            [1, 14],
                            [1, 28]]
                pos = random.randint(0, len(variants)-1)
                dict_['min_length_of_stay'] = variants[pos][0]
                dict_['max_length_of_stay'] = variants[pos][1]


                # список правил
                try:
                    elem = to_parse.find('div', class_='rules--list')
                    rules = html_validate(elem.find_all('div'), 'list')
                    for key in LIST_RULES:
                        dict_[key] = True if LIST_RULES[key] in rules else False
                except:
                    for key in LIST_RULES:
                        dict_[key] = bool(random.getrandbits(1))


                # список удобств
                try:
                    elem = to_parse.find('div', class_='often-properties')
                    properties = html_validate(elem.find_all('p'), 'list')
                    for key in LIST_PROPERTIES:
                        dict_[key] = True if LIST_PROPERTIES[key] in properties else False
                except:
                    for key in LIST_PROPERTIES:
                        dict_[key] = bool(random.getrandbits(1))


                # общие параметры
                try:
                    params = to_parse.find('div', class_='object-data--params')
                    text = html_validate(params.find_all('span'), 'list')
                    pos = text.find('кроват')
                    dict_['params'] = text
                    count = ''.join(re.findall(r'(\d+)', text[4:pos]))
                    dict_['count_beds'] = int(count) if count != '' else None
                except:
                    dict_['params'] = '2 гостя 1 кровать кухонная зона этаж 4 из 11, есть лифт'
                    dict_['count_beds'] = random.randint(1, 5)
                

                # оснащение и площать
                try:
                    elem = item.find('div', class_='card-content__facilities') 
                    elems = elem.find_all('div')
                    dict_['square'] = html_validate(elems[0], 'number')
                    dict_['count_people'] = html_validate(elems[1], 'number')
                except:
                    dict_['square'] = random.randint(14, 69)
                    dict_['count_people'] = random.randint(2, 13)


                # спальные места
                try:
                    dict_['sleeping_places'] = html_validate(to_parse.find('div', class_='object-data--sleeping-places'), 'number')
                except:
                    dict_['sleeping_places'] = dict_['count_people']
                if not dict_['sleeping_places']:
                    dict_['sleeping_places'] = dict_['count_people']


                # кровати
                try:
                    dict_['beds_info'] = html_validate(to_parse.find('div', class_='object-data--beds'), 'text')
                except:
                    dict_['beds_info'] = '1 двуспальная кровать 2 односпальные кровати'


                # тип жилья
                try:
                    type = html_validate(item.find('span', class_='object-hotel__type'), 'text')
                    if type == None:
                        dict_['type_flats'] = html_validate(item.find('div', class_='card-content__object-subtext'), 'text')
                    else:
                        dict_['type_flats'] = type
                except:
                    dict_['type_flats'] = 'Апартаменты'


                # описание
                try:
                    dict_['short_desc'] = html_validate(item.find('h2', class_='card-content__object-title'), 'text')
                except:
                    dict_['short_desc'] = 'Уютные апартаменты рядом с дорогой'
                if not dict_['short_desc']:
                    dict_['short_desc'] = 'Уютные апартаменты рядом с дорогой'


                # адрес
                try:
                    address_block = to_parse.find_all('div', class_='map-info')
                    if len(address_block):
                        city = html_validate(address_block[0].find('div', class_='address'), 'text')
                        street = html_validate(address_block[0].find('div', class_='map-info--address'), 'text')
                        if city and street:
                            dict_['address'] = f'{city}, {street}'
                        else:
                            dict_['address'] = 'Санкт-Петербург, Московский р-н'
                    else:
                        dict_['address'] = 'Санкт-Петербург, Московский р-н'
                except:
                    dict_['address'] = 'Санкт-Петербург, Московский р-н'
                
                coordinate = getCoordinate(dict_['address'])
                dict_['address_lat'] = coordinate[0]
                dict_['address_lon'] = coordinate[1]


                # цена за сутки
                try:
                    dict_['price'] = html_validate(item.find('div', class_='price-total__number'), 'number')
                except:
                    dict_['price'] = 7500

                # рейтинг
                try:
                    elem = to_parse.find('div', class_='reviews--empty')
                    if elem:
                        dict_['rating'] = 0
                        dict_['count_reviews'] = 0
                    else:
                        num = html_validate(to_parse.find('div', class_='rating-top'), 'number')
                        count = html_validate(to_parse.find('div', class_='count-reviews'), 'number')
                        if count != None and num != None:
                            if count > 50: count = random.randint(40, 60)
                            dict_['rating'] =  (float(num) / 10) // 1 if num else num
                            dict_['count_reviews'] = count
                        else:
                            dict_['rating'] = 0
                            dict_['count_reviews'] = 0
                except:
                    dict_['rating'] = 0
                    dict_['count_reviews'] = 0

                self.count_page_all += 1
                
                with open('data.txt', 'a', encoding="utf-8") as file:
                    file.write(f'//////////////////////////////////////\n')
                    for key in dict_.keys():
                        file.write(f'{str(key)}: {str(dict_[key])}\n')
                    file.write(f'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n\n')

                flag = False
                for key in dict_.keys():
                    if dict_[key] == None or dict_[key] == '' or dict_[key] == []: flag = True
                if flag: continue

                self.count_page_parsed += 1

                dict_['owner_id'] = 456

                # конект к базе
                try:
                    connection = psycopg2.connect(
                        dbname='my_db',
                        user='postgres',
                        password='0000',
                        host='localhost',
                        port='5432'
                    )
                except Error:
                    print(Error)

                # запись объявления в БД
                ad_id = 0
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"""
                                INSERT INTO core_ad (
                                    cash_back,
                                    fast_booking,
                                    long_term,
                                    description,
                                    clock_entry,
                                    clock_leave,
                                    min_length_of_stay,
                                    max_length_of_stay,
                                    animal_check,
                                    smoking_check,
                                    party_check,
                                    docs_check,
                                    kids_check,
                                    wifi,
                                    drier,
                                    towel,
                                    bed_linen,
                                    tv,
                                    microwave,
                                    electric_kettle,
                                    balcony,
                                    params,
                                    count_beds,
                                    square,
                                    count_people,
                                    sleeping_places,
                                    beds_info,
                                    type_flats,
                                    short_desc,
                                    address,
                                    address_lat,
                                    address_lon,
                                    price,
                                    owner_id
                                )
                                VALUES (
                                    '{10}',
                                    '{True}',
                                    '{True}',
                                    '{dict_['description']}',
                                    '{dict_['clock_entry']}',
                                    '{dict_['clock_leave']}',
                                    '{dict_['min_length_of_stay']}',
                                    '{dict_['max_length_of_stay']}',
                                    '{dict_['animal_check']}',
                                    '{dict_['smoking_check']}',
                                    '{dict_['party_check']}',
                                    '{dict_['docs_check']}',
                                    '{dict_['kids_check']}',
                                    '{dict_['wifi']}',
                                    '{dict_['drier']}',
                                    '{dict_['towel']}',
                                    '{dict_['bed_linen']}',
                                    '{dict_['tv']}',
                                    '{dict_['microwave']}',
                                    '{dict_['electric_kettle']}',
                                    '{dict_['balcony']}',
                                    '{dict_['params']}',
                                    '{dict_['count_beds']}',
                                    '{dict_['square']}',
                                    '{dict_['count_people']}',
                                    '{dict_['sleeping_places']}',
                                    '{dict_['beds_info']}',
                                    '{dict_['type_flats']}',
                                    '{dict_['short_desc']}',
                                    '{dict_['address']}',
                                    '{dict_['address_lat']}',
                                    '{dict_['address_lon']}',
                                    '{dict_['price']}',
                                    '{dict_['owner_id']}'
                                )
                                returning id
                            """
                        )
                        connection.commit()
                        ad_id = cursor.fetchone()[0]
                        print('Успешное создание записи объявления')
                except:
                    print('Ошибка при создании записи объявления')
                    continue

                # запись ссылок на изображения
                for image in dict_['img_src']:
                    try:
                        with connection.cursor() as cursor:
                            cursor = connection.cursor()
                            cursor.execute(
                                f"""
                                    INSERT INTO core_image (
                                        src,
                                        ad_id
                                    )
                                    VALUES (
                                        '{image}',
                                        '{ad_id}'
                                    )
                                """
                            )
                            connection.commit()
                    except:
                        print('Ошибка при записи изображения')

                # запись рэйтинга
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"""
                                INSERT INTO core_rating (
                                    count_reviews,
                                    sum_rating,
                                    ad_id
                                )
                                VALUES (
                                    '{0}',
                                    '{0}',
                                    '{ad_id}'
                                )
                            """
                        )
                        connection.commit()
                except:
                    print('Ошибка при записи рейтинга')

                print(f'Успешных итераций {self.count_page_parsed}/{self.count_page_all}')

            current_page += 1
            driver.close()
            driver.switch_to.window(originalWindow)

            try:
                driver.find_element(By.LINK_TEXT, f'{current_page}').click()
            except NoSuchElementException:
                break

        driver.quit()

    def run(self):
        for link in Parser.links_to_parse:
            self.get_flats_by_link(link)
            print(f'ссылка: {link}\nуспешно пройдена...')


Parser().run()

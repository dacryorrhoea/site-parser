import requests
from bs4 import BeautifulSoup
from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time, re
import data_client
import random


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
    links_to_parse = [
        'https://sutochno.ru/front/searchapp/search?occupied=2024-07-21;2024-08-31&guests_adults=2&term=%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3&pets=true&price_per=1&id=397367&type=city&SW.lat=59.764131550046194&SW.lng=30.04122762499994&NE.lat=60.07130936975916&NE.lng=30.56857137499992',
    ]
    data_client_imp = data_client.PostgresClient()


    @staticmethod
    def get_flats_by_link(link):
        cService = Service(r"C:\Users\Alice\ShitCode\aduc\chmo\chromedriver.exe")
        driver = wd.Chrome(service=cService)

        driver.get(link)

        time.sleep(10)

        page_height = driver.execute_script("return document.body.scrollHeight")
        curr_pos = 0
        while curr_pos < page_height:
            driver.execute_script(f"window.scrollTo({curr_pos}, {curr_pos+300});")
            curr_pos += 300
            time.sleep(1)

        time.sleep(1)

        to_parse = BeautifulSoup(driver.page_source, 'lxml')
        
        flats_items = []
        for elem in to_parse.find_all('div', class_='card'):
            flats_items.append(elem)

        flats = []
        
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

            time.sleep(1)

            to_parse = BeautifulSoup(driver.page_source, 'lxml')

            # with open('data.html', 'a', encoding='utf-8') as file:
            #     file.write(str(to_parse.find('body')))

            # полное описание
            dict_['description'] = html_validate(to_parse.find('div', class_='object-data--desk'), 'text')

            # изображение
            dict_['img_src'] = html_validate(item.find('img', class_='track__img'), 'src')

            # время заезда и отъезда
            clock = html_validate(to_parse.find('div', class_='clock'), 'text')
            if clock:
                pos = clock.find('Отъезд')
                dict_['clock_entry'] = clock[:pos]
                dict_['clock_leave'] = clock[pos:]
            else:
                dict_['clock_entry'] = None
                dict_['clock_leave'] = None

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
                        [7, 14],
                        [14, 28]]
            pos = random.randint(0, len(variants)-1)
            dict_['min_length_of_stay'] = variants[pos][0]
            dict_['max_length_of_stay'] = variants[pos][1]

            # список правил
            elem = to_parse.find('div', class_='rules--list')
            if elem:
                rules = html_validate(elem.find_all('div'), 'list')
                for key in LIST_RULES:
                    dict_[key] = True if LIST_RULES[key] in rules else False
            else:
                dict_['rules'] = None

            # список удобств
            elem = to_parse.find('div', class_='often-properties')
            if elem:
                properties = html_validate(elem.find_all('p'), 'list')
                for key in LIST_PROPERTIES:
                    dict_[key] = True if LIST_PROPERTIES[key] in properties else False
            else:
                dict_['properties'] = None

            # общие параметры
            params = to_parse.find('div', class_='object-data--params')
            if params:
                text = html_validate(params.find_all('span'), 'list')
                pos = text.find('кроват')
                dict_['params'] = text
                dict_['count_beds'] = int(''.join(re.findall(r'(\d+)', text[4:pos])))

            # оснащение и площать
            elem = item.find('div', class_='card-content__facilities') 
            elems = elem.find_all('div')
            dict_['square'] = html_validate(elems[0], 'number')
            dict_['count_people'] = html_validate(elems[1], 'number')

            # спальные места
            dict_['sleeping-places'] = html_validate(to_parse.find('div', class_='object-data--sleeping-places'), 'number')

            # кровати
            dict_['beds_info'] = html_validate(to_parse.find('div', class_='object-data--beds'), 'text')

            # тип жилья
            dict_['type_flats'] = html_validate(item.find('span', class_='object-hotel__type'), 'text')

            # описание
            dict_['short_desc'] = html_validate(item.find('h2', class_='card-content__object-type'), 'text')

            # адрес
            address_block = to_parse.find_all('div', class_='map-info')
            if len(address_block):
                city = html_validate(address_block[0].find('div', class_='address'), 'text')
                street = html_validate(address_block[0].find('div', class_='map-info--address'), 'text')
                dict_['address'] = f'{city}, {street}'

            # цена за сутки
            dict_['price'] = html_validate(item.find('span', class_='price-order__main-text'), 'number')

            # рэйтинг
            elem = to_parse.find('div', class_='reviews--empty')
            if elem:
                dict_['rating'] = 0
                dict_['number_reviews'] = 0
            else:
                num = html_validate(to_parse.find('div', class_='rating-top'), 'number')
                dict_['rating'] =  float(num) / 10 if num else num
                dict_['count_reviews'] = html_validate(to_parse.find('div', class_='count-reviews'), 'number')

            flats.append(dict_)



        driver.quit()

        return flats

    def save_to_postgres(self, flats_items):
        connection = self.data_client_imp.get_connection()
        self.data_client_imp.create_flats_table(connection)
        for item in flats_items:
            self. data_client_imp.insert(connection, item)

    def run(self):
        flats_items = []
        for link in Parser.links_to_parse:
            flats_items.extend(self.get_flats_by_link(link))

        with open('data.txt', 'w', encoding="utf-8") as file:
            for item in flats_items:
                flag = False
                for key in item.keys():
                    if item[key] == None: flag = True
                if flag: continue

                file.write(f'//////////////////////////////////////\n')
                for key in item.keys():
                    file.write(f'{str(key)}: {str(item[key])}\n')
                file.write(f'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n\n')


        # self.save_to_postgres(flats_items)


Parser().run()

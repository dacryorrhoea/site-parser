import requests
from bs4 import BeautifulSoup
from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time, re
import random
import psycopg2
from sqlite3 import Error
import datetime
from datetime import timedelta
from lorem.text import TextLorem

def reviews_generate():
    # try:
        # params = f'&type={'paragraph'}&number={1}'
        # response = requests.get(f'https://fish-text.ru/get?{params}')
        # if response.status_code == 200:
        #     data = response.json()['text']
        #     return data
    #     else:
    #         print("Ошибка при получении ответа")
    #         return '10 бобров из 13 выдр'
    # except:
        return 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Hic reiciendis neque rerum nulla nihil iste natus veniam porro, dolores, temporibus maiores assumenda minus consequuntur ullam eos provident quasi vel ea, laborum sint blanditiis. Fugit, nam quaerat atque numquam animi autem qui iste voluptatum distinctio ut nostrum deserunt delectus illo accusamus reprehenderit ex rerum earum eos minima exercitationem! Quos commodi corporis voluptate non quis adipisci debitis, voluptas, exercitationem repudiandae, ipsum fugit eos! Beatae magni nemo reprehenderit quis facere ipsum minus laborum delectus consequatur adipisci nihil, error voluptatem exercitationem cumque ab cum nostrum possimus quibusdam officia laudantium nesciunt ipsa pariatur? Sapiente, molestias!'
    

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
    user_id = 67
    ad_id = 194

    links_to_parse = [
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9A%D0%B0%D0%B7%D0%B0%D0%BD%D1%8C&price_per=1&id=281471&type=city&SW.lat=55.70730746975564&SW.lng=49.01138206250001&NE.lat=55.87964385200363&NE.lng=49.27505393750004',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9C%D0%B8%D0%BD%D1%81%D0%BA&price_per=1&id=398612&type=city&SW.lat=53.71150052556748&SW.lng=27.29628962109311&NE.lat=54.072879893738794&NE.lng=27.823633371093113',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%93%D1%80%D0%BE%D0%B4%D0%BD%D0%BE&price_per=1&id=399397&type=city&SW.lat=53.588629933682746&SW.lng=23.71482806249992&NE.lat=53.77024360358206&NE.lng=23.97849993749992',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%93%D0%BE%D0%BC%D0%B5%D0%BB%D1%8C&price_per=1&id=398075&type=city&SW.lat=52.27002437460174&SW.lng=30.69622512499998&NE.lat=52.64376041984084&NE.lng=31.223568874999984',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9C%D0%BE%D0%B3%D0%B8%D0%BB%D1%91%D0%B2&price_per=1&id=403756&type=city&SW.lat=53.79110416010789&SW.lng=30.220211562499973&NE.lat=53.971841466190874&NE.lng=30.483883437499976',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9A%D0%B0%D0%B7%D0%B0%D0%BD%D1%8C&price_per=1&id=281471&type=city&SW.lat=55.60313&SW.lng=48.82057&NE.lat=55.930791&NE.lng=49.379394',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%A3%D1%84%D0%B0&price_per=1&id=273530&type=city&SW.lat=54.55365426731437&SW.lng=55.774475124999974&NE.lat=54.90771176426685&NE.lng=56.30181887499998',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9F%D0%B8%D0%BD%D1%81%D0%BA&price_per=1&id=403949&type=city&SW.lat=52.08002562321086&SW.lng=26.00418903124998&NE.lat=52.1741620969489&NE.lng=26.136024968749993',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%B2%D0%BE%D1%81%D1%82%D0%BE%D0%BA&price_per=1&id=289562&type=city&SW.lat=42.94914231815717&SW.lng=131.77564012499988&NE.lat=43.39691941952273&NE.lng=132.30298387499988',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9A%D1%80%D0%B0%D1%81%D0%BD%D0%BE%D0%B4%D0%B0%D1%80&price_per=1&id=287323&type=city&SW.lat=44.95762135594417&SW.lng=38.85384356249998&NE.lat=45.17440235556739&NE.lng=39.11751543749998',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%95%D0%BA%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%BD%D0%B1%D1%83%D1%80%D0%B3&price_per=1&id=368255&type=city&SW.lat=56.451461589342436&SW.lng=59.94772174999994&NE.lat=57.12302256982763&NE.lng=61.00240924999995',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%A1%D0%BC%D0%BE%D0%BB%D0%B5%D0%BD%D1%81%D0%BA&price_per=1&id=369841&type=city&SW.lat=54.69047626008555&SW.lng=31.867228062499944&NE.lat=54.867294476562584&NE.lng=32.13089993749995',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9A%D1%80%D1%8B%D0%BC%D1%81%D0%BA&price_per=1&id=287698&type=city&SW.lat=44.867015208626036&SW.lng=37.92360603124993&NE.lat=44.97568165395947&NE.lng=38.055441968749946',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9A%D1%80%D1%8B%D0%BC&price_per=1&id=19888&type=region&SW.lat=43.47113790575115&SW.lng=32.416815999999976&NE.lat=46.929818405970586&NE.lng=36.63556599999998',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9A%D0%B8%D0%B5%D0%B2&price_per=1&id=398363&type=city&SW.lat=50.20647989305239&SW.lng=30.269062624999968&NE.lat=50.59750498785292&NE.lng=30.79640637499997',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9B%D0%B5%D0%BD%D0%B8%D0%BD%D0%B3%D1%80%D0%B0%D0%B4%D1%81%D0%BA%D0%B0%D1%8F&price_per=1&id=398420&type=city&SW.lat=46.32971126152109&SW.lng=39.375654626637704&NE.lat=46.329814730841335&NE.lng=39.37578337267041',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9C%D0%B0%D0%BB%D1%8C%D0%B4%D0%B8%D0%B2%D1%8B&price_per=1&id=101&SW.lat=1.9793903185840658&SW.lng=72.10806994999994&NE.lat=4.4389800699120645&NE.lng=74.21744494999992&type=country',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9F%D0%BE%D1%80%D0%BE%D1%88%D0%BA%D0%B8%D0%BD%D0%BE&price_per=1&id=1&SW.lat=59.99191586549477&SW.lng=28.95549568813293&NE.lat=60.59922542328349&NE.lng=30.01018318813294',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%A1%D0%BB%D0%B0%D0%B2%D1%8F%D0%BD%D1%81%D0%BA-%D0%BD%D0%B0-%D0%9A%D1%83%D0%B1%D0%B0%D0%BD%D0%B8&price_per=1&id=287945&SW.lat=45.19549313246032&SW.lng=38.04743903125002&NE.lat=45.303532955707794&NE.lng=38.17927496875001&type=city',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%91%D1%80%D0%B5%D1%81%D1%82&price_per=1&id=397903&SW.lat=51.99349953728543&SW.lng=23.577507062499958&NE.lat=52.181939372440205&NE.lng=23.84117893749996&type=city',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%90%D0%B4%D0%BB%D0%B5%D1%80&price_per=1&id=397369&SW.lat=43.322908494264254&SW.lng=39.82440951249997&NE.lat=43.54583101000978&NE.lng=40.088081387499976&type=city',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9C%D0%B0%D1%80%D0%B8%D1%83%D0%BF%D0%BE%D0%BB%D1%8C&price_per=1&id=398121&SW.lat=47.027835&SW.lng=37.46396&NE.lat=47.21859&NE.lng=37.755401&type=city',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9C%D1%83%D1%80%D0%BC%D0%B0%D0%BD%D1%81%D0%BA&price_per=1&id=337899&SW.lat=68.86333598429185&SW.lng=32.84982862499999&NE.lat=69.08304166153958&NE.lng=33.377172374999994&type=city',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9F%D0%B0%D1%80%D0%B3%D0%BE%D0%BB%D0%BE%D0%B2%D0%BE&price_per=1&id=405371&SW.lat=60.01034697560879&SW.lng=30.118329062500003&NE.lat=60.163151345969915&NE.lng=30.382000937500006&type=city',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%90%D0%BB%D1%83%D1%88%D1%82%D0%B0&price_per=1&id=397314&SW.lat=44.50408795926935&SW.lng=34.18842312499998&NE.lat=44.94026520244052&NE.lng=34.715766874999986&type=city',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9A%D0%B8%D1%80%D0%BE%D0%B2%D1%81%D0%BA&price_per=1&id=337904&SW.lat=67.56436732678561&SW.lng=33.5808945625&NE.lat=67.68093864446139&NE.lng=33.8445664375&type=city',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9B%D0%B0%D0%BD%D0%B3%D0%B5%D0%BF%D0%B0%D1%81&price_per=1&id=399068&SW.lat=61.18529303823396&SW.lng=75.0303030625&NE.lat=61.33261476831815&NE.lng=75.29397493749998&type=city',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9B%D0%B8%D0%BF%D0%B5%D1%86%D0%BA&price_per=1&id=330476&SW.lat=52.417782803385286&SW.lng=39.33218362499996&NE.lat=52.79026261922899&NE.lng=39.85952737499997&type=city',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%90%D1%80%D1%85%D1%8B%D0%B7&price_per=1&id=410738&SW.lat=43.49093138517124&SW.lng=41.20930253124995&NE.lat=43.60218448209667&NE.lng=41.34113846874997&type=city',
        # 'https://sutochno.ru/front/searchapp/search?occupied=2024-08-11;2024-08-12&guests_adults=1&term=%D0%9D%D0%B0%D1%80%D0%BE-%D0%A4%D0%BE%D0%BC%D0%B8%D0%BD%D1%81%D0%BA&price_per=1&id=334766&SW.lat=55.347439957531215&SW.lng=36.66462653124994&NE.lat=55.43450048761098&NE.lng=36.79646246874995&type=city',
    ]

    def get_flats_by_link(self, link):
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
                        [1, 14],
                        [1, 28]]
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
                count = ''.join(re.findall(r'(\d+)', text[4:pos]))
                dict_['count_beds'] = int(count) if count != '' else None

            # оснащение и площать
            elem = item.find('div', class_='card-content__facilities') 
            elems = elem.find_all('div')
            dict_['square'] = html_validate(elems[0], 'number')
            dict_['count_people'] = html_validate(elems[1], 'number')

            # спальные места
            dict_['sleeping_places'] = html_validate(to_parse.find('div', class_='object-data--sleeping-places'), 'number')

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
                dict_['count_reviews'] = 0
            else:
                num = html_validate(to_parse.find('div', class_='rating-top'), 'number')
                count = html_validate(to_parse.find('div', class_='count-reviews'), 'number')
                if count != None and num != None:
                    dict_['rating'] =  (float(num) / 10) // 1 if num else num
                    dict_['count_reviews'] = count if count < 100 else 100
                else:
                    dict_['rating'] = 0
                    dict_['count_reviews'] = 0

            
            flag = False
            for key in dict_.keys():
                if dict_[key] == None or dict_[key] == '': flag = True
            if flag: continue

            dict_['owner_id'] = self.user_id
            dict_['ad_id'] = self.ad_id
            if not (self.ad_id % 3):
                self.user_id += 1
            self.ad_id += 1

            flats.append(dict_)


        driver.quit()

        return flats

    def save_to_postgres(self, ads, reservations, reviews, ratings):
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

        for item in ads:
            cursor = connection.cursor()
            cursor.execute(
                f"""
                    INSERT INTO core_ad (
                        description,
                        img_src,
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
                        price,
                        owner_id
                    )
                    VALUES (
                        '{item['description']}',
                        '{item['img_src']}',
                        '{item['clock_entry']}',
                        '{item['clock_leave']}',
                        '{item['min_length_of_stay']}',
                        '{item['max_length_of_stay']}',
                        '{item['animal_check']}',
                        '{item['smoking_check']}',
                        '{item['party_check']}',
                        '{item['docs_check']}',
                        '{item['kids_check']}',
                        '{item['wifi']}',
                        '{item['drier']}',
                        '{item['towel']}',
                        '{item['bed_linen']}',
                        '{item['tv']}',
                        '{item['microwave']}',
                        '{item['electric_kettle']}',
                        '{item['balcony']}',
                        '{item['params']}',
                        '{item['count_beds']}',
                        '{item['square']}',
                        '{item['count_people']}',
                        '{item['sleeping_places']}',
                        '{item['beds_info']}',
                        '{item['type_flats']}',
                        '{item['short_desc']}',
                        '{item['address']}',
                        '{item['price']}',
                        '{item['owner_id']}'
                    )
                """
            )
            connection.commit()

        
        for item in ratings:
            cursor = connection.cursor()
            cursor.execute(
                f"""
                    INSERT INTO core_rating (
                        count_reviews,
                        sum_rating,
                        ad_id
                    )
                    VALUES (
                        '{int(item['count_reviews'])}',
                        '{int(item['sum_rating'])}',
                        '{item['ad_id']}'
                    )
                """
            )
            connection.commit()

        for item in reservations:
            cursor = connection.cursor()
            cursor.execute(
                f"""
                    INSERT INTO core_reservation (
                        begin_lease,
                        end_lease,
                        approve_status,
                        lease_end_status,
                        ad_id,
                        owner_id
                    )
                    VALUES (
                        '{item['begin_lease']}',
                        '{item['end_lease']}',
                        '{item['approve_status']}',
                        '{item['lease_end_status']}',
                        '{item['ad_id']}',
                        '{item['owner_id']}'
                    )
                """
            )
            connection.commit()
        
        for item in reviews:
            cursor = connection.cursor()
            cursor.execute(
                f"""
                    INSERT INTO core_review (
                        text,
                        rating,
                        reservation_id,
                        ad_id,
                        owner_id
                    )
                    VALUES (
                        '{item['text']}',
                        '{int(item['rating'])}',
                        '{item['reservation_id']}',
                        '{item['ad_id']}',
                        '{item['owner_id']}'
                    )
                """
            )
            connection.commit()


    def run(self):
        reservation_id = 8243
        with open('data.txt', 'w', encoding="utf-8") as file:
            for link in Parser.links_to_parse:
                flats_items = self.get_flats_by_link(link)
                
                ads = []
                reservations = []
                reviews = []
                ratings = []

                for item in flats_items:
                    file.write(f'//////////////////////////////////////\n')
                    for key in item.keys():
                        file.write(f'{str(key)}: {str(item[key])}\n')
                    file.write(f'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n\n')

                for ad in flats_items:
                    ads.append(ad)
                    rating = {
                        'count_reviews': ad['count_reviews'],
                        'sum_rating': ad['rating'] * ad['count_reviews'],
                        'ad_id': ad['ad_id']
                    }
                    ratings.append(rating)

                    first_rentor_id = random.randint(1067, 3000)
                    
                    month = random.randint(1, 12)
                    day = random.randint(1, 28)
                    first_date = datetime.date(2023, month, day)

                    for i in range(1, ad['count_reviews'] + 1):
                        reservation = {
                            'begin_lease': first_date + timedelta(i),
                            'end_lease': first_date + timedelta(i + 1),
                            'approve_status': True,
                            'lease_end_status': True,
                            'ad_id': ad['ad_id'],
                            'owner_id': first_rentor_id + (i-1)
                        }
                        text = reviews_generate()
                        review = {
                            'text': text,
                            'rating': ad['rating'],
                            'reservation_id': reservation_id,
                            'ad_id': ad['ad_id'],
                            'owner_id': first_rentor_id + (i-1)
                        }

                        reservation_id += 1

                        reservations.append(reservation)
                        reviews.append(review)

                self.save_to_postgres(ads, reservations, reviews, ratings)
                print(f'ссылка: {link}\nуспешно пройдена...')


Parser().run()

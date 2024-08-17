import time, re
import datetime
import pandas as pd
import requests
import random
import psycopg2
from sqlite3 import Error
from datetime import timedelta

def reviews_generate():
    time.sleep(0.5)
    try:
        params = f'&type={'sentence'}&number={random.randint(1, 4)}'
        response = requests.get(f'https://fish-text.ru/get?{params}')
        if response.status_code == 200:
            data = response.json()['text']
            print(data)
            return data
        else:
            print("Ошибка при получении ответа")
            return '7 бобров из 13 выдр и того 4 Динозавра Абрамовича'
    except:
        return '7 бобров из 13 выдр и того 4 Динозавра Абрамовича'
 
# 32
rating = [3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5]

comments = []

for p in range(0, 7):
    comments.append(reviews_generate())

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

for i in range(58, 3500):
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT id FROM core_ad WHERE id = {i}')
        if cursor.fetchone() == None:
            continue

        cursor.execute(f'SELECT price, count_people FROM core_ad WHERE id = {i}')
        price, count_people = cursor.fetchall()[0]

        print('Объявление ', i)

        print("    Генерим даты")
        dates_range = pd.date_range(start="2024-05-01",end="2024-10-13").to_pydatetime().tolist()
        dates = []
        for k in range(0, len(dates_range) - 1):
            dates.append([dates_range[k], dates_range[k + 1]])

        count_reviews = random.randint(3, 69)
        sum_rating = 0
        print(f'    Количество отзывов {count_reviews}')

        for j in range(1, count_reviews):
            date = dates[random.randint(0, len(dates) - 1)]
            dates.remove(date)

            # генерим брони и отзывы
            # берём рандомного юзера убедившись что он еесть в базе
            rentor_id = 0
            while True:
                id = random.randint(1067, 3250)
                cursor.execute(f'SELECT id FROM auth_user WHERE id = {id}')
                if cursor.fetchone() != None:
                    rentor_id = id
                    break

            print('     Юзер ', rentor_id, i)

            lease = True if date[0] < datetime.datetime.today() else False
            try:
                cursor.execute(
                    f"""
                        INSERT INTO core_reservation (
                            begin_lease,
                            end_lease,
                            count_people,
                            approve_status,
                            lease_end_status,
                            ad_id,
                            owner_id
                        )
                        VALUES (
                            '{date[0].date()}',
                            '{date[1].date()}',
                            '{count_people}',
                            '{True}',
                            '{lease}',
                            '{i}',
                            '{rentor_id}'
                        )
                        returning id
                    """
                )
                reservation_id = cursor.fetchone()[0]
            except Error:
                print('Не удалось создать бронь ')
                # exit()

            if lease: 
                rate = rating[random.randint(0, len(rating) - 2)]
                sum_rating += rate
                try:
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
                                '{comments[random.randint(0, len(comments) - 1)]}',
                                '{rate}',
                                '{reservation_id}',
                                '{i}',
                                '{rentor_id}'
                            );
                            INSERT INTO core_paymentreceipt (
                                sum,
                                reservation_id
                            )
                            VALUES (
                                '{price*count_people}',
                                '{reservation_id}'
                            )
                        """
                    )
                except:
                    print('Не удалось создать отзыв')

        try:
            cursor.execute(
                f"""
                    UPDATE core_rating SET sum_rating = {sum_rating}, count_reviews = {count_reviews} WHERE ad_id = {i};
                """
            )
        except:
            print('error') 
            exit()

        connection.commit()

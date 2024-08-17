import requests
import random 
import time
from transliterate import translit

url = 'http://127.0.0.1:8000/api/account/register/'

first_name = []
last_name = []

with open("first_name.txt", "r", encoding="utf-8") as file:
    for line in file:
        first_name.append(line[:-1])

with open("last_name.txt", "r", encoding="utf-8") as file:
    for line in file:
        last_name.append(line[:-1])

count = 1
with open('rentor_logins.txt', 'w', encoding='utf-8') as file:
    for i in range(5000):
        user_first_name = first_name[random.randint(0, (len(first_name) - 1))]
        user_last_name = last_name[random.randint(0, (len(last_name) - 1))]

        username = translit(
            f'{str.lower(user_first_name)}_{str.lower(user_last_name)}',
            language_code='ru',
            reversed=True
        )
        email = translit(f'{username}@mail.com', language_code='ru', reversed=True)

        data = {
            "username": username,
            "first_name": user_first_name,
            "last_name": user_last_name,
            "email": email,
            "password": "Monin1324",
            "groups": [2]
        }

        response = requests.post(url, data=data)

        if response:
            print(f'{count} - зарегистрирован')
            file.write(f'{username}\n')
            count += 1

        time.sleep(1)
    
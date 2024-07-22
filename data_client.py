import sqlite3
from sqlite3 import Error
# pip install psycopg2
import psycopg2
from abc import ABC, abstractmethod


class DataClient(ABC):
    @abstractmethod
    def get_connection(self):
        pass

    @abstractmethod
    def create_flats_table(self, conn):
        pass

    @abstractmethod
    def get_items(self, conn, price_from=0, price_to=100000):
        pass

    @abstractmethod
    def insert(self, conn, item):
        pass


class PostgresClient(DataClient):
    USER = "postgres"
    PASSWORD = "0000"
    HOST = "localhost"
    PORT = "5432"

    def get_connection(self):
        try:
            connection = psycopg2.connect(
                user=self.USER,
                password=self.PASSWORD,
                host=self.HOST,
                port=self.PORT
            )
            return connection
        except Error:
            print(Error)

    def create_flats_table(self, conn):
        cursor_object = conn.cursor()
        cursor_object.execute(
            """
                CREATE TABLE IF NOT EXISTS api_flats_ads
                (
                    id serial PRIMARY KEY, 
                    img_src text, 
                    type_flats text, 
                    description text,
                    address text,
                    count_bed text,
                    price int
                )
            """
        )
        conn.commit()

    def get_items(self, conn, price_from=0, price_to=100000):
        pass

    def insert(self, conn, item):
        cursor = conn.cursor()
        cursor.execute(
            f"""
                INSERT INTO api_flats_ads (
                    img_src,
                    type_flats,
                    description,
                    address,
                    count_bed,
                    price
                )
                VALUES (
                '{item['img_src']}',
                '{item['type_flats']}',
                '{item['description']}',
                '{item['address']}',
                '{item['count_bed']}',
                '{int(item['price'])}'
                )
            """
        )
        conn.commit()

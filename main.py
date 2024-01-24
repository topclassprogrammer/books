import json
import os
import sys

from environs import Env
from sqlalchemy import create_engine, exc
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker

from models import Publisher, Book, Stock, Shop, Sale, create_tables


DB_DATA = 'db_data.json'

env = Env()
env.read_env()
PROTOCOL = env('PROTOCOL')
USER = env('USER')
PASSWORD = env.int('PASSWORD')
HOST = env('HOST')
PORT = env.int('PORT')
DB_NAME = env('DB_NAME')


def create_db():
    try:
        DSN = f"{PROTOCOL}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
        engine = create_engine(DSN)
        if not database_exists(engine.url):
            create_database(engine.url)
        Session = sessionmaker(bind=engine)
        global session
        session = Session()
        create_tables(engine)
    except (exc.OperationalError,
            exc.ArgumentError) as err:
        print('Incorrect DSN string', err)
        sys.exit()


def read_json():
    if DB_DATA not in os.listdir():
        print(f'DB data file name {DB_DATA} '
              f'not found in the project folder {os.getcwd()}')
        sys.exit()
    with open(DB_DATA, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError as err:
            print(f'Incorrect JSON data in {DB_DATA}', err)
            sys.exit()
    return data


def make_rows():
    try:
        for el in read_json():
            if 'publisher' in el['model']:
                session.add(Publisher(name=el['fields']['name']))
            elif 'book' in el['model']:
                session.add(Book(title=el['fields']['title'],
                                 id_publisher=el['fields']['id_publisher']))
            elif 'shop' in el['model']:
                session.add(Shop(name=el['fields']['name']))
            elif 'stock' in el['model']:
                session.add(Stock(id_book=el['fields']['id_book'],
                                  id_shop=el['fields']['id_shop'],
                                  count=el['fields']['count']))
            elif 'sale' in el['model']:
                session.add(Sale(price=el['fields']['price'],
                                 date_sale=el['fields']['date_sale'],
                                 id_stock=el['fields']['id_stock'],
                                 count=el['fields']['count']))
    except KeyError as err:
        print(f'Incorrect key {err} while trying to get it in '
              f'FOR loop')
        sys.exit()
    session.commit()


def get_shops(user_input):
    common_query = session.query(Book, Shop, Sale, Stock).select_from(Shop).\
        join(Stock).join(Book).join(Publisher).join(Sale)
    if user_input.isdigit():
        input_query = common_query.filter(Publisher.id == user_input)
    else:
        input_query = common_query.filter(Publisher.name == user_input)
    if len(input_query.all()) == 0:
        return print('Nothing found')
    for book, shop, sale_price, sale_date in input_query:
        print(f"{book.title: <40} | {shop.name: <10} | {sale_price.price: <8}"
              f" | {sale_price.date_sale.strftime('%d-%m-%Y')}")


if __name__ == '__main__':
    create_db()
    read_json()
    make_rows()
    user_input = input("Enter the publisher's ID or its name "
                       "to show information: ")
    get_shops(user_input)

import json
import os
import sys
import sqlalchemy.exc
from configparser import ConfigParser
from prettytable import PrettyTable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Publisher, Book, Stock, Shop, Sale, create_tables

if __name__ == '__main__':
    credentials_file_name = 'db_credentials.ini'
    if credentials_file_name not in os.listdir():
        print(f'DB credentials file name {credentials_file_name} '
              f'not found in the project folder {os.getcwd()}')
        sys.exit()
    parser = ConfigParser()
    try:
        parser.read(credentials_file_name)
        DSN = (f"{parser['db']['protocol']}://{parser['db']['user']}:"
               f"{parser['db']['password']}@{parser['db']['host']}:"
               f"{parser['db']['port']}/{parser['db']['db_name']}")
        engine = create_engine(DSN)
        Session = sessionmaker(bind=engine)
        session = Session()
        create_tables(engine)
    except KeyError as err:
        print(f'Incorrect key {err} in DSN string')
        sys.exit()
    except sqlalchemy.exc.OperationalError as err:
        print(f'Incorrect data in {credentials_file_name}', err)
        sys.exit()

    db_data_file_name = 'db_data.json'
    if db_data_file_name not in os.listdir():
        print(f'DB data file name {db_data_file_name} '
              f'not found in the project folder {os.getcwd()}')
        sys.exit()
    with open(db_data_file_name, 'r', encoding='utf-8') as f:
        try:
            json_data = json.load(f)
        except json.decoder.JSONDecodeError as err:
            print(f'Incorrect JSON data in {db_data_file_name}', err)
            sys.exit()
    try:
        for el in json_data:
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

    while True:
        try:
            input_id = int(input("Enter the publisher's ID "
                                 "to show its information: "))
        except ValueError:
            print("You haven't entered a number. Please try again")
        else:
            break

    subq = session.query(Book.id).filter(Book.id_publisher ==
                                         input_id).subquery()
    stock_ids = session.query(Stock.id).join(subq, subq.c.id ==
                                             Stock.id_book).all()
    res = []
    for stock_id in stock_ids:
        stock_id = stock_id[0]
        book_titles = session.query(Book.title).join(Stock).filter(
            Stock.id == stock_id).all()[0][0]
        shop_names = session.query(Shop.name).join(Stock).filter(
            Stock.id == stock_id).all()[0][0]
        prices = float(session.query(Sale.price).filter(
            Sale.id_stock == stock_id).all()[0][0])
        date_sales = str(session.query(Sale.date_sale).filter(
            Sale.id_stock == stock_id).all()[0][0].date())
        res.append(book_titles)
        res.append(shop_names)
        res.append(prices)
        res.append(date_sales)
    session.close()

    table = PrettyTable()
    table.header = False
    table.border = False
    table.preserve_internal_border = True
    table.hrules = 2
    table.align = 'l'
    for i in range(len(stock_ids)):
        i = i * 4
        j = i + 4
        table.add_row(res[i:j])
    print(table)

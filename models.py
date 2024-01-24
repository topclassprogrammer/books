from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Publisher(Base):
    __tablename__ = 'publisher'
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    books = relationship('Book', backref='publisher')


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    id_publisher = Column(Integer, ForeignKey('publisher.id'), nullable=False)
    stock = relationship('Stock', backref='books')


class Stock(Base):
    __tablename__ = 'stock'
    id = Column(Integer, primary_key=True)
    id_book = Column(Integer, ForeignKey('book.id'), nullable=False)
    id_shop = Column(Integer, ForeignKey('shop.id'), nullable=False)
    count = Column(Integer)
    sales = relationship('Sale', backref='stock')


class Shop(Base):
    __tablename__ = 'shop'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    stock = relationship('Stock', backref='shops')


class Sale(Base):
    __tablename__ = 'sale'
    id = Column(Integer, primary_key=True)
    price = Column(Numeric(5, 2), nullable=False)
    date_sale = Column(DateTime)
    id_stock = Column(Integer, ForeignKey('stock.id'), nullable=False)
    count = Column(Integer)


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

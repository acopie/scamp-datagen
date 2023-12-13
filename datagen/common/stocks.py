"""
This file contains the elements related to product stocks in the data generator

@author: Adrian
"""

from typing import Any


class Acquisition:
    """
    A single acquisition of a certain quantity of a product scheduled for a certain date
    """

    def __init__(self, next_delivery_date, quantity):
        self.next_delivery_date = next_delivery_date
        self.quantity = quantity


class Stock:
    """
    Class representing a stock related to a certain product
    """

    def __init__(self, id, code, pname, quantity, acquisitions=None):
        self.id = id
        self.code = code
        self.pname = pname
        self.quantity = quantity
        if acquisitions is None:
            self.acquisitions = []
        else:
            self.acquisitions = acquisitions

    def __str__(self) -> str:
        return f"Stock(id={self.id}, code={self.code}, " \
               f"pname={self.pname}, quantity={self.quantity}, " \
               f"next_delivery_date={self.next_delivery_date})"

    def __repr__(self) -> str:
        return self.__str__()


class Stocks:
    """
    Class representing the collection of stocks in the system, together with some manipulation methods
    """

    # holds all the stocks in the system
    stocks = []

    _instance: object = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __eq__(self, other: Any):
        if not isinstance(other, Stock):
            return NotImplemented

        return self.id == other.id and \
               self.code == other.code and \
               self.pname == other.pname and \
               self.quantity == other.quantity and \
               self.next_delivery_date == other.next_delivery_date

    def __hash__(self):
        return hash((self.id, self.code, self.pname, self.quantity, self.next_delivery_date))

    @classmethod
    def add(cls, stock: Stock) -> None:
        cls.stocks.append(stock)

    @classmethod
    def get(cls, stock):
        if stock in cls.stocks:
            return stock

    def get_by_id(self, id):
        for stock in self.stocks:
            if stock.id == id:
                return stock

        return None

    def reset(self):
        Stocks.stocks.clear()

    def __str__(self) -> str:
        return f"Stocks(stocks={self.stocks}, index={self.index})"

    def __repr__(self) -> str:
        return self.__str__()

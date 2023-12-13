"""
This module is related to the stocks generation for multi-boms in the data generator.

@author: Adrian
"""

import random
import os

from typing import List
from json import JSONEncoder, JSONDecoder, dumps, load

from datagen.common.sequencer import Sequencer
from datagen.common.utility import get_abs_file_path

from datagen.common.stocks import Stock, Acquisition, Stocks
from datagen.common.stockgenb import StockGeneratorBase
from datagen.multi.utility import create_future_date
from datagen.multi.bom import MultiBom

RAW_MATERIALS_PERCENT = 0.2


class StockGeneratorMulti(StockGeneratorBase):

    def __init__(self, multi_bom):
        super().__init__(multi_bom)
        StockGeneratorMulti.multi_bom = multi_bom

    @classmethod
    def generate_stocks(cls, multi_bom: MultiBom) -> None:
        """
        Generates  the available stocks in the system. We assume that the raw materials are only
        a specified percentage of the total products in the system, so we firstly look to see
        how many products do we have, then we compute the number of products that we consider
        to be raw materials, and we generate them.
        """

        # we want to store the stocks in a Stocks object which is a singleton class
        stocks = Stocks()

        for i in range(int(multi_bom.machines_info.prod_number * RAW_MATERIALS_PERCENT)):
            next_supply_date = create_future_date()
            next_supply_date_str = next_supply_date.strftime("%d-%m-%Y %H:%M:%S")
            acquisition = Acquisition(next_supply_date_str, random.randint(10, 100))

            new_stock = Stock(Sequencer().index, cls.code(4),
                              cls.code(4), random.randint(10, 100),
                              [acquisition])
            stocks.add(new_stock)

            cls.stocks.append(new_stock)

    @classmethod
    def export(cls, multi_bom):
        """
        Exports all the stocks in a json file for further usage
        """

        class StockEncoder(JSONEncoder):
            def default(self, o):
                return o.__dict__

        encoder = StockEncoder()

        current_directory = os.getcwd()

        with open(get_abs_file_path(f"multiboms/{multi_bom.machines_info.root_directory}/stocks.json"), "w") as f:
            f.write(dumps(cls.stocks, default=lambda o: o.__dict__, indent=4))

    @classmethod
    def import_stocks(cls, multi_bom):
        """
        Imports all the stocks from a json file
        """

        class StockDecoder(JSONDecoder):
            def decode(self) -> List[Stock]:
                decoded_stocks = []

                with open(f"../multiboms/{multi_bom.machines_info.root_directory}/stocks.json") as f:
                    stocks_list = load(f)

                    for crt_stock in stocks_list:
                        vals = crt_stock.values()
                        stock = Stock(*vals)
                        decoded_stocks.append(stock)

                return decoded_stocks

        decoder = StockDecoder()
        cls.stocks = decoder.decode()


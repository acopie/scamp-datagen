"""
This module is the base class for the stocks generation in the data generator.

@author: Adrian
"""
import random
import os
import string

from abc import ABC, abstractmethod
from typing import List
from json import JSONEncoder, JSONDecoder, dumps, load

from datagen.common.sequencer import Sequencer
from datagen.common.utility import get_abs_file_path

from datagen.common.stocks import Stock, Acquisition, Stocks
from datagen.multi.randpgen import Product
from datagen.multi.utility import create_future_date
from datagen.multi.bom import MultiBom

RAW_MATERIALS_PERCENT = 0.2


class StockGeneratorBase(ABC):
    # CLASS LEVEL VARIABLES

    # holds all the stocks in the system
    stocks = list()

    # the Bom object which is related to the raw materials stocks to be generated
    bom = None

    def __init__(self, bom):
        StockGeneratorBase.bom = bom

    @classmethod
    def code(cls, length: int) -> str:
        # choose from all lowercase letter
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters.upper()) for i in range(length))

    @classmethod
    @abstractmethod
    def generate_stocks(cls, multi_bom: MultiBom) -> None:
        """
        Generates  the available stocks in the system. We assume that the raw materials are only
        a specified percentage of the total products in the system, so we firstly look to see
        how many products do we have, then we compute the number of products that we consider
        to be raw materials, and we generate them.
        """

        # we want to store the stocks in a Stocks object which is a singleton class
        raise NotImplementedError

    @classmethod
    def sample_products(cls, products: List[Product], number: int):
        """
        Samples a number of products from the available products
        :param products: the available products
        :param number: the number of products to be sampled
        :return: the sampled products
        """

        raw_materials = random.sample(products, number)

    @classmethod
    @abstractmethod
    def export(cls, bom):
        """
        Exports all the stocks in a json file for further usage
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def import_stocks(cls, bom):
        """
        Imports all the stocks from a json file
        """

        raise NotImplementedError


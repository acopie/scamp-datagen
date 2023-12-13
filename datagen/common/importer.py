"""
Class used to deal with the entries generated in the products.json file. It contains the support for deserialization
and creating objects of SProduct type

@author Adrian
"""

import json
from json import JSONDecoder
from typing import List, Type

from datagen.common.utility import get_abs_file_path

from datagen.mono.productgenerator import Product


class SProduct:
    """
    Class modelling a product that will be used as an entry in the BOM tree
    """
    def __init__(self, pid: int, code: str, pname: str, machines: List = None):
        self.productid = pid
        self.code = code
        self.pname = pname
        if machines is None:
            self.machines = []
        else:
            self.machines = machines

    def __eq__(self, o: Type['Product']) -> bool:
        """
        Overrides the default __eq__ method in order to provide uniqueness in collections
        """
        if isinstance(o, Product):
            return (self.pname == o.pname) and (self.productid == o.productid) and (self.code == o.code)
        else:
            return False

    def __hash__(self):
        """
        Overrides the default __hash__ method of the object class, used to define uniqueness in collections
        """
        return hash(self.productid, self.code)


class SProductDecoder(JSONDecoder):
    """
    Helper class used to deserialize the entries in the products.json file
    """

    def decode(self) -> List[SProduct]:
        decoded_products = []

        with open(get_abs_file_path("boms/products.json")) as f:
            products_list = json.load(f)

            for crt_prod in products_list:
                vals = crt_prod.values()
                product = SProduct(*vals)
                decoded_products.append(product)

        return decoded_products


if __name__ == "__main__":
    decoder = SProductDecoder()
    products = decoder.decode()

    for p in products:
        print(p.pname)

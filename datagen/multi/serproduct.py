from typing import List, Type
from json import JSONDecoder, load

from datagen.common.utility import get_abs_file_path

PRODUCTS_FILE = "temp/rand_products.json"


class SerializableProduct:
    """
    Class modelling a product that will be used as an entry in the BOM tree
    """

    def __init__(self, pid: int, code: str, pname: str, machines: List = None):
        # the product id
        self.pid: int = pid
        self.code: str = code
        self.pname: str = pname

        if machines is None:
            self.machines = []
        else:
            self.machines = machines

    def __eq__(self, o: Type['SerializableProduct']) -> bool:
        """
        Overrides the default __eq__ method in order to provide uniqueness in collections
        """
        if isinstance(o, SerializableProduct):
            return (self.pname == o.pname) and (self.pid == o.pid) and (self.code == o.code)
        else:
            return False

    def __hash__(self):
        """
        Overrides the default __hash__ method of the object class, used to define uniqueness in collections
        """
        return hash(self.pid, self.code)


class SerializableProductDecoder(JSONDecoder):
    """
    Helper class used to deserialize the entries in the rand_products.json file
    """

    def __init__(self, multibom):
        super().__init__()
        self.multibom = multibom

    def decode(self) -> List[SerializableProduct]:
        decoded_products = []

        with open(get_abs_file_path(f"multiboms/{self.multibom.machines_info.root_directory}/rand_products.json")) as f:
            products_list = load(f)

            for crt_prod in products_list:
                vals = crt_prod.values()
                product = SerializableProduct(*vals)
                decoded_products.append(product)

        return decoded_products

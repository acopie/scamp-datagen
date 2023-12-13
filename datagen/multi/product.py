from typing import List, Any
from json import JSONEncoder, JSONDecoder, load, dumps

from datagen.common.utility import get_abs_file_path

from datagen.multi.machines import Machine

PRODUCTS_FILE = "temp/rand_products.json"


class Product:
    """
    Class representing a product
    """

    def __init__(self, id, code, pname, machines: List = None):
        self.id = id
        self.code = code
        self.pname = pname

        if machines is None:
            setattr(self, 'machines', [])
        else:
            if not hasattr(self, 'machines'):
                setattr(self, 'machines', [])

            for entry in machines:
                if isinstance(entry, dict):
                    self.machines.append(Machine(entry.get("id"), entry.get("name"), entry.get("oee")))
                else:
                    self.machines.append(Machine(entry.id, entry.name, entry.oee))

        self.machines.sort(key=lambda M: M.id)

    def __str__(self) -> str:
        return f"Product(id={self.id}, code={self.code}, pname={self.pname})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: Any):
        if not isinstance(other, Product):
            return NotImplemented

        return self.id == other.id and \
            self.code == other.code and \
            self.pname == other.pname

    def __hash__(self):
        """
        Overrides the default __hash__ method of the object class, used to define uniqueness in collections
        """
        return hash(self.id, self.code)


class ProductEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class ProductDecoder(JSONDecoder):

    def decode(self) -> List[Product]:
        decoded_products = []

        with open(get_abs_file_path(PRODUCTS_FILE)) as f:
            products_list = load(f)

            for crt_prod in products_list:

                machines = []
                for crt_machine in crt_prod.get("machines"):
                    # machine = Machine(**crt_machine)
                    # machines.append(machine)
                    machines.append(crt_machine)

                product = Product(crt_prod.get("id"), crt_prod.get("code"), crt_prod.get("pname"), machines)
                decoded_products.append(product)

        return decoded_products

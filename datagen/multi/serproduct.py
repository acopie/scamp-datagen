# datagen/multi/serproduct.py
import os
from typing import List, Optional, Type
from json import JSONDecoder, load

from datagen.common.utility import get_abs_file_path


class SerializableProduct:
    def __init__(self, pid: int, code: str, pname: str, machines: List = None):
        self.pid: int = pid
        self.code: str = code
        self.pname: str = pname
        self.machines = [] if machines is None else machines

    def __eq__(self, o: Type['SerializableProduct']) -> bool:
        if isinstance(o, SerializableProduct):
            return (self.pname == o.pname) and (self.pid == o.pid) and (self.code == o.code)
        return False

    def __hash__(self):
        return hash((self.pid, self.code))


class SerializableProductDecoder(JSONDecoder):
    def __init__(self, multibom):
        super().__init__()
        self.multibom = multibom

    def decode(self, products_path: Optional[str] = None) -> List["SerializableProduct"]:
        if products_path:
            open_path = products_path if os.path.isabs(products_path) else get_abs_file_path(products_path)
        else:
            open_path = get_abs_file_path(
                f"multiboms/{self.multibom.machines_info.root_directory}/rand_products.json"
            )

        if not os.path.exists(open_path):
            raise FileNotFoundError(f"products_source not found: {open_path}")

        with open(open_path, "r", encoding="utf-8") as f:
            products_list = load(f)

        decoded_products: List[SerializableProduct] = []
        for crt_prod in products_list:
            # presupune cheile în ordine (pid, code, pname, machines), ca în rand_products.json existent
            vals = list(crt_prod.values())
            product = SerializableProduct(*vals)
            decoded_products.append(product)

        return decoded_products

from json import JSONEncoder, dumps
from typing import Any

from .boms_processing import BomDecoder, Boms
from .sequencer import Sequencer


class OrderEncoder(JSONEncoder):

    def encode(self, o: Any) -> str:
        return o.__dict__


class Order(object):

    def __init__(self, id, product_id, product_name, quantity, delivery_date):
        self.id = id
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.delivery_date = delivery_date

    def export(self, output_file: str) -> None:
        encoder = OrderEncoder()

        with open(output_file, "w") as f:
            f.write(dumps(encoder.encode(self), indent=4))


if __name__ == "__main__":
    # generate the list of all the BOMs defined in the system
    BomDecoder.build()

    # now, let's take one of the BOMs in the list and generate it
    bom = Boms.get_bom("First BOM")

    order = Order(Sequencer().index, )

from json import JSONEncoder, dumps
from typing import List, Dict, Any

from datagen.multi.utility import save_metainfo
from datagen.multi.prodmachine import ProdMachines, ProdMachinesAll


class MetaInfo(object):
    """
    Singleton that holds info about the products and machines involved in the BOM

    @author Adrian
    """
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    @classmethod
    def export(cls, metainfo) -> None:
        """
        Exports the meta information for a BOM in a json file for further usage
        :return: None
        """
        class Encoder(JSONEncoder):
            def encode(self, obj) -> Dict[str, Any]:
                return obj.__dict__

        save_metainfo(f"metainfo.json", metainfo)

    def add_product(self, prodid: int) -> None:
        if not hasattr(self, 'products'):
            setattr(self, 'products', [])

        self.products.append(prodid)

    def add_operation(self, opid: int) -> None:
        """
        Adds the operation meta information in the BOM
        """
        if not hasattr(self, 'operations'):
            # the field below is added on a post-creation phase, it is not declared in the constructor
            self.operations = []

        self.operations.append(opid)

    def add_machine(self, machineid: int) -> None:
        """
        Adds the machines involved in the fabrication of the product described in BOM
        """
        if not hasattr(self, 'machines'):
            setattr(self, 'machines', [])

        # add the attributes below outside the constructor, in a late decoration phase
        self.machines.append(machineid)
        self.machines = list(set(self.machines))

    def add_prod_machines(self, prodid: int, machines: List[int]) -> None:
        """
        Adds the machines involved in the fabrication of the product described in BOM
        """
        if not hasattr(self, 'prod_machines'):
            # the field below is added on a post-creation phase, it is not declared in the constructor
            self.prod_machines = []

        prod_machines = ProdMachines(prodid, machines)
        self.prod_machines.append(prod_machines)

    def add_metainfo(self, product, opid):
        self.add_operation(opid)

        for m in product.machines:
            self.add_machine(m.get("id"))

    def reset_operations(self):
        """
        Clears the operations list
        """
        if hasattr(self, 'operations'):
            self.operations.clear()

    def reset_machines(self):
        """
        Cleans the machines list
        """
        if hasattr(self, 'machines'):
            self.machines.clear()

    def get_products(self):
        """
        Gathers the list of all products
        """
        return self.products

    def get_operations(self):
        """
        Gathers the list of all operations
        """
        return self.operations

    def get_machines(self):
        """
        Gathers the list of all machines
        """
        return self.machines

    def get_prod_machines(self):
        """
        Gathers the list of all machines
        """
        return self.prod_machines

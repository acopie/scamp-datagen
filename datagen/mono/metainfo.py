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

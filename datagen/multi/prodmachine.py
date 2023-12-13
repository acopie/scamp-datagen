class ProdMachines:

    def __init__(self, id, machines):
        self.productid = id
        self.machines = machines

    def __eq__(self, other):
        if isinstance(other, ProdMachines):
            return (self.productid == other.productid) and (self.machines == other.machines)
        else:
            return False

    def __hash__(self):
        combined_attributes = str(self.productid) + str(self.machines)
        return hash(combined_attributes)


class ProdMachinesAll:

    all_prods_machines = []

    @classmethod
    def add(cls, prod_machines):
        cls.all_prods_machines.append(prod_machines)
        cls.all_prods_machines = list(set(cls.all_prods_machines))

    @classmethod
    def get(cls):
        return sorted(cls.all_prods_machines, key=lambda x: x.productid)

    @classmethod
    def reset(cls):
        cls.all_prods_machines.clear()
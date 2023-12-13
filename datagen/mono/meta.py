from json import JSONEncoder, dumps
from typing import Any


class Meta:
    """
    Meta information which decorates the root node in BOM
    """
    def __init__(self, operations_list, machines_list, maintenances):
        self.operations_list = operations_list
        self.machines_list = machines_list
        self.maintenances = maintenances

    def __str__(self):
        encoder = MetaEncoder()
        return dumps(encoder.encode(self))


class MetaEncoder(JSONEncoder):

    def default(self, o: Any) -> str:
        return o.__dict__

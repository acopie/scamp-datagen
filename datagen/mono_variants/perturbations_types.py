from enum import StrEnum, auto

class OperationGraphPerturbationParam(object):
    """
    Stores the operation graph perturbation parameters
    """

    class OPERATION_GRAPH_PERTUBATION(StrEnum):
        ADD_LEAF_OPERATION = auto() #add leaf nodes to any node from operation graph
        REMOVE_LEAF_OPERATION = auto() #remove nodes from the leaf nodes of the operation graph


    def __init__(self, dct):
        self.type = dct["type"]
        self.value_type = dct["value_type"]
        self.value = dct["value"]

class MachinesAssignmentPerturbationsParams(object):
    """
    Stores the machine assignment perturbation parameters
    """

    class MACHINE_ASSIGNMENT_PERTUBATION(StrEnum):
        REASSIGN = auto()  # gets information regarding machine number and alternatives from initial instance and generates new assignment
        NEW_MACHINE_CONFIGURATION = auto()  # (machine no, min_alternatives, max_alternatives)

    def __init__(self, dct):
        self.type = dct["type"]

        # attributes used by NEW_MACHINE_CONFIGURATION
        self.machine_no = dct["machine_no"] if 'machine_no' in dct else None

        # attributes used by NEW_MACHINE_CONFIGURATION
        self.modified_operations_percentage = dct["modified_operations_percentage"] / 100. if 'modified_operations_percentage' in dct else 0.5
        self.favor_machine_alternatives_increase_percentage = dct["favor_machine_alternatives_increase_percentage"] / 100 if 'favor_machine_alternatives_increase_percentage' in dct else 0.5

        self.min_alternatives = dct["min_alternatives"] if 'min_alternatives' in dct else None
        self.max_alternatives = dct["max_alternatives"] if 'max_alternatives' in dct else None
from datagen.multi.machineinfo import SetupTime, UnitAssemblyTime
from datagen.multi.quantity import Quantity
import json
from anytree.importer import JsonImporter
from datagen.mono.gentree import render_tree
from anytree import  PreOrderIter, Node

class Instance(object):
    node_index = 0 #needed to create the anytree object

    def __init__(self, input_file_path : str, seed: int = None):
        self.input_file_path : str = input_file_path
        self.seed = seed
        self.quantity : Quantity = None
        self.setup_time : SetupTime = None
        self.unit_assembly_time : UnitAssemblyTime = None
        self.machines_alternatives : int = 1
        self.operation_id_list : list = []
        self.machine_id_list : list = []
        self.nodes_number = 0
        self.maintenances_list = []
        self.load_instance()

    def get_any_tree(self) -> Node:
        with open(self.input_file_path, 'r') as file:
            instance = json.load(file)
            # load anyTree instance from file
        return JsonImporter().import_(json.dumps(instance))

    def load_instance(self):
        """
        Load existing information from the instance input file
        """

        self.any_tree = self.get_any_tree()
        quantities = []
        setup_times = []
        execution_times = []
        machine_alternatives = []
        for node in PreOrderIter(self.any_tree):
            self.nodes_number += 1
            quantities.append(node.quantity)
            machine_alternatives.append(len(node.machines))
            for m in node.machines:
                setup_times.append(m['setup_time'])
                execution_times.append(m['execution_time'])

        self.quantity = Quantity({'min':min(quantities), 'step':1, 'max':max(quantities)}, seed= self.seed)
        self.machines_alternatives = max(machine_alternatives)
        self.setup_time = SetupTime(min(setup_times),max(setup_times), 1, 'seconds', seed= self.seed)
        self.unit_assembly_time = UnitAssemblyTime(min(execution_times), max(execution_times),1, 'seconds', seed= self.seed)

        self.operation_id_list = self.any_tree.metainfo['operations_list']
        self.machine_id_list = self.any_tree.metainfo['machines_list']
        self.maintenances_list = self.any_tree.metainfo['maintenances']

        render_tree( self.any_tree)

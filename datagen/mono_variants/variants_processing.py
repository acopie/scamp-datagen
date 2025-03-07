"""
This class deals with the configuration file used to generate variants of instances starting from an existing instance.

Basically it deserializes the variants.json file and make all the params available for the data generator

@author Flavia Micota
"""

import json
import logging
from json import JSONDecoder
from datagen.common.utility import get_abs_file_path
from datagen.mono_variants.load_instance import Instance
from datagen.mono_variants.perturbations_types import OperationGraphPerturbationParam, MachinesAssignmentPerturbationsParams
from enum import StrEnum, auto
from anytree import Node, PreOrderIter
from datagen.multi.quantity import Quantity
import random

log = logging.getLogger("main")

class VALUE_TYPE(StrEnum):
    ABSOLUTE = auto()
    PERCENTAGE = auto()

class PerturbationVariant(object):
    """
    Models the parameters needed for generating a variant.
    NOTE: In this version is important to keep the order of the parameters defined in variants.json with the
            list of parameters in the Variant constructor
    """

    def __init__(self,
                 initial_instance_path: str,
                 seed: int,
                 generated_instances_number: int,
                 generated_instances_path: str,
                 generated_instances_name: str
                 ):
        # the instance file from which variants are generated
        self.initial_instance_path: str = initial_instance_path

        # seed used to initialize the random generator
        self.seed: int = seed

        #the number of vaiants files generated from the initial instance file
        self.generated_instances_number: int = generated_instances_number

        self.generated_instances_path = generated_instances_path

        #the name of generated instances files
        self.generated_instances_name: str = generated_instances_name

class PertubationOperationGraph(PerturbationVariant):
    """
    The perturbation is done on operation graph structure.
    """

    def __init__(self,
                 initial_instance_path: str,
                 seed: int,
                 generated_instances_number: int,
                 generated_instances_path : str,
                 generated_instances_name: str,
                 perturb_operations_graph: OperationGraphPerturbationParam
                 ):
        super().__init__(initial_instance_path,
                         seed,
                         generated_instances_number,
                         generated_instances_path,
                         generated_instances_name,
                         )
        self.perturb_operations_graph: OperationGraphPerturbationParam = perturb_operations_graph
        random.seed(self.seed)

    def __add_nodes(self, nodes_no: int, instance: Instance, op_net: Node):
        """
        Private function that adds a number of leaf nodes equal to nodes_no to any operation network
        :param nodes_no: the number of leaf nodes that are added
        :param instance: the initial problem instance
        :param op_net:  root node of the operations network
        """
        initial_nodes = [node for node in PreOrderIter(op_net)]
        random.shuffle(initial_nodes)

        #get last operation ID in order to generate from there new IDs
        last_op_id = max(instance.operation_id_list) + 1
        for operationid in range(last_op_id, last_op_id + nodes_no):
            # select the node to add child
            selected_node_index = random.randint(0, instance.nodes_number - 1)
            op_net.metainfo['operations_list'].append(operationid)

            # build the new node
            machines_list = []
            for it in range(random.randint(1, instance.machines_alternatives)):
                machine_id = random.randint(min(instance.machine_id_list), max(instance.machine_id_list))
                machines_list.append({'id': machine_id,
                                      'name': f'Machine_{machine_id:02d}',
                                      'oee': 1,
                                      'setup_time': instance.setup_time.generate_value(),
                                      'execution_time': instance.unit_assembly_time.generate_value()
                                      })

            s0 = Node(parent=initial_nodes[selected_node_index],
                      name=f's_{operationid}',
                      operationid=operationid,
                      productid=operationid,
                      quantity=Quantity.get_quantity(instance.quantity.min, 1, instance.quantity.max),
                      code=f"code_{operationid}",
                      pname=f"prod_{operationid}",
                      parentid=initial_nodes[selected_node_index].operationid,
                      machines=machines_list)

    def __remove_nodes(self, nodes_no: int, op_net: Node):
        """
        From the set of leaf nodes removes nodes_no operations from operation graph
        :param nodes_no: the number of nodes to be removed
        :param op_net: root node of the operations network
        """
        leaf_nodes = [node for node in PreOrderIter(op_net) if len(node.children) == 0]
        random.shuffle(leaf_nodes)

        for it in range(nodes_no):
            node_to_remove = random.choice(leaf_nodes)
            op_net.metainfo['operations_list'].remove(node_to_remove.operationid)
            leaf_nodes.remove(node_to_remove)

            parent = node_to_remove.parent
            children = list(parent.children)
            children.remove(node_to_remove)
            parent.children = children

    def perturb(self, instance: Instance, new_op_net: Node) -> Node:
        if self.perturb_operations_graph.type == OperationGraphPerturbationParam.OPERATION_GRAPH_PERTUBATION.ADD_LEAF_OPERATION:
            new_nodes_no = None
            if self.perturb_operations_graph.value_type == VALUE_TYPE.ABSOLUTE:
                new_nodes_no = int(self.perturb_operations_graph.value)
            elif self.perturb_operations_graph.value_type == VALUE_TYPE.PERCENTAGE:
                new_nodes_no = int(instance.nodes_number*self.perturb_operations_graph.value / 100)
            else:
                raise Exception(f"Unknown value_type: {self.perturb_operations_graph.value_type} available options: {str(VALUE_TYPE.ABSOLUTE)}, {str(VALUE_TYPE.PERCENTAGE)}")
            print(f"{str(OperationGraphPerturbationParam.OPERATION_GRAPH_PERTUBATION.ADD_LEAF_OPERATION)}: {new_nodes_no} node(s) are added to the operations graph")

            self.__add_nodes(new_nodes_no, instance, new_op_net)

        elif self.perturb_operations_graph.type == OperationGraphPerturbationParam.OPERATION_GRAPH_PERTUBATION.REMOVE_LEAF_OPERATION:
            leaf_nodes = [node for node in PreOrderIter(new_op_net) if len(node.children) == 0]
            if self.perturb_operations_graph.value_type == VALUE_TYPE.ABSOLUTE:
                remove_nodes_no = int(self.perturb_operations_graph.value)
            elif self.perturb_operations_graph.value_type == VALUE_TYPE.PERCENTAGE:
                remove_nodes_no = int(len(leaf_nodes) * self.perturb_operations_graph.value / 100)
            else:
                raise Exception(
                    f"Unknown value_type: {self.perturb_operations_graph.value_type} available options: {str(VALUE_TYPE.ABSOLUTE)}, {str(VALUE_TYPE.PERCENTAGE)}")

            self.__remove_nodes(remove_nodes_no, new_op_net)
        else:
            raise Exception(f"Unknown graph structure modification: {self.type} available options: {str(self.GRAPH_PERTUBATION.ADD_LEAF_OPERATION)}, {str(self.GRAPH_PERTUBATION.REMOVE_LEAF_OPERATION)}")
        return new_op_net

class PerturbationMachines(PerturbationVariant):
    """
        The perturbation is done on operation graph structure.
    """

    def __init__(self, initial_instance_path: str,
                 seed: int,
                 generated_instances_number: int,
                 generated_instances_path: str,
                 generated_instances_name: str,
                 machine_assignment_perturbation: MachinesAssignmentPerturbationsParams
                 ):
        super().__init__(initial_instance_path,
                         seed,
                         generated_instances_number,
                         generated_instances_path,
                         generated_instances_name,
                         )
        self.machine_assignment_perturbation: MachinesAssignmentPerturbationsParams = machine_assignment_perturbation
        random.seed(self.seed)


    def __reassign(self, instance: Instance, op_net: Node):
        """
        Changes the operation eligible machines
        - keeps a percentage of operations with same alternative machine variants
        - modifies operation alternative machine by adding or removing machines in the range [min_alternative, max_alternatives]
        :param instance: the perturbation variant properties
        :param op_net: the operation graph
        :return:
        """
        initial_nodes = [node for node in PreOrderIter(op_net)]
        random.shuffle(initial_nodes)

        min_machines_alternatives = self.machine_assignment_perturbation.min_alternatives \
            if self.machine_assignment_perturbation.min_alternatives is not None else 1
        max_machines_alternatives = self.machine_assignment_perturbation.max_alternatives \
            if self.machine_assignment_perturbation.max_alternatives is not None else instance.machines_alternatives

        for operation in initial_nodes:
            if random.random() < self.machine_assignment_perturbation.modified_operations_percentage: continue #leave operations machine number as it is

            current_op_no = len(operation.machines)
            if random.random() < self.machine_assignment_perturbation.favor_machine_alternatives_increase_percentage:
                #remove machines if the number of machines > min_alternatives
                if current_op_no > min_machines_alternatives:
                    no_machines_to_remove = random.randint(0, current_op_no - min_machines_alternatives)
                    random.shuffle(operation.machines)
                    operation.machines = operation.machines[no_machines_to_remove:]

            else:
                #add machines if the number of alternatives is less than the max_alternative number
                if current_op_no < instance.machines_alternatives:
                    no_machines_to_add = random.randint(0, max_machines_alternatives - current_op_no)
                    machines_list = operation.machines
                    used_machines = [machine['id'] for machine in machines_list]
                    available_machines = [id for id in range(min(instance.machine_id_list), max(instance.machine_id_list) + 1) if id not in used_machines]
                    for it in range(no_machines_to_add):
                        machine_id = random.choice(available_machines)
                        available_machines.remove(machine_id)
                        machines_list.append({'id': machine_id,
                                              'name': f'Machine_{machine_id:02d}',
                                              'oee': 1,
                                              'setup_time': instance.setup_time.generate_value(),
                                              'execution_time': instance.unit_assembly_time.generate_value()
                                              })

    def __modify_machine_number(self, instance: Instance, op_net: Node):
        """
        Increase or decrease the number of machines used by the current instance. Maps the number of alternatives for
        each operation in the range [min_alternative, max_alternatives]
        :param instance: the perturbation variant properties
        :param op_net: the operation graph
        :return:
        """
        operation_list = [node for node in PreOrderIter(op_net)]

        current_machines = instance.machine_id_list.copy()
        removed_machines = []
        if len(instance.machine_id_list) > self.machine_assignment_perturbation.machine_no:
            #remove machines from current list
            no_of_machines_to_be_removed = len(instance.machine_id_list) - self.machine_assignment_perturbation.machine_no
            random.shuffle(current_machines)
            removed_machines = current_machines[:no_of_machines_to_be_removed]
            current_machines = current_machines[no_of_machines_to_be_removed:]
            current_machines.sort()
            op_net.metainfo['maintenances'] = [maintenance for maintenance in instance.maintenances_list if maintenance["machineid"] in current_machines]
        else:
            #add machines in current list
            max_machine_id = max(current_machines) + 1
            current_machines.extend([max_machine_id + i for i in range(0, self.machine_assignment_perturbation.machine_no - len(current_machines))])

        for operation in operation_list:
            operation.machines = [machine for machine in operation.machines if machine['id'] not in removed_machines]
            alternatives_no = random.randint(self.machine_assignment_perturbation.min_alternatives, self.machine_assignment_perturbation.max_alternatives)
            if len(operation.machines) > alternatives_no:
                random.shuffle(operation.machines)
                operation.machines = operation.machines[len(operation.machines) - alternatives_no :]
            else:
                used_machines = [machine['id'] for machine in operation.machines]
                available_machines = list(set(current_machines) - set(used_machines))
                for it in range(alternatives_no - len(operation.machines)):
                    machine_id = random.choice(available_machines)
                    available_machines.remove(machine_id)
                    operation.machines.append({'id': machine_id,
                                          'name': f'Machine_{machine_id:02d}',
                                          'oee': 1,
                                          'setup_time': instance.setup_time.generate_value(),
                                          'execution_time': instance.unit_assembly_time.generate_value()
                                          })
        op_net.metainfo['machines_list'] = current_machines

    def perturb(self, instance: Instance, new_op_net: Node) -> Node:
        """
        Select perturbation variant strategy
        :param instance: the perturbation variant properties
        :param new_op_net: the operation graph
        :return: the new generated variant
        """

        if self.machine_assignment_perturbation.type == MachinesAssignmentPerturbationsParams.MACHINE_ASSIGNMENT_PERTUBATION.REASSIGN:
           self.__reassign(instance, new_op_net)

        elif self.machine_assignment_perturbation.type == MachinesAssignmentPerturbationsParams.MACHINE_ASSIGNMENT_PERTUBATION.NEW_MACHINE_CONFIGURATION:
            self.__modify_machine_number(instance, new_op_net)
        else:
            raise Exception(f"Unknown machine perturbation type: {self.type} available options: {str(self.MACHINE_ASSIGMENT_PERTUBATION.REASSIGN)}, {str(self.MACHINE_ASSIGMENT_PERTUBATION.NEW_MACHINE_CONFIGURATION)}")
        return new_op_net

class PerturbationVariants(object):
    """
    Singleton that holds all perturbations variants
    """
    instance = None
    perturbation_variants = []

    def __new__(cls, *args, **kwargs) -> object:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    @classmethod
    def get_variant(cls, name: str) -> PerturbationVariant:
        for v in cls.perturbation_variants:
            if name == v.name:
                return v

    @classmethod
    def add_variant(cls, variant: PerturbationVariant) -> None:
        cls.perturbation_variants.append(variant)

    @classmethod
    def remove_variant(cls, variant: PerturbationVariant) -> None:
        if variant in cls.perturbation_variants:
            cls.perturbation_variants.remove(variant)

    @classmethod
    def get_all(cls):
        return cls.perturbation_variants

class PerturbationsTypes(StrEnum):
    OPERATIONS_GRAPH_PERTURBATION = auto()
    MACHINE_ASSIGNMENT_PERTURBATION = auto()

class PerturbationVariantDecoder(JSONDecoder):

    @classmethod
    def decode(cls, todecode) -> list:
        """
        Maps the configuration file to the parse structure
        :param todecode: configuration file
        :return: list with the configurations
        """

        variants = todecode.get("instance_variants")
        is_operation_graph_variance = True

        for v in variants:
            vals = []
            for key in v.keys():
                if key == PerturbationsTypes.OPERATIONS_GRAPH_PERTURBATION:
                    vals.append(OperationGraphPerturbationParam(v[key]))
                    is_operation_graph_variance = True
                elif key == PerturbationsTypes.MACHINE_ASSIGNMENT_PERTURBATION:
                    vals.append(MachinesAssignmentPerturbationsParams(v[key]))
                    is_operation_graph_variance = False
                else:
                    vals.append(v[key])

            if is_operation_graph_variance:
                PerturbationVariants.add_variant(PertubationOperationGraph(*vals))
            else:
                PerturbationVariants.add_variant(PerturbationMachines(*vals))

        return PerturbationVariants.get_all()

    @staticmethod
    def handle_error(key) -> Exception:
        log.error(f"No such a key {key} in dictionary")
        return KeyError(f"No such a key {key} in dictionary")

    @classmethod
    def build(cls, configuration_file_path: str):
        try:
            log.info("Importing the variants config file...")
            #with open(get_abs_file_path("config/variants-config.json")) as f:
            with open(get_abs_file_path(configuration_file_path)) as f:
                encoded_variants = json.load(f)
                cls.variants = cls.decode(encoded_variants)
            return cls.variants
        except FileNotFoundError as e:
            log.error("The variants configuration file is missing...")

if __name__ == "__main__":
    PerturbationVariantDecoder.build()

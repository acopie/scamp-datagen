import random
import json
import random

from anytree import Node, Resolver

from boms_processing import BomDecoder
from gentree import create_children, export_tree
from datagen.common.importer import SProductDecoder
from metainfo import MetaInfo
from productgenerator import generate
from ..common.sequencer import Sequencer


def generate_dataset_config():
    datagen = {"boms": []}
    bom_config = {
        "name": "",
        "max_depth": 0,
        "max_children": 0,
        "randomize_children": False,
        "seed": 0,
        "prod_number": 200,
        "machines_number": 0,
        "max_alternatives_machines_number": 0,
        "randomize_alternative_machines": True,
        "output_file": "",
        "start_date": "2023-01-01 00:00:00.000000",
        "delivery_date": "2023-03-01 00:00:00.000000",
        "quantity": {
            "min": 1,
            "step": 1,
            "max": 10
        },
        "allow_identical_machines": False,
        "percent_of_identical_machines": 0,
        "maintenance_duration": {
            "min_duration": 180,
            "max_duration": 360,
            "step": 60,
            "time_units": "minutes"
        },
        "maintenance_interval": {
            "duration": 168,
            "time_units": "hours"
        },
        "maintenance_probability": 0.25,
        "unit_assembly_time": {
            "min": 60,
            "step": 60,
            "max": 600,
            "time_units": "seconds"
        },
        "oee": {
            "min": 0.75,
            "max": 1,
            "distribution": "normal"
        },
        "setup_time": {
            "min": 60,
            "step": 30,
            "max": 120,
            "time_units": "minutes"
        }
    }
    for depth in [2, 3, 4]:
        for children in [2, 3, 4, 5]:
            for machines in [5, 10, 20]:
                for alternates in [2, 3, 5]:
                    bom = bom_config.copy()
                    bom["max_depth"] = depth
                    bom["max_children"] = children
                    bom["machines_number"] = machines
                    bom["max_alternatives_machines_number"] = alternates
                    bom["name"] = f"Bom_{depth}_{children}_{machines}_{alternates}"
                    bom["output_file"] = f"bom_{depth}_{children}_{machines}_{alternates}.json"
                    datagen["boms"].append(bom)
    with open('./config/datagen.json', 'w', encoding="utf8") as json_file:
        json.dump(datagen, json_file, indent=2, default=str)

'''
def generate_problem_encoding(file, filename):
    root = import_tree(file)

    print(root.machines_list)
    print(root.operations_list)
    for i, node in enumerate(PreOrderIter(root)):
        if node.name == "root":
            node.quantity = 1
        #print(i,node.id, node.pname)
        
        # node.operationid = i
        # for child in node.children:
        #     child.parentid = i
        

    planification_problem = {}
    n = len(root.operations_list)
    planification_problem['n'] = n
    m = len(root.machines_list)
    planification_problem['m'] = m

    planification_problem['operationIDs'] = sorted(root.operations_list)
    planification_problem['operationProductCode'] = [""]*n
    planification_problem['operationProductQuantity'] = [0]*n
    planification_problem['operationSuccessor'] = [0]*n

    planification_problem['workstationIDs'] = sorted(root.machines_list)
    planification_problem['workstationNames'] = [f"WS_{id}" for id in root.machines_list]
    planification_problem['workstationAssignment'] = np.zeros((n, m), dtype=np.int8).tolist()
    planification_problem['assemblyTime'] = np.zeros((n, m)).tolist()
    planification_problem['unitAssemblyTime'] = np.zeros((n, m)).tolist()
    planification_problem['setupTime'] = np.zeros((n, m)).tolist()

    planification_problem['finalOperationIDs'] = []
    planification_problem['finalOperationPosition'] = []
    planification_problem['finalDeadline'] = []

    #current_time = datetime.datetime.now()
    current_time = datetime.datetime(2022, 6, 1)
    planification_problem['planificationStartTime'] = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    for operation in PreOrderIter(root):
        planification_problem['operationProductCode'][planification_problem['operationIDs'].index(operation.operationid)] = operation.code  # operation.pname
        planification_problem['operationProductQuantity'][planification_problem['operationIDs'].index(operation.operationid)] = operation.quantity
        planification_problem['operationSuccessor'][planification_problem['operationIDs'].index(
            operation.operationid)] = -1 if operation.parentid == None else planification_problem['operationIDs'].index(operation.parentid)+1

        if operation.parentid == None:
            planification_problem['finalOperationIDs'].append(operation.operationid)
            planification_problem['finalOperationPosition'].append(planification_problem['operationIDs'].index(operation.operationid)+1)
            planification_problem['finalDeadline'].append((datetime.datetime.strptime(operation.delivery_date, '%Y-%m-%d %H:%M:%S.%f') -
                                                          datetime.datetime.strptime(planification_problem['planificationStartTime'], '%Y-%m-%d %H:%M:%S.%f')).total_seconds())

        for machine in operation.machines:
            planification_problem['workstationAssignment'][planification_problem['operationIDs'].index(operation.operationid)][planification_problem['workstationIDs'].index(machine['id'])] = 1
            planification_problem['assemblyTime'][planification_problem['operationIDs'].index(operation.operationid)][planification_problem['workstationIDs'].index(
                machine['id'])] = float(operation.quantity*machine["execution_time"]+machine["setup_time"])
            planification_problem['unitAssemblyTime'][planification_problem['operationIDs'].index(
                operation.operationid)][planification_problem['workstationIDs'].index(machine['id'])] = float(machine["execution_time"])
            planification_problem['setupTime'][planification_problem['operationIDs'].index(
                operation.operationid)][planification_problem['workstationIDs'].index(machine['id'])] = float(machine["setup_time"])

    planification_problem['finalOperations'] = len(planification_problem['finalOperationIDs'])
    planification_problem['M'] = int(max(planification_problem['finalDeadline'])*2)

    with open(f'../solvers/benchmark_dataset/{filename}.json', 'w', encoding="utf8") as json_file:
        json.dump(planification_problem, json_file, indent=4, default=str)
'''

if __name__ == '__main__':
    generate_dataset_config()
    # generate_boms()

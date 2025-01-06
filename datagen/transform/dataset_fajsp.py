import os
from pathlib import Path
import json
from datetime import datetime, timedelta


def build_node(operationid, product, parentid):
    node = {"operationid": operationid, "productid": operationid,
            "code": product, "pname": product, 'name': product,
            "quantity": 1, "parentid":  parentid}
    node["machines"] = []
    node["children"] = []
    return node


def generate_datasets(data_dir, output_dir):

    for file_name in os.listdir(data_dir):
        print(file_name)
        with open(Path(data_dir)/file_name, 'r') as file:
            lines = file.readlines()
            fistLine = 0
            for line in lines:
                if line.strip().startswith("#"):
                    fistLine += 1
                else:
                    break

            operations_no,relations_no,machine_no = [int(x) for x in lines[fistLine].strip().split(" ")]
            operations_relations = lines[fistLine+1:fistLine+1+relations_no]
            operations_machines = lines[fistLine+1+relations_no:]
            # print(operations_relations)
            # print(operations_machines)

        metainfo_machine = list(range(machine_no+1))
        metainfo_operations = list(range(operations_no+1))
        root_operation_id = operations_no
        output_data = build_node(root_operation_id, "root", None)
        output_data["machines"] = [{"id": machine_no,"name": f"Machine_{machine_no}", "oee": 1, "execution_time": 0,"setup_time": 0}]
        max_time = 0

        #machines for operations
        operations_machines_parsed={}
        index = 0
        for line in operations_machines:
            items = [int(x) for x in line.strip().split(" ")]
            op_machines = []
            _op_max_time = -1
            for i in range(1, 2*items[0], 2):
                op_machines.append({"id": items[i], "name": f"Machine_0{items[i]}", "oee": 1, "execution_time": items[i+1], "setup_time": 0})
                if _op_max_time < items[i+1]:
                    _op_max_time =  items[i+1]
            max_time += _op_max_time
            operations_machines_parsed[index] = op_machines
            index += 1
        #print(operations_machines_parsed)
        operations = {}
        jobs_first_operation = set()
        jobs_following_operations = set()
        index_job = 1
        node_parents = {}
        for relation in operations_relations:
            parent, child = [int(x) for x in relation.strip().split(" ")]
            if child not in node_parents:
                node_parents[child] = []
            node_parents[child].append(parent)
            if parent not in jobs_following_operations:
                jobs_first_operation.add(parent)
                # if child not in jobs_following_operations:
                #     index_job += 1
            jobs_following_operations.add(child)

            if parent not in operations:
                parent_node = build_node(parent, f'Job_{index_job}_op_{parent}', root_operation_id)
                parent_node["machines"] = operations_machines_parsed[parent]
                operations[parent] = parent_node
                output_data["children"].append(parent_node)
            else: 
                parent_node = operations[parent]
            
            if child not in operations:
                child_node = build_node(child, f'Job_{index_job}_op_{child}', parent)
                child_node["machines"] = operations_machines_parsed[child]
                operations[child] = child_node
            else:
                child_node = {"operationid": child, "quantity": 1, "parentid":  parent, "productid": child}

            parent_node["children"].append(child_node)

        # for node, parents_list in node_parents.items():
        #     if len(parents_list) > 1:
        #         for machine in operations_machines_parsed[node]:
        #             machine['execution_time'] /= len(parents_list)

        dt = datetime(2023, 2, 1, 0, 0, 0)
        result = dt + timedelta(seconds=max_time)
        output_data["start_date"] = "2023-01-01 00:00:00.000000"
        output_data["delivery_date"] = result.strftime("%Y-%m-%d %H:%M:%S.%f")
        output_data["metainfo"] = {"operations_list": list(metainfo_operations), "machines_list": list(metainfo_machine),
                                   "maintenances": []}

        # Convert and write JSON object to file
        with open(output_dir +"/" + file_name + ".json", "w") as outfile:
             json.dump(output_data, outfile, indent=2)

if __name__=='__main__':
    data_dir   = '../../initial-transform-datasets/dafjs/'
    output_dir = '../../datasets/dafjs/'
    generate_datasets(data_dir, output_dir)
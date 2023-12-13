import os
from pathlib import Path
import random
import string
import json
from datetime import datetime, timedelta

def random_string():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(4))

def unique_random_strings(n):
    unique_strings = set()

    while len(unique_strings) < n:
        new_string = random_string()
        unique_strings.add(new_string)

    return list(unique_strings)

def generate_datasets(data_dir, output_dir):

    for file_name in os.listdir(data_dir):
        with open(Path(data_dir)/file_name, 'r') as file:
            lines = file.readlines()
            m1,m2 = [int(x) for x in lines[0].strip().split(" ")]
            n = int(lines[1].strip())
            operations = []
            all_operation = []
            for line in lines[2:]:
                line = line.strip()
                operation_line = [int(x) for x in line.split(" ")]
                operations.append(operation_line)
                all_operation.extend(operation_line)
        print("m1=", m1, "m2=", m2)


        metainfo_machine = set()
        metainfo_opperations = set()
        output_data = {}
        output_data["operationid"] = 0
        output_data["productid"] = 0
        output_data["code"] = "root"
        output_data["pname"] = "root"
        output_data["name"] = "root"
        output_data["parentid"] = None


        output_data["quantity"] = 1
        output_data["machines"] = [{"id": 0,"name": "Machine_00", "oee": 1, "execution_time": 0,"setup_time": 0}]

        metainfo_machine.add(0)
        metainfo_opperations.add(0)

        #build machines for 1st stage m1
        machines_m1 = []
        index = 0
        for i in range(m1):
            index += 1
            machines_m1.append({"id": index, "name": f"Machine_0{i+1}", "oee": 1, "execution_time": -1, "setup_time": 0})
            metainfo_machine.add(index)

        #build machines for 2nd stage m2
        machines_m2 = []
        index = m1
        max_time = 0
        for i in range(m2):
            index += 1
            machines_m2.append({"id": index, "name": f"Machine_A0{i+1}", "oee": 1, "execution_time": -1, "setup_time": 0})
            metainfo_machine.add(index)

        #build operations
        children = []
        index_job = 0
        for job in operations:
            index_job += 10
            metainfo_opperations.add(index_job)
            name = f"Job_{index_job}"
            child = {"operationid": index_job, "productid": index_job, "code": name, "pname" : name, 'name' : name, "quantity":1}
            child["parentid"] = 0
            child["machines"] = []
            max_time += job[m1]
            for m in machines_m2:
                temp = m.copy()
                temp["execution_time"] = job[m1]
                child["machines"].append(temp)
            child_children = []
            for i in range(m1-1, -1, -1):
                index_operation = index_job + i + 1
                metainfo_opperations.add(index_operation)
                name = f"Job_{index_job}_o{i+1}"
                c = {"operationid": index_operation, "productid": index_operation, "code": name, "pname": name, 'name': name,
                         "quantity": 1}
                c["parentid"] = index_job
                temp = machines_m1[i].copy()
                temp["execution_time"] = int(job[i])
                c["machines"] = [temp]
                max_time += job[i]
                child_children.append(c)
            child["children"] = child_children
            children.append(child)

        output_data["children"] = children

        dt = datetime(2023, 2, 1, 0, 0, 0)
        result = dt + timedelta(seconds=max_time)
        output_data["start_date"] = "2023-01-01 00:00:00.000000"
        output_data["delivery_date"] = result.strftime("%Y-%m-%d %H:%M:%S.%f")  # calculeaza
        output_data["metainfo"] = {"operations_list": list(metainfo_opperations), "machines_list": list(metainfo_machine),
                                   "maintenances": []}

        # Convert and write JSON object to file
        with open(output_dir +"/" + file_name + ".json", "w") as outfile:
             json.dump(output_data, outfile, indent=2)

if __name__=='__main__':
    data_dir = '../../solutions/TALENS_2021/initial_data/B1'
    output_dir = '../../solutions/TALENS_2021/out/B1'
    generate_datasets(data_dir, output_dir)
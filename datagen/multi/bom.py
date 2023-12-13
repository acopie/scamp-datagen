"""
This module contains the logic for multi-product BOM generation

@author: Adrian
"""

import logging
import os

from json import JSONDecoder, load

from datagen.common.utility import get_abs_file_path

from datagen.multi.machineinfo import MachineInfo, UnitAssemblyTime, SetupTime, MaintenanceDuration, \
    MaintenanceInterval, OEE
from datagen.multi.prodinfo import ProductInfo

log = logging.getLogger("main")

MULTICONFIG_FILE = "config/multi-config.json"


# def get_config_file() -> str:
#     module_dir = os.path.dirname(os.path.abspath(__file__))
#     parent_dir = os.path.abspath(os.path.join(module_dir, os.pardir))
#     # Construiește calea absolută către fișierul config
#     config_path = os.path.abspath(os.path.join(parent_dir, MULTICONFIG_FILE))
#
#     return config_path


class ProductsInfo:
    products_info = []

    @classmethod
    def add_product_info(cls, product_info):
        cls.products_info.append(product_info)

    @classmethod
    def remove_product_info(cls, product_info):
        if product_info in cls.products_info:
            cls.products_info.remove(product_info)

    @classmethod
    def get_product_info(cls, name):
        for p in cls.products_info:
            if name == p.name:
                return p

    @classmethod
    def get_all(cls):
        return cls.products_info


class MultiBom:
    """
    Class that deals with an entry in the multi-config.json file

    @param products_info: a list of products that will be used as entries in the BOM tree
    @machines_info: a list of machines that will be used as entries in the BOM tree
    """

    def __init__(self, products_info, machines_info):
        self.products_info = products_info
        self.machines_info = machines_info


class MultiBoms:
    """
    Singleton that holds all the multi-BOMs defined in our data generator
    """
    instance = None
    multi_boms = []

    def __new__(cls, *args, **kwargs) -> object:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    @classmethod
    def get_multi_bom(cls, name: str) -> MultiBom:
        for b in cls.multi_boms:
            if name == b.name:
                return b

    @classmethod
    def add_multi_bom(cls, multi_bom: MultiBom) -> None:
        cls.multi_boms.append(multi_bom)

    @classmethod
    def remove_multi_bom(cls, multi_bom: MultiBom) -> None:
        if multi_bom in cls.multi_boms:
            cls.multi_boms.remove(multi_bom)

    @classmethod
    def get_all(cls):
        return cls.multi_boms


class MultiBomDecoder(JSONDecoder):

    @classmethod
    def decode(cls, todecode) -> list:

        list_of_boms = todecode.get("boms")
        is_standard_bom = True

        for b in list_of_boms:

            products_info = []
            machines_info = None

            for key in b.keys():

                if key == "outputs":
                    for i in range(len(b[key])):
                        products_info.append(ProductInfo(**(b[key][i])))
                elif key == "start_date":
                    start_date = b[key]
                elif key == "prod_number":
                    prod_number = b[key]
                elif key == "root_directory":
                    root_directory = b[key]
                elif key == "machines_number":
                    machines_number = b[key]
                elif key == "max_alternatives_machines_number":
                    max_alternatives_machines_number = b[key]
                elif key == "randomize_alternative_machines":
                    randomize_alternative_machines = b[key]
                elif key == "allow_identical_machines":
                    allow_identical_machines = b[key]
                elif key == "percent_of_identical_machines":
                    percent_of_identical_machines = b[key]
                elif key == "unit_assembly_time":
                    unit_assembly_time = UnitAssemblyTime(**b[key])
                elif key == "maintenance_duration":
                    maintenance_duration = MaintenanceDuration(**b[key])
                elif key == "maintenance_interval":
                    maintenance_interval = MaintenanceInterval(**b[key])
                elif key == "maintenance_probability":
                    maintenance_probability = b[key]
                elif key == "oee":
                    oee = OEE(**b[key])
                elif key == "setup_time":
                    setup_time = SetupTime(**b[key])

            machine_info = MachineInfo(start_date,
                                       prod_number,
                                       root_directory,
                                       machines_number,
                                       max_alternatives_machines_number,
                                       randomize_alternative_machines,
                                       allow_identical_machines,
                                       percent_of_identical_machines,
                                       unit_assembly_time,
                                       maintenance_duration,
                                       maintenance_interval,
                                       maintenance_probability,
                                       oee,
                                       setup_time)

            MultiBoms.add_multi_bom(MultiBom(products_info, machine_info))

            # TODO: check if really needed
            return MultiBoms.get_all()

    @classmethod
    def build(cls):
        """
        Reads the multi-config.json file and builds the multi-BOMs
        """

        log.info("Importing multi-product BOMs config file...")
        try:
            import os
            crt_dir = os.getcwd()
            with open(get_abs_file_path(MULTICONFIG_FILE), "r") as f:
                data = load(f)
                cls.decode(data)
        except FileNotFoundError:
            log.error(
                "Multi-product BOMs config file not found. Please make sure that the file exists and is in the correct location.")

            # leave the program since one cannot go further without the config file
            exit(1)

"""

This class deals with the configuration file used to generate the BOMs in the system.

Basically it deserializes the datagen.json file and make all the params available for the
data generator

@author Adrian

"""

import json
import logging

from json import JSONDecoder

from datagen.common.assembly import UnitAssemblyTime, Oee
from datagen.common.utility import get_abs_file_path

from datagen.mono.maintenance import MaintenanceDuration, MaintenanceInterval
from datagen.mono.setup import SetupTime
from datagen.mono.quantity import Quantity
from datagen.mono.vtdepth import VerticalTreeDepth

log = logging.getLogger("main")

class MachinesSetup(object):
    """
    Represents the general parameters for the machines used to process a specific product

    """

    def __init__(self, time_units="seconds"):
        self.time_units = time_units


class Bom(object):
    """
    Models the parameters needed for a single BOM.
    NOTE: In this version is important to keep the order of the parameters defined in datagen.json with the
            list of parameters in the Bom constructor
    """

    def __init__(self,
                 name: str,
                 max_depth: int,
                 max_children: int,
                 randomize_children: bool,
                 seed: int,
                 prod_number: int,
                 machines_number: int,
                 max_alternatives_machines_number: int,
                 randomize_alternative_machines: bool,
                 output_file: str,
                 start_date: str,
                 delivery_date: str,
                 quantity: Quantity,
                 allow_identical_machines,
                 percent_of_identical_machines: float,
                 maintenance_duration: MaintenanceDuration,
                 maintenance_interval: MaintenanceInterval,
                 maintenance_probability: float,
                 unit_assembly_time: UnitAssemblyTime,
                 oee: Oee,
                 setup_time: SetupTime):
        # the name of the BOM. Must be unique across our system
        self.name: str = name

        # the maximum depth of the BOM as a tree representation
        self.max_depth: int = max_depth

        # the maximum number of children on a level
        self.max_children: int = max_children

        # if the number of children is computed as a random number between 1 and max_children
        self.randomize_children: bool = randomize_children

        # seed used to initialize the random generator
        self.seed: int = seed

        # the number of possible products that will be in the final BOM
        self.prod_number = prod_number

        # the number of machines used for the product
        self.machines_number: int = machines_number

        # the maximum number of alternative machines where a product can be processed
        self.max_alternatives_machines_number: int = max_alternatives_machines_number

        # if the max_alternatives_machines_number will be randomly chosen
        self.randomize_alternative_machines: bool = randomize_alternative_machines

        # the name of the output file representing the BOM
        self.output_file: str = output_file

        # the starting date of the product
        self.start_date = start_date

        # the delivery date for the product
        self.delivery_date: str = delivery_date

        # the duration of the maintenance operation for machines
        self.maintenance_duration: MaintenanceDuration = maintenance_duration

        # the interval on which the maintenance repeats
        self.maintenance_interval = maintenance_interval

        # the probability to generate a maintenance for a machine
        self.maintenance_probability = maintenance_probability

        # the time necessary to assembly one unit of product
        self.unit_assembly_time = unit_assembly_time

        # overall equipment effectiveness for an operation/product
        self.oee = oee

        # the time necessary to setup a machine
        self.setup_time: SetupTime = setup_time

        # the maximum products per BOM
        self.quantity: Quantity = quantity

        # if the BOM supports identical machines
        self.allow_identical_machines: bool = allow_identical_machines

        # the percent of identical machines from the total number of machines
        self.percent_of_identical_machines = percent_of_identical_machines

        # the possible maintenance intervals for this BOM
        self.possible_maintenance_intervals = None


class VerticalTreeBom(Bom):
    """
    Models a vertical tree BOM. This particular BOM differs form the standard BOM in the way that it has one or more
    vertical branches attached on the children from the last level of the n-ary tree, which represents the standard BOM.
    """

    def __init__(self, name, max_depth, max_children, randomize_children, seed, prod_number, machines_number,
                 max_alternatives_machines_number, randomize_alternative_machines, output_file, start_date,
                 delivery_date, quantity, allow_identical_machines, percent_of_identical_machines,
                 maintenance_duration, maintenance_interval, maintenance_probability, unit_assembly_time, oee,
                 setup_time, vertical_tree_depth):
        super().__init__(name,
                         max_depth,
                         max_children,
                         randomize_children,
                         seed,
                         prod_number,
                         machines_number,
                         max_alternatives_machines_number,
                         randomize_alternative_machines,
                         output_file,
                         start_date,
                         delivery_date,
                         quantity,
                         allow_identical_machines,
                         percent_of_identical_machines,
                         maintenance_duration,
                         maintenance_interval,
                         maintenance_probability,
                         unit_assembly_time,
                         oee,
                         setup_time)
        self.vertical_tree_depth = vertical_tree_depth


class Boms(object):
    """
    Singleton that holds all the BOMs defined in our data generator
    """
    instance = None
    boms = []

    def __new__(cls, *args, **kwargs) -> object:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    @classmethod
    def get_bom(cls, name: str) -> Bom:
        for b in cls.boms:
            if name == b.name:
                return b

    @classmethod
    def add_bom(cls, bom: Bom) -> None:
        cls.boms.append(bom)

    @classmethod
    def remove_bom(cls, bom: Bom) -> None:
        if bom in cls.boms:
            cls.boms.remove(bom)

    @classmethod
    def get_all(cls):
        return cls.boms


class BomDecoder(JSONDecoder):

    @classmethod
    def decode(cls, todecode) -> list:

        list_of_boms = todecode.get("boms")
        is_standard_bom = True

        for b in list_of_boms:
            vals = []
            for key in b.keys():
                if key == "machines_setup":
                    vals.append(MachinesSetup(b[key]))
                elif key == "maintenance_duration":
                    vals.append(MaintenanceDuration(b[key]))
                elif key == "maintenance_interval":
                    vals.append(MaintenanceInterval(b[key]))
                elif key == "unit_assembly_time":
                    vals.append(UnitAssemblyTime(b[key]))
                elif key == "setup_time":
                    vals.append(SetupTime(b[key]))
                elif key == "oee":
                    vals.append(Oee(b[key]))
                elif key == "quantity":
                    vals.append(Quantity(b[key]))
                elif key == "vertical_tree_depth":
                    vals.append(VerticalTreeDepth(b[key]))
                    is_standard_bom = False
                else:
                    vals.append(b[key])

            # if we don't have a standard BOM (which means that we have a combination of n-ary tree and vertical trees)
            # we have to deal with distinct BOM types
            if is_standard_bom:
                Boms.add_bom(Bom(*vals))
            else:
                Boms.add_bom(VerticalTreeBom(*vals))

        return Boms.get_all()

    @staticmethod
    def handle_error(key) -> Exception:
        log.error(f"No such a key {key} in dictionary kkk")
        return KeyError(f"No such a key {key} in dictionary")

    @classmethod
    def build(cls, configuration_file_path):
        try:
            log.info("Importing the BOMs config file...")
            #with open(get_abs_file_path("config/datagen.json")) as f:
            with open(get_abs_file_path(configuration_file_path)) as f:
                encoded_boms = json.load(f)
                cls.boms = cls.decode(encoded_boms)
            return cls.boms
        except FileNotFoundError as e:
            log.error("The BOMs configuration file is missing...")

    @classmethod
    def build_ex(cls):
        try:
            log.info("Importing the BOMs config file...")
            with open("config/mixed-config.json") as f:
                encoded_boms = json.load(f)
                cls.boms = cls.decode(encoded_boms)
            return cls.boms
        except FileNotFoundError as e:
            log.error("The BOMs configuration file is missing...")


if __name__ == "__main__":
    BomDecoder.build()

import json
import logging
import string

import datagen.common.assembly
import datagen.mono.setup as setup

from typing import Any, List, Dict, Type
from json import JSONEncoder
from scipy.stats import norm, truncnorm

from datagen.common.sequencer import Sequencer
from datagen.common.utility import get_abs_file_path

from datagen.mono.msequencer import MachineSequencer
from datagen.mono.setup import *
from datagen.mono.distribution import distribution_params


"""
This file contains the product random generator, which will populate the tree simulating the BOM

@author Adrian
"""


def has_duplicates(self: List[Any]) -> bool:
    """
    Small function to check if a list has duplicates
    """
    return len(set(self)) != len(self)


log = logging.getLogger("main")

# the maximum number of machines on which a part is processed
MAX_ALTERNATIVES_MACHINES: int = 3

# the file where machines are written, in order to build the Machine objects
MACHINES_FILE = "boms/machines.json"

# a list with 200 distinct products, used in our data generator
products_200 = ["AC compressor", "AC drain hose", "A-pillar", "ABS", "ACE filter",
                "Adaptive cruise control", "Adaptive headlights", "Adjustable pedals", "Adjustable suspension",
                "Air conditioning filter",
                "Air filter", "Air pump filter", "Airbag", "Antenna", "Antilock brake system",
                "Anti-theft", "Antifreeze", "Auto-delay headlights", "Auto-leveling suspension",
                "Automatic door unlock",
                "Automatic transaxle", "Automatic transmission", "Automatic transmission cooler hoses",
                "Automatic transmission filter", "Automatic transmission fluid",
                "Auxiliary input (Audio)", "Auxiliary lighting", "AWD", "Axle drive fluid", "B-pillar",
                "Backup assistance", "Balance shaft belt", "Ball joints", "Bed extender", "Bed liner",
                "Beverage cooler", "Bi-level purge valve", "Block heater", "Body water drains", "Bolstering",
                "Brake booster", "Brake fluid", "Brake lines, hoses and connections", "Brake linings",
                "Brake master cylinder",
                "Brake pads", "Brake pedal", "Brake pedal spring", "Brush guard", "Bumpers",
                "C-pillar", "Cabin lighting", "Carburetor", "Catalytic converter", "Catalytic converter heat shield",
                "Charcoal canister", "Child seat", "Child seat anchors", "Choke linkage", "Climate control",
                "Climate-controlled seat filter", "Climate-controlled seats", "Clutch fluid", "Clutch lines & hoses",
                "Clutch master cylinder",
                "Clutch pedal", "Collapsible steering column", "Compass", "Console", "Convertible wind blocker",
                "Coolant", "Cooling fan and shroud", "Cornering brake control", "Cornering lights",
                "Crankcase breather",
                "Crankcase ventilation filter", "Cruise control", "Curtain airbags", "D-Pillar", "Death brake",
                "Descent control", "Diesel engine", "Differential fluid", "Direct injection system",
                "Direct shift gearbox",
                "Disc changer", "Distributor cap", "Distributor rotor", "Diverter valve", "Downshift cable",
                "Drive axle boots", "Drive belt tensioner", "Drive belt", "Drive shaft", "Drive system",
                "Drive train mounts", "Driver state sensor", "Drivetrain", "Driving lights", "DSG",
                "Dusk-sensing headlights", "Dynamic brake control", "EGR system", "Electrochromatic rearview mirror",
                "Electronic stability control",
                "Emergency brake assist", "Engine Auto Stop-Start", "Entry lighting", "Evaporative control canister",
                "Evaporative control canister filter",
                "Evaporative control system", "Exterior camera", "External temperature display", "Fan hub",
                "Fog lights",
                "Four-wheel steering", "Fuel filler cap", "Fuel filter", "Fuel injection system",
                "Fuel lines and connections",
                "Fuel pre-filter", "Fuel pump shutoff", "Fuel system", "Gauges", "Gyro sensor",
                "Haldex clutch", "Head airbags", "Head unit", "Headlight washers", "Headlights",
                "Headsets", "Heads-up display", "Heated air temperature sensor", "Heated mirrors", "Heated windshield",
                "Heated windshield wiper rests", "Heater", "Heater hoses", "Hill holder", "Idler pulley",
                "Instrumentation", "Interior lighting", "Knee airbags", "Liftgate window", "Lip spoiler",
                "Manifold heat control valve", "Manual extending mirrors", "Manual transmission",
                "Manual transmission fluid", "Navigation interface",
                "Nightvision", "Oil filter", "On-board diagnosis system", "One-touch windows", "Oxygen sensor",
                "Parking assist", "Parking lights", "Parking senors", "PCV valve", "PCV filter",
                "Pilot bearing", "Plenum chamber water drain valve", "Power extending mirrors", "Power steering",
                "Power steering fluid",
                "Power steering hoses", "Precrash system", "Premium audio", "Privacy glass", "Purge valve",
                "Radiator core & AC condenser", "Radiator hoses", "Radio data system", "Rain-sensing wipers",
                "Rear area cargo cover",
                "Rear defroster", "Rear door", "Rear electric motor", "Rear HVAC", "Rear seat entertainment system",
                "Rear seat", "Rear spoiler", "Rear area cargo cover", "Repair kit", "Retractable mirrors",
                "Reverse tilt mirrors", "Roof rack", "Roof spoiler", "Run flat", "Satellite communication",
                "Satellite radio", "Seat adjustment", "Seat belts", "Seat extension", "Seatback storage",
                "Self-leveling headlights", "Self leveling suspension (SLS) filter", "Separate rear audio",
                "Sequential manual gearbox", "Serpentine belt", "Horn"
                ]

# few values needed to establish a time per unit on a specific machine
times_per_unity = [60 * i for i in range(1, 11)]

# few values needed to establish a setup time per machine
setup_times = [60 * i for i in range(1, 11)]


class Machine:
    """
    class modelling a Machine in the production system.
    Every machine has an id, a name and an Overall Equipment Effectiveness (oee)
    """

    def __init__(self, id: int, name: string = None, oee: float = 1):
        self.id: int = id
        if name is None:
            if id < 10:
                self.name: str = f"Machine_0{id}"
            else:
                self.name: str = f"Machine_{id}"
        else:
            self.name: str = name
        # overall equipment effectiveness
        self.oee = oee

    def __eq__(self, other):
        if isinstance(other, Machine):
            return (self.id == other.id) and (self.name == other.name)
        else:
            return False

    def __hash__(self):
        return hash(self.id) ^ hash(self.name)

    class MachineEncoder(JSONEncoder):
        """
        Helper class needed for Machine class serialization
        """

        def encode(self, obj: Any) -> dict:
            return obj.__dict__


class Machines:
    """
    Class containing all the machines in our system
    """

    # list of Machine instances
    machines: List[Machine] = []

    class MachinesEncoder(JSONEncoder):
        """
        Helper class needed for Machines class serialization
        """

        def encode(self, obj: Any) -> str:
            return obj.__dict__

    def __init__(self, bom):

        # # list of Machine instances
        # self.machines: List[Machine] = []

        # the current BOM for which we build the machine list
        self.bom = bom

    def assign_machines(self):
        """
        Not implemented yet, for now
        """
        raise NotImplementedError

    @classmethod
    def get(cls, id: int) -> Machine:
        """
        Returns a machine given its id
        :param id:
        :return:
        """
        for m in cls.machines:
            if m.id == id:
                return m

    def build(self) -> List[Machine]:
        """
        Builds a list of machines specific to a BOM. For example, the maximum number of alternate
        machines for a specific product is taken from the passed BOM

        :param bom:
        :return:
        """

        # be sure to start with a clear list of machines
        if len(self.machines) > 0:
            self.machines.clear()

        # get the number of machines from the BOM
        machines_number = self.bom.machines_number

        # here we build the machines by passing a unique identifier, a name and a random OEE value
        for _ in range(machines_number):
            if self.bom.oee.distribution == "normal":
                mean, std_dev = distribution_params(self.bom)

                # normal distribution (no truncation)
                # machine_oee = round(norm.rvs(mean, std_dev), 3)

                # use truncated normal distribution
                truncated_norm = truncnorm((self.bom.oee.min - mean)/std_dev,
                                           (self.bom.oee.max - mean) / std_dev,
                                           loc=mean, scale=std_dev)
                machine_oee = round((truncated_norm.rvs(1)[0]), 3)

            elif self.bom.oee.distribution == "uniform":
                machine_oee = round(random.randrange(self.bom.oee.min, self.bom.oee.max), 3)
            else:
                raise ValueError("Not a valid value for the statistical distribution")

            crt_machine = Machine(id=MachineSequencer().id, oee=machine_oee)

            Machines.machines.append(crt_machine)

        if has_duplicates(Machines.machines):
            log.error("Duplicate machine found")

        return Machines.machines

    def export(self) -> None:
        """
        serializes the Machine instances in a JSON file on disk
        :return: None
        """
        encoded_machines = []

        class Encoder(JSONEncoder):
            """
            Helper class for serializing machines
            """

            def encode(self, obj: Any) -> Dict:
                return obj.__dict__

        encoder = Encoder()
        for m in self.machines:
            encoded_machines.append(encoder.encode(m))

        with open(get_abs_file_path(MACHINES_FILE), "w") as f:
            f.write(json.dumps(encoded_machines, indent=4))

    @classmethod
    def import_machines(cls):
        decoded_machines = None
        try:
            with open(get_abs_file_path(MACHINES_FILE)) as f:
                decoded_machines = json.load(f)
        except FileNotFoundError as e:
            log.error("The source file for machines was not found...")

        return decoded_machines


class Product:
    def __init__(self, productid: str, code: str, name: str, machines_list=None):
        self.productid = productid
        self.code = code

        # use pname instead of name because of a conflict with the name attribute on the Node class
        self.pname = name

        if machines_list is None:
            setattr(self, 'machines', [])
        else:
            if not hasattr(self, 'machines'):
                setattr(self, 'machines', [])

            for entry in machines_list:
                self.machines.append(Machine(entry.get("id"), entry.get("name"), entry.get("oee")))
            self.machines.sort(key=lambda M: M.id)

    def __eq__(self, o: Type['Product']) -> bool:
        """
        Overrides the default __eq__ method in order to provide uniqueness in collections
        """
        if isinstance(o, Product):
            return (self.pname == o.pname) and (self.productid == o.productid) and (self.code == o.code)
        else:
            return False

    def __hash__(self):
        """
        Overrides the default __hash__ method of the object class, used to define uniqueness in collections
        """
        return hash(self.productid, self.code)

    def __str__(self):
        return f"id={self.productid}, code={self.code}, name={self.pname}, quantity={self.quantity}"


class ProductEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class ProductGenerator:

    def __init__(self, bom):
        self.bom = bom
        """
        the pool of products from which we extract when we build the BOM. Its size could vary, based on the 
        prod_number parameter in datagen.json config file
        """
        self.products_pool = products_200.copy()[:bom.prod_number]

    @staticmethod
    def generate_maintenance(bom) -> bool:
        """
        decides if the Maintenance object is generated for a machine
        :return:
        """
        if bom.maintenance_probability == 1:
            return True
        elif bom.maintenance_probability == 0:
            return False
        else:
            return random.random() < bom.maintenance_probability

    def build(self) -> Product:
        # prepare the list of existing machines
        # all_machines = Machines().build()
        all_machines = Machines.import_machines()

        if self.bom.randomize_alternative_machines:
            max_alternative_machine_number = random.randint(1, self.bom.max_alternatives_machines_number)
        else:
            max_alternative_machine_number = self.bom.max_alternatives_machines_number

        if max_alternative_machine_number > len(all_machines):
            print(f"WARNING: the number of alternative machines is greater than the number of existing machines. ")
            print(50 * "#")

        machines_per_product = random.sample(all_machines, max_alternative_machine_number)

        # for debugging reasons, build a list of Machine objects
        machines_list = []
        for m in machines_per_product:
            machine = Machine(id=m.get("id"), name=m.get("name"), oee=m.get("oee"))
            machines_list.append(machine)

        if has_duplicates(machines_list):
            log.warning("Duplicate machine found in the list of machines for a product")
            print(f"WARNING: the list of machines for a product contains duplicates. ")

        return Product(self.productid(), self.code(4), self.part(), machines_list=machines_per_product)

    @staticmethod
    def code(length: int) -> str:
        # choose from all lowercase letter
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters.upper()) for i in range(length))

    @staticmethod
    def productid() -> int:
        # use the hex property of UUID object because of JSON serialization issues
        return Sequencer().index

    def part(self) -> str:
        """
        Picks a product name from the list of existing ones (200 for now)
        """
        if len(self.products_pool) == 0:
            self.products_pool = products_200.copy()[:self.bom.prod_number]

        if len(self.products_pool) > 0:
            chosen = random.choice(self.products_pool)
            self.products_pool.remove(chosen)
            return chosen

    @staticmethod
    def quantity() -> int:
        return random.randint(1, 10)


class Products:
    """
    Class dealing with a collection of Product objects. Offers methods for decoration the BOM nodes
    """

    def __init__(self, bom):
        self.all_products = []
        self.bom = bom

    def build(self) -> List[Product]:
        for i in range(200):
            p = ProductGenerator(self.bom).build()
            self.all_products.append(p)

        return self.all_products

    def export(self) -> None:
        """
        Exports all the products in a json file for further usage
        :return: None
        """

        encoded_products = []

        class Encoder(JSONEncoder):
            def encode(self, obj) -> Dict[str, Any]:
                return obj.__dict__

        encoder = Encoder()

        for p in self.all_products:
            encoded_products.append(encoder.encode(p))

        with open(get_abs_file_path("boms/products.json"), "w") as f:
            f.write(json.dumps(encoded_products, default=lambda o: o.__dict__, indent=4))

    def add_setup_time(self) -> None:
        """
        this method will decorate the list of machines with a randomly chosen setup time
        :return:
        """
        time_units_setup = self.bom.setup_time.time_units

        allowed_identical_machines = self.bom.allow_identical_machines

        # the number of identical machines is given by a parameter in datagen.json
        percent_of_identical_machines = self.bom.percent_of_identical_machines

        max_number_of_identical_machines = int(self.bom.machines_number * percent_of_identical_machines)

        # generate a setup time based on some input parameters
        setup_time = SetupTime.get_setup_time(self.bom.setup_time.min,
                                              self.bom.setup_time.step,
                                              self.bom.setup_time.max)

        for p in self.all_products:
            # define a counter to count the machines which were set up
            machines_counter = 0

            for m in p.machines:

                # if identical machines are allowed, retain this value to be reused
                if allowed_identical_machines and machines_counter < max_number_of_identical_machines:
                    m.setup_time = self.to_seconds(time_units_setup, setup_time)
                    machines_counter += 1
                else:
                    m.setup_time = self.to_seconds(time_units_setup,
                                                   setup.SetupTime.get_setup_time(self.bom.setup_time.min,
                                                                                  self.bom.setup_time.step,
                                                                                  self.bom.setup_time.max))

    def add_time_units(self) -> None:
        """
        this method will decorate the machines list with a time specific to create a unit of product
        :return:
        """
        time_units_assembly = self.bom.unit_assembly_time.time_units
        allowed_identical_machines = self.bom.allow_identical_machines
        percent_of_identical_machines = self.bom.percent_of_identical_machines

        # let's say that the number of identical machines could be only percent_of_identical_machines  from the total
        # number of the machines
        max_number_of_identical_machines = int(self.bom.machines_number * percent_of_identical_machines)

        for p in self.all_products:
            # define a counter to count the machines which were set up
            machines_counter = 0

            generic_execution_time = self.to_seconds(time_units_assembly,
                                                     datagen.common.assembly.UnitAssemblyTime.get_unit_assembly_time(
                                                         self.bom.setup_time.min,
                                                         self.bom.setup_time.step,
                                                         self.bom.setup_time.max))

            for m in p.machines:
                # if identical machines are allowed, retain this value to be reused
                if allowed_identical_machines and machines_counter < max_number_of_identical_machines:
                    m.execution_time = self.to_seconds(time_units_assembly, generic_execution_time)
                    machines_counter += 1
                else:
                    m.execution_time = int(generic_execution_time / m.oee)

    def to_seconds(self, time_units, val) -> int:
        """
        Transforms a certain duration in seconds, based on the units in which duration is expressed
        :param time_units:
        :param val:
        :return:
        """

        d = {"seconds": val, "minutes": val * 60, "hours": val * 60 * 60, "days": val * 60 * 60 * 60}
        res = d.get(time_units, "No such time unit.")

        return res

    def generate_products(self):
        self.build()
        self.add_time_units()
        self.add_setup_time()
        self.export()


def generate(bom):
    # for every BOM defined in datagen.json we need to regenerate the machines list, because they can
    # differ in number
    MachineSequencer().reset()
    machines = Machines(bom)
    machines.build()
    machines.export()

    # and the products also, since they can have different number on machines on which they are executed
    products = Products(bom)
    products.generate_products()


if __name__ == "__main__":
    generate()

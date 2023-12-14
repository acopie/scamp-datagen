"""
This module is a random product generator. The product names are chosen randomly from
the words defined in the /usr/share/dict/words file.

@author: Adrian
"""
import logging
import random
import string

from typing import List, Any, Dict
from json import JSONEncoder, JSONDecoder, dumps, load

from datagen.common.assembly import UnitAssemblyTime

from datagen.common.sequencer import Sequencer
from datagen.common.utility import get_abs_file_path, check_and_create_if_not_exists

from datagen.multi.msequencer import MachineSequencer
from datagen.multi.machines import Machine, Machines
from datagen.multi.product import Product
from datagen.multi.setup import SetupTime
from datagen.multi.bom import MultiBom

NUMBER_OF_PRODUCTS = 100

# whether to generate names from a sequence of random characters or from the words file
generated_names_from_words = False

# get the logger for this module
log = logging.getLogger("main")


class RandomProductGenerator:
    """
    Class representing a random product generator
    """

    # class level. holds all the products in the system
    all_products = list()

    def __init__(self, multi_bom):
        """
        Simple constructor. We need the multi_bom object inside our class
        in order to extract necessary information for building the products
        """
        self.multi_bom = multi_bom

    @staticmethod
    def is_maintenance_generated(bom) -> bool:
        """
        decides if the Maintenance object is generated for a machine
        :return:
        """
        if bom.machines_info.maintenance_probability == 1:
            return True
        elif bom.machines_info.maintenance_probability == 0:
            return False
        else:
            return random.random() < bom.machines_info.maintenance_probability

    def code(self, length: int) -> str:
        # choose from all lowercase letter
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters.upper()) for i in range(length))

    def productid(self) -> int:
        # use the hex property of UUID object because of JSON serialization issues
        return Sequencer().index

    def build_product(self) -> Product:
        """
        Builds a single product with a random name
        """
        all_machines = Machines.import_machines()

        if self.multi_bom.machines_info.randomize_alternative_machines:
            max_alternative_machines_number = random.randint(1,
                                                             self.multi_bom.machines_info.max_alternatives_machines_number)
        else:
            max_alternative_machines_number = self.multi_bom.machines_info.max_alternatives_machines_number

        if max_alternative_machines_number > len(all_machines):
            log.warning(f"The number of alternative machines is greater than the number of existing machines. ")

        # a product can be produced on one or more machines
        machines_per_product = random.sample(all_machines, random.randint(1, max_alternative_machines_number))

        machines_list = []
        for m in machines_per_product:
            machine = Machine(id=m.get("id"), name=m.get("name"), oee=m.get("oee"))
            machines_list.append(machine)

        return Product(self.productid(), self.code(4), self.part() if generated_names_from_words else self.code(4),
                       machines_list)

    def generate_products(self) -> List[Product]:
        """
        Generates a random product

        @param multi_bom: the current bill of materials for one or many products
        @return: a list of generated products
        """

        # reset the sequencer and generate the machines
        MachineSequencer().reset()
        machines = Machines(self.multi_bom)
        machines.build()
        machines.export()

        for i in range(self.multi_bom.machines_info.prod_number):
            RandomProductGenerator.all_products.append(self.build_product())

        self.add_setup_time()
        self.add_time_units()
        self.export()

        return RandomProductGenerator.all_products

    def decode(self) -> Product:
        """
        Decodes a json object into a Product object

        :return: the decoded Product object
        """

        products = list()

        with open(get_abs_file_path(f"multiboms/{self.multi_bom.machines_info.root_directory}/rand_products.json"),
                  "r") as fp:
            decoded = load(fp)
            for prod in decoded:
                products.append(Product(prod['id'], prod['code'], prod['pname']))

        return products

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

        for p in RandomProductGenerator.all_products:
            encoded_products.append(encoder.encode(p))

        check_and_create_if_not_exists(f"multiboms/{self.multi_bom.machines_info.root_directory}")

        with open(get_abs_file_path(f"multiboms/{self.multi_bom.machines_info.root_directory}/rand_products.json"),
                  "w") as f:
            f.write(dumps(encoded_products, default=lambda o: o.__dict__, indent=4))
            # dump(encoded_products, f, default=lambda o: o.__dict__, indent=4)

    def add_setup_time(self) -> None:
        """
        this method will decorate the list of machines with a randomly chosen setup time
        :return:
        """
        time_units_setup = self.multi_bom.machines_info.setup_time.time_units

        allowed_identical_machines = self.multi_bom.machines_info.allow_identical_machines

        # the number of identical machines is given by a parameter in datagen.json
        percent_of_identical_machines = self.multi_bom.machines_info.percent_of_identical_machines

        max_number_of_identical_machines = int(
            self.multi_bom.machines_info.machines_number * percent_of_identical_machines)

        # generate a setup time based on some input parameters
        setup_time = SetupTime.get_setup_time(self.multi_bom.machines_info.setup_time.min,
                                              self.multi_bom.machines_info.setup_time.step,
                                              self.multi_bom.machines_info.setup_time.max)

        for p in self.all_products:
            # define a counter to count the machines which were set up
            machines_counter = 0

            for m in p.machines:

                # if identical machines are allowed, retain this value to be reused
                if allowed_identical_machines and machines_counter < max_number_of_identical_machines:
                    m.setup_time = self.to_seconds(time_units_setup, setup_time)
                    machines_counter += 1
                else:
                    setuptime = self.to_seconds(time_units_setup,
                                                SetupTime.get_setup_time(self.multi_bom.machines_info.setup_time.min,
                                                                         self.multi_bom.machines_info.setup_time.step,
                                                                         self.multi_bom.machines_info.setup_time.max))
                    m.setup_time = setuptime

    def add_time_units(self) -> None:
        """
        this method will decorate the machines list with a time specific to create a unit of product
        :return:
        """
        time_units_assembly = self.multi_bom.machines_info.unit_assembly_time.time_units
        allowed_identical_machines = self.multi_bom.machines_info.allow_identical_machines
        percent_of_identical_machines = self.multi_bom.machines_info.percent_of_identical_machines

        # let's say that the number of identical machines could be only percent_of_identical_machines  from the total
        # number of the machines
        max_number_of_identical_machines = int(
            self.multi_bom.machines_info.machines_number * percent_of_identical_machines)

        for p in self.all_products:
            # define a counter to count the machines which were set up
            machines_counter = 0

            generic_execution_time = self.to_seconds(time_units_assembly,
                                                     UnitAssemblyTime.get_unit_assembly_time(
                                                         self.multi_bom.machines_info.setup_time.min,
                                                         self.multi_bom.machines_info.setup_time.step,
                                                         self.multi_bom.machines_info.setup_time.max))

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


class RandomProductDecoder(JSONDecoder):
    """
    Helper class used to deserialize the entries in the products.json file
    """

    multi_bom = None

    def __init__(self, multi_bom: MultiBom):
        """
        Constructor for the class
        """
        super().__init__()
        RandomProductDecoder.multi_bom = multi_bom

    @classmethod
    def decode(cls) -> List[Product]:
        decoded_products = []

        with open(f"../multiboms/{cls.multi_bom.machines_info.root_directory}/rand_products.json") as f:
            products_list = load(f)

            for crt_prod in products_list:
                vals = crt_prod.values()
                product = Product(*vals)
                decoded_products.append(product)

        return decoded_products


if __name__ == "__main__":
    products = RandomProductGenerator().generate_products(NUMBER_OF_PRODUCTS)
    RandomProductGenerator.export()
    products = RandomProductGenerator.decode()
    print(products)

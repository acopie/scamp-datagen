import random
import logging

from json import JSONEncoder, dumps, load
from typing import Any, List, AnyStr, Dict
from anytree.exporter import JsonExporter
from scipy.stats import norm, truncnorm

from datagen.common.utility import get_abs_file_path

from datagen.multi.msequencer import MachineSequencer
from datagen.multi.distribution import distribution_params

# the file where machines are written, in order to build the Machine objects
MACHINES_FILE = "temp/machines.json"

log = logging.getLogger("main")


class Machine:
    """
    class modelling a Machine in the production system.
    Every machine has an id, a name and an Overall Equipment Effectiveness (oee)
    """

    def __init__(self, id: int, name: AnyStr = None, oee: float = 1):
        self.id: int = id
        if name == None:
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

    def __str__(self):
        return f"{{'id':{self.id}, 'name':{self.name}, 'oee':{self.oee}}}"


class MachineEncoder(JSONEncoder):
    """
    Helper class needed for Machine class serialization
    """

    def default(self, obj: Any) -> dict:
        return obj.__dict__


class MachineJsonExporter(JsonExporter):
    def get_value(self, node):
        if isinstance(node.name, Machine):
            return MachineEncoder().default(node.name)
        return super().get_value(node)


class Machines:
    """
    Class containing all the machines in our system
    """

    # list of Machine instances
    machines: List[Machine] = []

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
        machines_number = self.bom.machines_info.machines_number

        # here we build the machines by passing a unique identifier, a name and a random OEE value
        for _ in range(machines_number):
            if self.bom.machines_info.oee.distribution == "normal":
                mean, std_dev = distribution_params(self.bom)

                # normal distribution (no truncation)
                # machine_oee = round(norm.rvs(mean, std_dev), 3)

                # use truncated normal distribution
                truncated_norm = truncnorm((self.bom.machines_info.oee.min - mean) / std_dev,
                                           (self.bom.machines_info.oee.max - mean) / std_dev,
                                           loc=mean, scale=std_dev)
                machine_oee = round((truncated_norm.rvs(1)[0]), 3)

            elif self.bom.oee.distribution == "uniform":
                machine_oee = round(random.randrange(self.bom.oee.min, self.bom.oee.max), 3)
            else:
                raise ValueError("Not a valid value for the statistical distribution")

            crt_machine = Machine(id=MachineSequencer().id, oee=machine_oee)

            Machines.machines.append(crt_machine)

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
            f.write(dumps(encoded_machines, indent=4))

    @classmethod
    def import_machines(cls):
        decoded_machines = None
        try:
            with open(get_abs_file_path(MACHINES_FILE)) as f:
                decoded_machines = load(f)
        except FileNotFoundError as e:
            log.error("The source file for machines was not found...")

        return decoded_machines


class MachinesEncoder(JSONEncoder):
    """
    Helper class needed for Machines class serialization
    """

    def encode(self, obj: Any) -> str:
        return obj.__dict__

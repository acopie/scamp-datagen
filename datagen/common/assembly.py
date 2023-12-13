"""
Module related to the time needed to execute a specific operation/product. Contains the config parameters needed
to generate a unit execution time and also the class modelling the Overall Equipment Effectiveness (OEE)

@author Adrian
"""

import random
from typing import Dict


class UnitAssemblyTime(object):
    """
    Represents the assembly time necessary for making a unit of a specific product
    """

    def __init__(self, dct: Dict[str, int]):
        """
        :param: dct - a dictionary containing info about the minimum time for assembling a product unit,
                a step used to increment teh assembling time for a product unit
                and the maximum time for assembling a product unit
        """
        self.min = dct["min"]
        self.step = dct["step"]
        self.max = dct["max"]
        self.time_units = dct["time_units"]

    @classmethod
    def get_unit_assembly_time(cls,
                                min: int,
                                step: int,
                                max: int) -> int:
        """
        builds a unit assembly time based on the parameters provided in BOM
        :param min:
        :param step:
        :param max:
        :return:
        """
        steps_number = (max - min) // step
        return min + random.randint(0, steps_number) * step


class Oee:
    """
    Class representing the OEE (Overall Equipment Effectiveness) for an operation
    """

    def __init__(self, dct: Dict):
        self.min = dct.get("min", 0)
        self.max = dct.get("max", 1)
        self.distribution = dct.get("distribution", "uniform")

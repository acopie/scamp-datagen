import random

"""
Represents the setup_time configuration in datagen.json file

@author Adrian
"""


class SetupTime(object):

    def __init__(self, dct):
        self.min = dct["min"]
        self.step = dct["step"]
        self.max = dct["max"]
        self.time_units = dct["time_units"]

    @classmethod
    def get_setup_time(cls, min: int, step: int, max: int) -> int:
        steps_number = (max - min) // step
        return min + random.randint(0, steps_number) * step

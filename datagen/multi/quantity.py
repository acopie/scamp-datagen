import random


class Quantity(object):

    def __init__(self, dct):
        self.min = dct["min"]
        self.step = dct["step"]
        self.max = dct["max"]

    @classmethod
    def get_quantity(cls, min: int, step: int, max: int) -> int:
        steps_number = (max - min) // step
        return min + random.randint(0, steps_number) * step

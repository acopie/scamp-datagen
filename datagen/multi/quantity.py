import random


class Quantity(object):

    def __init__(self, dct, seed = None):
        self.min = dct["min"]
        self.step = dct["step"]
        self.max = dct["max"]
        if seed is not None:
            random.seed(seed)


    def genereate_quantity(self) -> int:
        steps_number = (self.max - self.min) // self.step
        return self.min + random.randint(0, steps_number) * self.step

    @classmethod
    def get_quantity(cls, min: int, step: int, max: int) -> int:
        steps_number = (max - min) // step
        return min + random.randint(0, steps_number) * step


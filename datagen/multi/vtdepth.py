import random


class VerticalTreeDepth(object):
    """
    Models the depth of the vertical tree which is to be attached to the last level of the n-ary tree, representing
    the standard BOM

    @author: Adrian
    """

    def __init__(self, dct):
        self.min = dct["min"]
        self.step = dct["step"]
        self.max = dct["max"]
        self.probability = dct["probability"]

    @classmethod
    def get_depth(cls, min: int, step: int, max: int) -> int:
        steps_number = (max - min) // step
        return min + random.randint(0, steps_number) * step

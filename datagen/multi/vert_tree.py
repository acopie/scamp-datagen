"""
This module is related to the characteristics of the vertical tree in the BOM

@author: Adrian
"""

from random import randint


class VerticalTreeDepth:
    def __init__(self, min: int, max: int, step: int, probability: float):
        self.min = min
        self.max = max
        self.step = step
        self.probability = probability

    @classmethod
    def get_depth(cls, min: int, step: int, max: int) -> int:
        steps_number = (max - min) // step
        return min + randint(0, steps_number) * step

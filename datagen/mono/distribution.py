"""
This module will compute some parameters needed for computing random values based on normal distribution

@author: Adrian
"""
from math import sqrt


def distribution_params(bom):
    # compute the mean of the interval
    mean = (bom.oee.min + bom.oee.max) / 2

    # compute the standard deviation of the values from the mean
    # here we use the formula std_dev = (max - min) / 2 * sqrt(3)
    std_dev = (bom.oee.max - bom.oee.min) / (2 * sqrt(3))

    return (mean, std_dev)

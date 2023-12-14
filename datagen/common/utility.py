"""
This module contains ua collection of utility functions that are used by other modules

@Author: Adrian
"""

import os
import datetime
import random

MAX_DAYS = 30
MAX_HOURS = 24


def get_abs_file_path(file: str) -> str:
    module_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(module_dir, os.pardir))
    config_path = os.path.abspath(os.path.join(parent_dir, file))

    return config_path


def check_and_create_if_not_exists(dir: str) -> None:
    """
    Checks if the directory exists and creates it if it doesn't

    :param dir: the directory to be checked
    :return: None
    """
    if not os.path.exists(get_abs_file_path(dir)):
        # Create the directory
        os.makedirs(get_abs_file_path(dir))


def create_future_date() -> datetime:
    """
    Creates a future date starting at the start_date by adding a number of days and hours

    :return: a future date starting at start_date by adding a number of days and hours
    """

    start_date = datetime.datetime.now()

    random_days = random.randint(0, MAX_DAYS)
    random_hours = random.randint(0, MAX_HOURS)

    end_date = start_date + datetime.timedelta(days=random_days, hours=random_hours)
    return end_date

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

import datetime
import random
import os

from json import dumps
from anytree.exporter import JsonExporter

from datagen.multi.root_dir import RootDir
import datagen.common.utility as cu


MAX_DAYS = 30
MAX_HOURS = 24

RELATIVE_BOMS_DIR = "../datagen/multiboms"


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


def save_bom(bom_file, exporter: JsonExporter, node):
    # save the initial directory because at the end of the function we want to restore it back
    initial_dir = os.getcwd()

    root_dir = RootDir().get()

    destination_path = os.path.join(RELATIVE_BOMS_DIR, root_dir)

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    os.chdir(destination_path)
    with open(bom_file, 'w') as f:
        f.write(exporter.export(node))

    # restore the initial directory
    os.chdir(initial_dir)


def save_metainfo(bom_file, metainfo):
    # save the initial directory because at the end of the function we want to restore it back
    initial_dir = os.getcwd()

    root_dir = RootDir().get()

    destination_path = os.path.join(RELATIVE_BOMS_DIR, root_dir)

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    os.chdir(destination_path)
    with open(os.path.join(cu.get_abs_file_path(destination_path), bom_file), 'w') as f:
        f.write(dumps(metainfo, default=lambda o: o.__dict__, indent=4))

    # restore the initial directory
    os.chdir(initial_dir)


if __name__ == '__main__':
    future_date = create_future_date()
    print(future_date)

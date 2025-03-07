import os
import sys
import argparse

# Get the parent directory of the current file
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Add the parent directory to the Python path
sys.path.append(parent_dir)

from datagen.multi.main import start
from datagen.mono.main_all import nary_trees
from datagen.mono_variants.main import variate_instance


def errored_action() -> None:
    print("Invalid mode. Please use one of the following modes: multi, mono")


actions = {"multi": start, "mono": nary_trees, "variate": variate_instance}

parser = argparse.ArgumentParser(description="SCAMP-ML data generator")

# Define your command line parameters
parser.add_argument("mode", help="The working mode of the data generator")
parser.add_argument('-c', '--configFilePath', help='the configuration file path', type=str)

# Parse the command line arguments
args = parser.parse_args()

# Access the parsed arguments
action = actions.get(args.mode, errored_action)

action(args.configFilePath)

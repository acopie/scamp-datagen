""""
This module contains the entry point of the data generator and allows the user to generate either standard or mixed
trees directly from the command line

Just be sure that the modules installed in the virtual environment of the projects are available at the time of the run

For this, one can change directory  to the root of the project and run the following command:

source venv/bin/activate

This will activate the virtual environment and the modules will be available for the run

Then you can run the data generator as follows:

python datagen/data_gen.py --type standard
python datagen/data_gen.py --type mixed

@author: Adrian
"""

import argparse
from mixed_tree import mixed_trees
from main_all import nary_trees


def main():
    parser = argparse.ArgumentParser(description='Generates arbitrary trees for scheduled processes simulation.')

    parser.add_argument('--type', type=str, help='The type of the tree to be generated. It can be either "standard" '
                                                 'or "vertical".', required=True)

    args = parser.parse_args()

    tree_type = args.type

    if tree_type == "n-ary":
        print("Generating the standard tree...")
        nary_trees()
    elif tree_type == "mixed":
        print("Generating the mixed tree...")
        mixed_trees()


if __name__ == "__main__":
    main()

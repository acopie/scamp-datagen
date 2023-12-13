import argparse
from pathlib import Path

from datagen.config.examples_config import LETSA_EXAMPLE_FILE


def main():
    # Parse user arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--alg', type=str, default=None, required=False,
                        choices=['letsa'],
                        help='Algorithm/Heuristic example to add. One of [\'letsa\']',
                        )

    parser.add_argument('--datasource_type', type=str, required=True,
                        choices=['DB'],
                        help='How to save the example. One of [\'DB\']')

    parser.add_argument('--input_file', type=str, default=None, required=False,
                        help='Path to the yaml file describing the example')

    args = parser.parse_args()

    if (args.alg is None) and (args.input_file is None):
        raise Exception(
            'Error: You should provide the name of the algorithm/heuristic or the input file path to generate the example from.')

    if args.alg and args.input_file:
        raise Exception(
            'Error: You should provide only one argument: the name of the algorithm/heuristic or the input file path to generate the example from.')

    if args.alg:
        if args.alg == 'letsa':
            # load the pre-existing LETSA example from the article
            example_path = Path(LETSA_EXAMPLE_FILE)


if __name__ == '__main__':
    main()

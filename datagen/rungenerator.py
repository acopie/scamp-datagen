#
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import argparse

from datagen.multi.main import start
from datagen.mono.main_all import nary_trees
from datagen.mono_variants.main import variate_instance
from datagen.fixed.main import start_fixed
from datagen.bounded.main import start_bounded
from datagen.izomorf import cli_iso   

def errored_action() -> None:
    print("Invalid mode. Please use one of: multi, mono, variate, fixed, iso")

actions = {
    "multi": start,
    "mono": nary_trees,
    "variate": variate_instance,
    "fixed": start_fixed,
    "bounded": start_bounded,
    # "iso" NU intra aici pt pentru ca nu foloseste configFilePath
}

parser = argparse.ArgumentParser(description="SCAMP-ML data generator")

# mode + argumente comune
parser.add_argument("mode", help="Working mode: multi | mono | variate | fixed | iso")

# pentru modurile existente: config path
parser.add_argument("-c", "--configFilePath", type=str, help="Configuration file path")

# pentru iso: doua fisiere si eticheta (productid|pname|none)
parser.add_argument("--bomA", type=str, help="Path to first BOM (.json) for iso mode")
parser.add_argument("--bomB", type=str, help="Path to second BOM (.json) for iso mode")
parser.add_argument(
    "--label",
    choices=["productid", "pname", "none"],
    default="productid",
    help="Label attribute for isomorphism (default: productid). Use 'none' for structural-only."
)

args = parser.parse_args()

# pentru ISO (nu foloseste configFilePath)
if args.mode == "iso":
    if not args.bomA or not args.bomB:
        print("For 'iso' mode you must provide both --bomA and --bomB paths.")
        sys.exit(2)
    labelkey = None if args.label == "none" else args.label
    cli_iso(args.bomA, args.bomB, labelkey=labelkey)
    sys.exit(0)

# Restul modurilor raman neschimbate
action = actions.get(args.mode, errored_action)
action(args.configFilePath)


"""
py datagen\rungenerator.py bounded -c config\bounded-config.json
py datagen\rungenerator.py iso --bomA ... --bomB ... --label pname| none
py datagen\rungenerator.py bounded -c config\fixed-config.json
py datagen\config\generate_variants_config.py --help

"""


import os
import json
import random
import argparse
from pathlib import Path
import datetime

DEFAULT_SOURCE_DIR = "/Users/User/scamp-datagen/datasets/ASP-DEEP"
DEFAULT_OUTPUT_PATH = "/Users/User/scamp-datagen/datagen/config/variants-auto-generated"
DEFAULT_GENERATED_PATH = "/Users/User/scamp-datagen/datagen/boms/variants-auto-generated-location"
DEFAULT_NUM_VARIANTS = 2

PERTURBATION_TYPES = ['add_leaf_operation', 'remove_leaf_operation', 'new_machine_configuration']
VALUE_TYPES = ['percentage', 'absolute']
PERCENTAGE_VALUES = [20, 40, 60, 80]
ABSOLUTE_VALUES = [2, 4, 6, 8]

MACHINE_NO_VALUES = [10, 20, 30]
MIN_ALT_VALUES = [1, 2]
MAX_ALT_VALUES = [3, 4, 5]

def list_json_files(source_dir):
    return [str((Path(source_dir) / f).as_posix()) for f in os.listdir(source_dir) if f.endswith('.json')]

def build_variant(path, ptype, value_type, value, generated_path):
    base = {
        "initial_instance_path": [path],
        "seed": 110,
        "root_quantity_min": 100,
        "root_quantity_max": 500,
        "generated_instances_number": random.choice([2, 3, 5]),
        "generated_instances_path": generated_path,
        "generated_instances_name": f"auto_{Path(path).stem}_{ptype}_{value_type}_{value}"
        
    }

    if ptype == "new_machine_configuration":
        base["machine_assignment_perturbation"] = {
            "type": ptype,
            "machine_no": random.choice(MACHINE_NO_VALUES),
            "min_alternatives": random.choice(MIN_ALT_VALUES),
            "max_alternatives": random.choice(MAX_ALT_VALUES)
        }
    else:
        base["operations_graph_perturbation"] = {
            "type": ptype,
            "value_type": value_type,
            "value": value
        }

    base["renumerotate_operations_starting_with"] = random.randint(1, 4)
    base["renumerotate_machines_starting_with"] = random.randint(1, 3)

    
    return base

def generate_variants(source_dir, num_variants, only_perturbation_type, generated_path):
    json_paths = list_json_files(source_dir)
    variants = []

    for _ in range(num_variants):
        path = random.choice(json_paths)
        ptype = only_perturbation_type or random.choice(PERTURBATION_TYPES)

        if ptype == "new_machine_configuration":
            variant = build_variant(path, ptype, None, None, generated_path)
        else:
            value_type = random.choice(VALUE_TYPES)
            value = (
                random.choice(PERCENTAGE_VALUES) if value_type == "percentage"
                else random.choice(ABSOLUTE_VALUES)
            )
            variant = build_variant(path, ptype, value_type, value, generated_path)

        variants.append(variant)

    return {"instance_variants": variants}

def main():
    
    parser = argparse.ArgumentParser(description="Generate automatic variant config file.")
    parser.add_argument("--source-dir", type=str, default=DEFAULT_SOURCE_DIR, help="Folder with input JSONs.")
    parser.add_argument("--num", type=int, default=DEFAULT_NUM_VARIANTS, help="Number of variants to generate.")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_PATH, help="Path to output .json config file.")
    parser.add_argument("--only-perturbation-type", type=str, choices=PERTURBATION_TYPES, help="Restrict to a single perturbation type.")
    parser.add_argument("--generated-path", type=str, default=DEFAULT_GENERATED_PATH,help="Path where the generated instances will be saved (used in each variant)."
)

    args = parser.parse_args()

    variants_dict = generate_variants(
        source_dir=args.source_dir,
        num_variants=args.num,
        only_perturbation_type=args.only_perturbation_type,
        generated_path=args.generated_path
    )


    filename = f"config_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path = os.path.join(args.output, filename)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(variants_dict, f, indent=2)

    print(f"Generated {len(variants_dict['instance_variants'])} variants in: {args.output}")

if __name__ == "__main__":
    main()

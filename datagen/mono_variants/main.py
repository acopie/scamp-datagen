"""
This is the entry point of data generator
"""
import random
from datetime import date, timedelta

from anytree import Node, RenderTree, Resolver
from anytree.importer import JsonImporter

from datagen.common.utility import get_abs_file_path
from datagen.mono_variants.load_instance import Instance
from datagen.mono_variants.variants_processing import PerturbationVariantDecoder, PerturbationVariant
from datagen.mono.gentree import render_tree, export_tree

def print_name(node) -> None:
    """
    callback function used to traverse the tree and perform a
    n action
    :param node: the root (or upper) tree node
    :return:
    """
    print(node.pname)


def process_perturbation(perturbation: PerturbationVariant):
        print("-------process_perturbation-----------")
        #perturb existing file
        INPUT_FILE_PATH = get_abs_file_path(perturbation.initial_instance_path)
        OUTPU_FILE_PATH = get_abs_file_path(perturbation.generated_instances_path)

        instance = Instance(INPUT_FILE_PATH, seed = perturbation.seed)

        for i in range(1, perturbation.generated_instances_number + 1):
            tree = perturbation.perturb(instance, instance.get_any_tree())

            resolver = Resolver('name')
            root_node = resolver.get(tree, '/root')
            export_tree(root_node, f'{OUTPU_FILE_PATH}/{perturbation.generated_instances_name}_{i}.json')
            rendered_tree = ""
            for line in RenderTree(root_node):
                rendered_tree += f"{line.pre} [{line.node.operationid}]  [{line.node.parentid}] [{line.node.code}]\n"
                print(
                    f"{line.pre} [{line.node.operationid}]  [{line.node.parentid}] [{line.node.code}]")
            with open(f'{OUTPU_FILE_PATH}/{perturbation.generated_instances_name}_{i}.json.tree', "w") as f:
                f.write(rendered_tree)

def variate_instance(configuration_file_path : str):
    #generate the list of all the perturbations variants
    all_perturbations = PerturbationVariantDecoder.build(configuration_file_path)
    print("all_perturbations", len(all_perturbations))
    for p in all_perturbations:
        process_perturbation(p)


if __name__ == '__main__':
    variate_instance()

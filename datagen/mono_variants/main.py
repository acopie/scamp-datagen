"""
This is the entry point of data generator
"""
import random
from datetime import date, timedelta

from anytree import Node, RenderTree, Resolver
from pathlib import Path

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
        output_file_path = get_abs_file_path(perturbation.generated_instances_path)

        for input_file_path in [get_abs_file_path(path) for path in perturbation.initial_instance_path]:
            instance = Instance(input_file_path, seed = perturbation.seed)
            for var_no in range(1, perturbation.generated_instances_number + 1):
                tree = perturbation.perturb(instance, instance.get_any_tree())

                resolver = Resolver('name')
                root_node = resolver.get(tree, '.')
                file_name = Path(input_file_path).stem
                final_file_name = f'{output_file_path}/{file_name}_{perturbation.generated_instances_name}_ao{len(root_node.metainfo['operations_list'])}_am{len(root_node.metainfo['machines_list'])}_{var_no}.json'
                export_tree(root_node, final_file_name)
                rendered_tree = ""
                for line in RenderTree(root_node):
                    rendered_tree += f"{line.pre} [{line.node.operationid}]  [{line.node.parentid}] [{line.node.code}]\n"
                    print(
                        f"{line.pre} [{line.node.operationid}]  [{line.node.parentid}] [{line.node.code}]")
            
                with open(f'{final_file_name}.tree', "w", encoding="utf-8") as f:
                    f.write(rendered_tree)


def variate_instance(configuration_file_path : str):
    #generate the list of all the perturbations variants
    all_perturbations = PerturbationVariantDecoder.build(configuration_file_path)
    print(configuration_file_path, all_perturbations)
    print("all_perturbations", len(all_perturbations))
    for p in all_perturbations:
        process_perturbation(p)


if __name__ == '__main__':
    variate_instance("./config/variants-config.json")

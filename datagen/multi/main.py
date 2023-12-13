"""
This is the entry point in the multi-product BOM generator
Here, one read the content of the multi-config.json file and generates the BOM trees for each of the entries

@author: Adrian
"""

import os
import sys
import random

import datagen.multi.bomcache as bomcache
import datagen.common.maintenances

from datetime import datetime
from random import choice

from anytree import Node, RenderTree, Resolver

from datagen.common.rootprod import RootProduct, RootNode
from datagen.common.sequencer import Sequencer
from datagen.common.scampdate import datemask
from datagen.common.config import GENERATE_SIMPLE_TREE

from datagen.multi.bom import MultiBomDecoder, MultiBoms, MultiBom
from datagen.multi.maintenance import Maintenance
from datagen.multi.machines import Machines
from datagen.multi.randpgen import RandomProductGenerator
from datagen.multi.metainfo import MetaInfo
from datagen.multi.quantity import Quantity
from datagen.multi.gentree import create_children, import_tree, export_tree, walk, render_tree, \
                    simple_render_tree, create_complex_tree
from datagen.multi.serproduct import SerializableProductDecoder
from datagen.multi.root_dir import RootDir
from datagen.multi.prodmachine import ProdMachines, ProdMachinesAll
from datagen.multi.sanity import SanityChecker
from datagen.multi.stockgen import StockGeneratorMulti
from datagen.common.stocks import Stocks


def print_name(node: Node) -> None:
    """
    Callback function used to traverse the tree and perform an action

    :param node: the root (or upper) tree node
    :return: None
    """
    print(node.pname)


def max_nodes_number(children: int, depth: int) -> int:
    """
    Computes the maximum number of nodes for the BOM tree (m-ary tree) based on its depth and children per node
    """
    max_nodes = 0
    for i in range(depth):
        max_nodes += pow(children, i)
    return max_nodes


def compute_end_delivery_date(multi_bom: MultiBom) -> datetime:
    """
    Computes the end delivery date for the entire BOM
    """

    all_end_delivery_dates = []
    for crt_bom in multi_bom.products_info:
        all_end_delivery_dates.append(datetime.strptime(crt_bom.delivery_date, datemask()))

    return max(all_end_delivery_dates)


def process_bom(multi_bom: MultiBom) -> None:
    """
    Because we have to do with a multiple BOM, we have to iterate over all the BOMs defined in the multi-config.json
    and generate the trees for each of them
    """

    # determine the possible maintenance intervals for the machines involved in the current product
    maintenance_intervals = Maintenance.get_maintenance_intervals(multi_bom)

    Stocks().reset()
    ProdMachinesAll.reset()

    bomcache.MultiBomCache.add_bom(multi_bom)
    RootDir().set(multi_bom.machines_info.root_directory)

    # generate the products that will be used to populate the BOM tree
    random_product_generator = RandomProductGenerator(multi_bom)
    random_product_generator.generate_products()

    # generate the stocks of raw materials
    stocks_generator = StockGeneratorMulti(multi_bom)
    stocks_generator.generate_stocks(multi_bom)
    stocks_generator.export(multi_bom)

    for crt_bom in multi_bom.products_info:

        # if one need to attach the vertical tree to the n-ary tree
        # to avoid having the auxiliary vertical tree, set the min parameter of the vertical_tree_depth in the
        # multi-config.json to 0
        GENERATE_COMPLEX_TREE = crt_bom.vertical_tree_depth.max > 0

        # the name of output file
        OUTPUT_FILE = crt_bom.output_file

        # maximum depth of the tree representing the BOM
        MAX_DEPTH = crt_bom.max_depth

        # the maximum number of children per node
        MAX_CHILDREN = crt_bom.max_children

        MAX_PRODUCTS = multi_bom.machines_info.prod_number

        # the case in which we have a tree with a single child per node and the depth level exceeds
        # the number of products we have to stop, because we cannot provide enough products to build the BOM
        # (a product cannot be used more than once per a single path)
        if (MAX_DEPTH > MAX_PRODUCTS) and (MAX_CHILDREN == 1):
            print("The maximum depth of the tree cannot be greater than the maximum number of products. Now exiting...")
            sys.exit()

        # compute the maximum number of nodes for the m-ary tree having MAX_DEPTH levels and MAX_CHILDREN children
        MAX_NODES_NUMBER = max_nodes_number(MAX_CHILDREN, MAX_DEPTH)

        # compute the ratio between the max number of nodes and the max number of products used to build this BOM
        acceptance_ratio = MAX_NODES_NUMBER / MAX_PRODUCTS

        # in case this parameter is true, the number of children per node will be in the
        # interval [1, MAX_CHILDREN] otherwise, if false, the number of children will be MAX_CHILDREN
        RANDOMIZE_CHILDREN = crt_bom.randomize_children

        # cache the current BOM for further usage
        bomcache.BomCache.add_bom(crt_bom)

        # the maximum number of alternative machine on which a product could be processed
        MAX_ALTERNATIVES_MACHINES_NUMBER = multi_bom.machines_info.max_alternatives_machines_number

        datagen.common.maintenances.Maintenances.reset()

        decoder = SerializableProductDecoder(multi_bom)
        products = decoder.decode()

        # the product used for the root node. We pop a product from the list because the root must be unique
        root_product = choice(products)

        # add the root product in the RootProduct singleton, so no other identical entries won't be present in BOM
        RootProduct.add_root(root_product)

        # start to prepare the operations list
        if not hasattr(root_product, 'operations'):
            root_product.operations = []

        root_operation = Sequencer().index
        root_product.operations.append(root_operation)

        # put the info about product id and machines ids in the MetaInfo class
        MetaInfo().reset_machines()
        MetaInfo().reset_operations()
        MetaInfo().add_metainfo(root_product, root_operation)
        ProdMachinesAll.add(ProdMachines(root_product.pid, root_product.machines))

        root = Node("root", parent=None, operationid=root_operation, productid=root_product.pid,
                    code=root_product.code, pname=root_product.code,
                    parentid=None, start_date=multi_bom.machines_info.start_date,
                    delivery_date=crt_bom.delivery_date,
                    priority=random.randint(1, 10),
                    quantity=Quantity.get_quantity(crt_bom.quantity.min,
                                                   crt_bom.quantity.step,
                                                   crt_bom.quantity.max))

        RootNode().add_node(root)

        if GENERATE_COMPLEX_TREE:
            create_complex_tree(root, MAX_DEPTH, products, crt_bom, MAX_CHILDREN, random_children=RANDOMIZE_CHILDREN)
        else:
            # effectively create the generic tree
            create_children(root, MAX_CHILDREN, MAX_DEPTH, products, crt_bom, random_children=RANDOMIZE_CHILDREN)

        # generate the associated maintenances for the machines involved in root product, if necessary
        for i in maintenance_intervals:
            for crt_machine_id in MetaInfo().machines:
                if RandomProductGenerator.is_maintenance_generated(multi_bom):
                    crt_machine = Machines.get(crt_machine_id)
                    actual_maintenance_interval = Maintenance.build_maintenance_dates_ex(i[0], i[1])
                    datagen.common.maintenances.Maintenances.add(Maintenance(crt_machine, actual_maintenance_interval[0],
                                                              actual_maintenance_interval[1]))

        all_maintenances = datagen.common.maintenances.Maintenances.get_maintenances()
        all_encoded_maintenances = datagen.common.maintenances.Maintenances().to_json()

        # decorate the root node with some meta information  related to the products ids in the BOM and
        # the list of the unique ids of the alternate machines involved in the BOM
        resolver = Resolver('name')

        root_node = resolver.get(root, '/root')
        root_node.operations_list = MetaInfo().get_operations()

        # export the generated tree (BOM) in a json file
        export_tree(root, f"{OUTPUT_FILE}", False)

        # print the tree to the console for visualization
        print(RenderTree(root))

        node = import_tree(f"../multiboms/{RootDir().get()}/{OUTPUT_FILE}")
        render_tree(node)

        walk(root, print_name)

        # export the generated tree (BOM) in a json file (if needed)
        if GENERATE_SIMPLE_TREE:
            simple_tree_root_node = resolver.get(root, '/root')

            # render the smaller tree for debugging purposes
            print(RenderTree(simple_tree_root_node))

            simple_tree_node = import_tree(f"../multiboms/{multi_bom.machines_info.root_directory}/{OUTPUT_FILE}")
            simple_render_tree(simple_tree_root_node, crt_bom)

    # update the metainfo node with the right information
    metainfo = {"machines_list": MetaInfo().get_machines(),
                "maintenances": all_encoded_maintenances,
                "prod_machines": ProdMachinesAll.get()}

    MetaInfo().export(metainfo)

    print("Running the sanity checker...")

    SanityChecker(root, metainfo).walk(root)

    print("End of sanity check...")


def start() -> None:
    MultiBomDecoder.build()

    # all the BOMS in the system
    all_boms = MultiBoms.get_all()

    for multi_bom in all_boms:
        process_bom(multi_bom)


if __name__ == "__main__":

    MultiBomDecoder.build()

    # all the BOMS in the system
    all_boms = MultiBoms.get_all()

    for multi_bom in all_boms:

        process_bom(multi_bom)

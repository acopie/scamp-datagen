"""
This is the entry point of data generator
"""
import sys
import random

from anytree import Node, RenderTree, Resolver

import datagen.mono.maintenance
import datagen.mono.productgenerator
import datagen.mono.boms_processing
import datagen.common.maintenances

from datagen.common.config import GENERATE_SIMPLE_TREE
from datagen.common.importer import SProductDecoder
from datagen.common.sequencer import Sequencer
from datagen.common.rootprod import RootProduct, RootNode
from datagen.common.utility import get_abs_file_path, check_and_create_if_not_exists
from datagen.common.stocks import Stocks

from datagen.mono.bomcache import BomCache
from datagen.mono.quantity import Quantity
from datagen.mono.gentree import create_children, import_tree, export_tree, walk, render_tree, simple_render_tree
from datagen.mono.metainfo import MetaInfo
from datagen.mono.stockgen import StockGeneratorMono


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


def bom_process(bom: datagen.mono.boms_processing.Bom):
    # extract the BOM's parameters and put them in constants, so they can be further used

    # the name of output file
    OUTPUT_FILE = bom.output_file

    # maximum depth of the tree representing the BOM
    MAX_DEPTH = bom.max_depth

    # the maximum number of children per node
    MAX_CHILDREN = bom.max_children

    MAX_PRODUCTS = bom.prod_number

    # the case in which we have a tree with a single child per node and the depth level exceeds the number of products
    # we have to stop, because we cannot provide enough products to build the BOM (a product cannot be used more than
    # once per a single path)
    if (MAX_DEPTH > MAX_PRODUCTS) and (MAX_CHILDREN == 1):
        print("The maximum depth of the tree cannot be greater than the maximum number of products. Now exiting...")
        sys.exit()

    # compute the maximum number of nodes for the m-ary tree having MAX_DEPTH levels and MAX_CHILDREN children
    MAX_NODES_NUMBER = max_nodes_number(MAX_CHILDREN, MAX_DEPTH)

    # compute the ratio between the max number of nodes and the max number of products used to build this BOM
    acceptance_ratio = MAX_NODES_NUMBER / MAX_PRODUCTS

    # TODO: establish a reasonable value for which the BOM will continue to be built. If the ration is too large, it
    # means that too many entries in BOM have the same components (products)

    # in case this parameter is true, the number of children per node will be in the
    # interval [1, MAX_CHILDREN] otherwise, if false, the number of children will be MAX_CHILDREN
    RANDOMIZE_CHILDREN = bom.randomize_children

    SEED = bom.seed

    # reset the stocks before processing a new BOM
    Stocks().reset()

    # generate the stocks of raw materials
    stocks_generator = StockGeneratorMono(bom)
    stocks_generator.generate_stocks(bom)
    stocks_generator.export(bom)

    StockGeneratorMono(bom)

    # put the current BOM in cache
    BomCache.add_bom(bom)

    # the maximum number of alternative machine on which a product could be processed
    MAX_ALTERNATIVES_MACHINES_NUMBER = bom.max_alternatives_machines_number

    datagen.common.maintenances.Maintenances.reset()

    # now generate the list of all products in the system. This will be used by the tree builder
    datagen.mono.productgenerator.generate(bom)

    # let's create the memory representation of the products
    decoder = SProductDecoder()
    products = decoder.decode()

    # the product used for the root node. We pop a product from the list because the root must be unique
    root_product = random.choice(products)

    # add the root product in the RootProduct singleton, so no other identical entries won't be present in BOM
    RootProduct.add_root(root_product)

    # determine the possible maintenance intervals for the machines involved in the current product
    maintenance_intervals = datagen.mono.maintenance.Maintenance.get_maintenance_intervals()

    # set this interval in BOM too, for further needs
    bom.possible_maintenance_intervals = maintenance_intervals

    # start to prepare the operations list
    if not hasattr(root_product, 'operations'):
        root_product.operations = []

    root_operation = Sequencer().index
    root_product.operations.append(root_operation)

    # put the info about product id and machines ids in the MetaInfo class
    MetaInfo().reset_machines()
    MetaInfo().reset_operations()
    MetaInfo().add_metainfo(root_product, root_operation)

    # create the order corresponding to this BOM
    random.seed(SEED)
    # if necessary, generate an order which is attached to this BOM
    # TODO: maybe should be parameterized if useful (or extract the order info directly from BOM)
    # order = Order(Sequencer().index, root_product.productid, root_product.pname, random.randint(1, 100),
    #               bom.delivery_date)

    # order.export(f"boms/order_{OUTPUT_FILE}")

    # create the root of the tree
    root = Node("root", parent=None, operationid=root_operation, productid=root_product.productid,
                code=root_product.code, pname=root_product.pname,
                parentid=None, start_date=bom.start_date, delivery_date=bom.delivery_date,
                quantity=Quantity.get_quantity(bom.quantity.min, bom.quantity.step, bom.quantity.max),
                machines=root_product.machines, metainfo={})

    RootNode().add_node(root)

    # effectively create the generic tree
    create_children(root, MAX_CHILDREN, MAX_DEPTH, products, SEED, bom, random_children=RANDOMIZE_CHILDREN)

    # generate the associated maintenances for the machines involved in root product, if necessary
    for i in maintenance_intervals:
        for crt_machine_id in MetaInfo().machines:
            if datagen.mono.productgenerator.ProductGenerator.generate_maintenance(bom):
                crt_machine = datagen.mono.productgenerator.Machines.get(crt_machine_id)
                actual_maintenance_interval = datagen.mono.maintenance.Maintenance.build_maintenance_dates_ex(i[0], i[1])
                datagen.common.maintenances.Maintenances.add(
                    datagen.mono.maintenance.Maintenance(crt_machine, actual_maintenance_interval[0],
                                            actual_maintenance_interval[1]))

    all_encoded_maintenances = datagen.common.maintenances.Maintenances().to_json()

    # decorate the root node with some meta information  related to the products ids in the BOM and
    # the list of the unique ids of the alternate machines involved in the BOM
    resolver = Resolver('name')

    root_node = resolver.get(root, '/root')

    # update the metainfo node with the right information
    root_node.metainfo = {"operations_list": MetaInfo().get_operations(), "machines_list": MetaInfo().get_machines(),
                          "maintenances": all_encoded_maintenances}

    # export the generated tree (BOM) in a json file
    export_tree(root, get_abs_file_path(f"boms/{OUTPUT_FILE}"), False)

    # print the tree to the console for visualization
    print(RenderTree(root))

    node = import_tree(get_abs_file_path(f"boms/{OUTPUT_FILE}"))
    render_tree(node)

    walk(root, print_name)

    # export the generated tree (BOM) in a json file (if needed)
    if GENERATE_SIMPLE_TREE:
        simple_tree_root_node = resolver.get(root, '/root')

        # render the smaller tree for debugging purposes
        print(RenderTree(simple_tree_root_node))

        simple_tree_node = import_tree(get_abs_file_path(f"boms/{OUTPUT_FILE}"))
        simple_render_tree(simple_tree_root_node, bom)


def nary_trees():
    """
    Generates an n-ary tree with the number of levels and children per node specified in the configuration file
    """
    Sequencer().reset()

    # generate the list of all the BOMs defined in the system
    all_boms = datagen.mono.boms_processing.BomDecoder.build()

    for b in all_boms:
        bom_process(b)


if __name__ == "__main__":
    check_and_create_if_not_exists("boms")
    nary_trees()

    # Sequencer().reset()
    #
    # # generate the list of all the BOMs defined in the system
    # all_boms = boms_processing.BomDecoder.build()
    #
    # for b in all_boms:
    #     bom_process(b)

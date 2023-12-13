"""
This module is used to generate a random tree of products. The tree is much closer to the real life situations.

A possible (simplified) tree can be seen in the following image:


                                    o
                                /       \   \   \    \   \   \   \   \
                               o          o   o   o   o   o   o   o   o
                           /  / \        / \
                          o  o   o  o   o   o
                                 |          |
                                 o          o
                                 |          |
                                 o          o
                                            |
                                            o
                                            |
                                            o


@author: Adrian
"""
import sys
print(sys.modules)


#from datagen.common.sequencer import Sequencer
import datagen.common.sequencer
from anytree import AnyNode, RenderTree, Resolver
from quantity import Quantity
from random import choice, randint
from datagen.common.importer import SProductDecoder, SProduct
from datagen.common.rootprod import RootProduct, RootNode
from pathprods import PathProducts
from metainfo import MetaInfo
from gentree import export_tree, simple_render_tree
from bomcache import BomCache
from boms_processing import Bom
import logging
import boms_processing
import maintenances
import maintenance
import productgenerator
import random
import log_config

log_config.config()
log = logging.getLogger("main")

log.info("Starting the BOM generator")


def create_random_tree(node: AnyNode, depth: int, products, bom: Bom, num_children: int,
                       random_children: bool) -> AnyNode:
    """
    This function is used to create a random tree of products. The tree is much closer to the real life situations
    and it is a combination of an n-ary tree and one or more vertical trees, which are added at teh last level of
    the n-ary tree.

    :param node: The root node of the tree
    :param depth: The depth of the vertical tree
    :param products: The list of products from which we can choose
    :param bom: The BOM object
    :param num_children: The number of children for each node, related to teh standard BOM
    :param random_children: If the children number should be chosen randomly or not

    @author: Adrian
    """
    if depth == 0:
        return None

    number_of_children = random.randint(1, num_children) if random_children else num_children
    children_products = []

    for i in range(number_of_children):

        is_eligible_product = False

        while not is_eligible_product:
            product = random.choice(products)

            # Check to see if the randomly chosen product is the root of the BOM. If yes, we need to do another pick
            # The idea is that the root product cannot be used as a child of the BOM elsewhere. The root is the
            # final product and that's it!
            if product.productid == RootProduct.product.productid and product.pname == RootProduct.product.pname:
                continue

            operation_id = datagen.common.sequencer.Sequencer().index
            MetaInfo().add_metainfo(product, operation_id)

            if (product not in PathProducts.products) and (product not in children_products) and (
                    product is not RootNode().node):
                log.debug(f'{product.productid} is added to the path')
                is_eligible_product = True
                PathProducts.add_product(product)
                children_products.append(product)
            else:
                log.debug(f'The product with the id {product.productid} is a duplicate product. Picking a new one...')
                continue

            new_node_str = f"AnyNode(id='{datagen.common.sequencer.Sequencer().index}', parent=node, parentid={node.operationid}, operationid={operation_id}, productid={product.productid}, " \
                           f"code='{product.code}', pname='{product.pname}', quantity={Quantity.get_quantity(bom.quantity.min, bom.quantity.step, bom.quantity.max)}, machines={str(product.machines)})"

            # no need to return the node from create_random_tree() fnction because the node is added to the tree based
            # on the parent node
            create_random_tree(eval(new_node_str), depth - 1, products, bom, num_children, random_children)
            PathProducts.remove_product(product)

        if depth == 1:
            # it means we are at the last level of the tree, we attach the vertical trees here
            # randomly generate the vertical tree based on a 50% chance
            choices = [0, 1]
            if random.choice(choices) == 1:
                current_node = node
                tree_depth = bom.vertical_tree_depth.get_depth(bom.vertical_tree_depth.min,
                                                               bom.vertical_tree_depth.step,
                                                               bom.vertical_tree_depth.max)
                for _ in range(tree_depth):

                    product = random.choice(products)

                    # Check to see if the randomly chosen product is the root of the BOM. If yes, we need to do
                    # another pick. The idea is that the root product cannot be used as a child of the BOM elsewhere.
                    # The root is the final product and that's it!
                    if product.productid == RootProduct.product.productid and product.pname == RootProduct.product.pname:
                        continue

                    operation_id = datagen.common.sequencer.Sequencer().index
                    MetaInfo().add_metainfo(product, operation_id)

                    if (product not in PathProducts.products) and (product not in children_products) and (
                            product is not RootNode().node):
                        log.debug(f'The product with the id {product.productid} is added to the path')
                        children_products.append(product)

                    new_node_str = f"AnyNode(id='{datagen.common.sequencer.Sequencer().index}', parent=current_node, parentid={node.operationid}, operationid={operation_id}, productid={product.productid}, " \
                                   f"code='{product.code}', pname='{product.pname}', quantity={Quantity.get_quantity(bom.quantity.min, bom.quantity.step, bom.quantity.max)}, machines={str(product.machines)})"
                    new_node = eval(new_node_str)
                    current_node = new_node

    return node


def bom_processing(bom: Bom):
    # holds the number of children for the first level of the tree

    maintenances.Maintenances.reset()

    # put the current BOM in cache
    BomCache.add_bom(bom)

    # now generate the list of all products in the system. This will be used by the tree builder
    productgenerator.generate(bom)

    OUTPUT_FILE = bom.output_file

    maintenance_intervals = maintenance.Maintenance.get_maintenance_intervals()

    # let's create the memory representation of the products
    decoder = SProductDecoder()
    products = decoder.decode()

    root_product = choice(products)

    # start to prepare the operations list
    if not hasattr(root_product, 'operations'):
        root_product.operations = []

    # start clean sequencer
    datagen.common.sequencer.Sequencer().reset()

    root_operation = datagen.common.sequencer.Sequencer().index
    root_product.operations.append(root_operation)

    # put the info about product id and machines ids in the MetaInfo class
    MetaInfo().reset_machines()
    MetaInfo().reset_operations()
    MetaInfo().add_metainfo(root_product, root_operation)

    # add the root product in the RootProduct singleton, so no other identical entries won't be present in BOM
    RootProduct.add_root(root_product)

    # the root of the tree
    # create the root of the tree
    root = AnyNode(id="root", parent=None, operationid=root_operation, productid=root_product.productid,
                   code=root_product.code, pname=root_product.pname,
                   parentid=None, start_date=bom.start_date, delivery_date=bom.delivery_date,
                   quantity=Quantity.get_quantity(bom.quantity.min, bom.quantity.step, bom.quantity.max),
                   machines=root_product.machines, metainfo={})

    # effectively create the generic tree
    create_random_tree(root, 6, products, bom, 3, random_children=True)

    # generate the associated maintenances for the machines involved in root product, if necessary
    for i in maintenance_intervals:
        for crt_machine_id in MetaInfo().machines:
            if productgenerator.ProductGenerator.generate_maintenance(bom):
                crt_machine = productgenerator.Machines.get(crt_machine_id)
                actual_maintenance_interval = maintenance.Maintenance.build_maintenance_dates_ex(i[0], i[1])
                maintenances.Maintenances.add(maintenance.Maintenance(crt_machine, actual_maintenance_interval[0],
                                                                      actual_maintenance_interval[1]))

    all_encoded_maintenances = maintenances.Maintenances().to_json()

    # decorate the root node with some meta information  related to the products ids in the BOM and
    # the list of the unique ids of the alternate machines involved in the BOM
    resolver = Resolver('id')

    root_node = resolver.get(root, '/root')

    # update the metainfo node with the right information
    root_node.metainfo = {"operations_list": MetaInfo().get_operations(), "machines_list": MetaInfo().get_machines(),
                          "maintenances": all_encoded_maintenances}

    # export the generated tree (BOM) in a json file
    export_tree(root, f"boms/{OUTPUT_FILE}", False)

    # print the tree to the console for visualization
    print(RenderTree(root))

    simple_render_tree(root, bom)


def mixed_trees() -> None:
    """
    This function generates a mixed tree, with both n-ary and vertical trees
    """

    # reset the bom cache
    BomCache.reset()

    boms = boms_processing.BomDecoder.build_ex()

    for crt_bom in boms:
        bom_processing(crt_bom)

    log.info("BOM generator finished")


# the main function. It reads from the configuration file the BOMs to be generated, then it starts to process them
# one by one
if __name__ == '__main__':
    mixed_trees()

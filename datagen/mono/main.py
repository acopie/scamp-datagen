"""
This is the entry point of data generator
"""
import random
from datetime import date, timedelta

from anytree import Node, RenderTree, Resolver

from .boms_processing import BomDecoder, Boms
from .gentree import create_children, import_tree, export_tree, walk, render_tree
from datagen.common.importer import SProductDecoder
from .metainfo import MetaInfo
from .order import Order
from .productgenerator import generate
from datagen.common.sequencer import Sequencer


def print_name(node) -> None:
    """
    callback function used to traverse the tree and perform a
    n action
    :param node: the root (or upper) tree node
    :return:
    """
    print(node.pname)


def main():
    # generate the list of all the BOMs defined in the system
    BomDecoder.build()

    # now, let's take one of the BOMs in the list and generate it
    bom = Boms.get_bom("Bom_1_2")

    # extract the BOM's parameters and put them in constants, so they can be further used

    # the name of output file
    OUTPUT_FILE = bom.output_file

    # maximum depth of the tree representing the BOM
    MAX_DEPTH = bom.max_depth

    # the maximum number of children per node
    MAX_CHILDREN = bom.max_children

    # in case this parameter is true, the number of children per node will be in the
    # interval [1, MAX_CHILDREN] otherwise, if false, the number of children will be MAX_CHILDREN
    RANDOMIZE_CHILDREN = bom.randomize_children

    SEED = bom.seed

    # the maximum number of alternative machine on which a product could be processed

    MAX_ALTERNATIVES_MACHINES_NUMBER = bom.max_alternatives_machines_number

    # now generate the list of all products in the system. This will be used by the tree builder
    generate(bom)

    # let's create the memory representation of the products
    decoder = SProductDecoder()
    products = decoder.decode()

    # the product used for the root node. We pop a product from the list because the root must be unique
    root_product = products.pop()

    # put the info about product id and machines ids in the MetaInfo class
    MetaInfo().add_metainfo(root_product)

    date_in_future = date.today() + timedelta(days=random.randint(1, 100))

    # create the order corresponding to this BOM
    random.seed(SEED)
    order = Order(Sequencer().index, root_product.productid, root_product.pname, random.randint(1, 100),
                  bom.delivery_date)

    order.export(f"boms/order_{OUTPUT_FILE}")

    # create the root of the tree
    root = Node("root", parent=None, operationid=Sequencer().index, productid=root_product.productid,
                code=root_product.code, pname=root_product.pname,
                parentid=None, delivery_date=bom.delivery_date, machines=root_product.machines)

    # effectively create the generic tree
    create_children(root, MAX_CHILDREN, MAX_DEPTH, products, SEED, random_children=RANDOMIZE_CHILDREN)

    # decorate the root node with some meta information  related to the products ids in the BOM and
    # the list of the unique ids of the alternate machines involved in the BOM
    resolver = Resolver('name')
    root_node = resolver.get(root, '/root')
    root_node.products_list = MetaInfo().get_products()
    root_node.machines_list = MetaInfo().get_machines()

    # export the generated tree (BOM) in a json file
    export_tree(root, f"boms/{OUTPUT_FILE}", False)

    # print the tree to the console for visualization
    print(RenderTree(root))

    node = import_tree(f"../boms/{OUTPUT_FILE}")
    render_tree(node)

    walk(root, print_name)


if __name__ == '__main__':
    main()

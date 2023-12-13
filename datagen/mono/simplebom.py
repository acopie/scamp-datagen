"""
Module whic is related to a simplified version of the BOM.  It is used for debugging purposes.
"""

from anytree import Node, Walker, RenderTree
from boms_processing import Bom

from productgenerator import *
from typing import List, Tuple
from datagen.common.rootprod import RootProduct

from datagen.common.treeutil import NodeCounter
from prettytable import PrettyTable

from datagen.common.config import PRINT_TABULAR_TREE_PATHS

DUPLICATE_NODES_FILE = "./out/simple_duplicate_nodes.txt"


class SimpleTreeRootNode:
    """
    class that models the root node of the simplified tree
    """
    instance = None
    node = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            return super().__new__(*args, **kwargs)

    @classmethod
    def add_node(cls, n: Node):
        """
        Adds a root product which will be used at every product generation
        """
        cls.node = n

    @classmethod
    def reset(cls):
        """Resets the existent root product to be used for another BOM"""
        cls.node = None


class SimpleTreePathProducts:
    """
    This singleton holds the products on a tree path

    @author Adrian
    """

    # instance: type['SimpleTreePathProducts'] = None
    products: List[Product] = list()

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            return super().__new__(*args, **kwargs)

    @classmethod
    def add_product(cls, p: Product):
        """
        Adds a product belonging to a specific path in BOM tree
        """
        if p not in cls.products:
            cls.products.append(p)

    @classmethod
    def reset(cls):
        """Resets the existent product items in the products list"""
        cls.products.clear()


def contains_duplicates(l: List) -> bool:
    """
    Checks if a list contains duplicates
    :param l: the list to be checked
    :return: True if the list contains duplicates, False otherwise
    """
    return len(l) != len(set(l))


def print_tree_path(nodes: Tuple[Node, ...]) -> None:
    """
    Prints the paths of the BOM in a table representation
    """
    table = PrettyTable()
    table.field_names = ["name", "depth", "productid", "parentid", "code"]

    for node in nodes:
        table.add_row([node.name, node.depth, node.productid, node.parentid, node.code])

    print(table)


def walk_for_duplicates(start_node: Node, end_node: Node) -> None:
    """
    Walks the tree from the start node to the end node and checks if there are duplicates
    :param start_node: the node from where the walking process begins
    :param end_node: the node where the walking process ends
    :return: the list of nodes
    """
    w = Walker()

    res = w.walk(start_node, end_node)

    if PRINT_TABULAR_TREE_PATHS:
        print_tree_path(res[0])

    if contains_duplicates(list(res[0])):
        with open(DUPLICATE_NODES_FILE, "a") as f:
            # TODO add the path to the file
            f.write(f"There are duplicates on the current path")
        print(f"There are duplicates on the current path")


def render_tree_ex(node: Node, bom) -> None:
    rendered_tree = ""
    for line in RenderTree(node):
        rendered_tree += f"{line.pre} [{line.node.operationid}]  [{line.node.parentid}] [{line.node.code}]\n"
        print(
            f"{line.pre} [{line.node.operationid}]  [{line.node.parentid}] [{line.node.code}]")
    with open(f"boms/{bom.output_file}.tree", "w") as f:
        f.write(rendered_tree)


def create_children_ex(node: Node,
                       num_children: int,
                       depth: int,
                       products: List,
                       seed: int,
                       bom: Bom,
                       random_children: bool = False) -> None:
    """
    This function will create a generic tree using recursion. The process looks to work slow
    for large depths, should be replaced with a faster alternative, for now is usable

    :param node: the node to which the children are created and attached
    :param num_children: the number of children to be created for the specified node
    :param depth: the depth of the tree (the number of levels below the specified node)
    :param seed: the seed used to initialize the random generator.
    :param random_children: in the case one need to create a random number of children for the
            specified node. The number of children will vary between 1 and num_children

    :return:
    """

    # exit condition
    if depth == 0:
        # if we are at this point, we need to reset the list of products for this path
        SimpleTreePathProducts.reset()
        walk_for_duplicates(node, SimpleTreeRootNode.node)

        return

    number_of_children = random.randint(1, num_children) if random_children else num_children

    for i in range(number_of_children):

        is_eligible_product = False

        while not is_eligible_product:
            product = random.choice(products)

            # Check to see if the randomly chosen product is the root of the BOM. If yes, we need to do another pick
            # The idea is that the root product cannot be used as a child of the BOM elsewhere. The root is the
            # final product and that's it!
            if product.productid == RootProduct.product.productid and product.pname == RootProduct.product.pname:
                continue

            if product not in SimpleTreePathProducts.products:
                log.debug(f'{product.productid} is added to the path')
                is_eligible_product = True
                SimpleTreePathProducts.add_product(product)
            else:
                log.debug(f'{product.productid} is a duplicate product. Picking a new one...')
                print(f'{product.productid} is a duplicate product. Picking a new one...')
                continue

        operation_id = Sequencer().index

        new_node = f"Node('s{i}', parent=node, parentid={node.operationid}, operationid={operation_id}, productid={product.productid}, " \
                   f"code='{product.code}')"
        NodeCounter.counter += 1

        log.debug(f"Current number of nodes in the tree is {NodeCounter.counter}")
        create_children_ex(eval(new_node), number_of_children, depth - 1, products, seed, bom,
                           random_children=random_children)  # recurse!

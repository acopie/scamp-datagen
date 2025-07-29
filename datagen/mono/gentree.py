import logging

from typing import List, Tuple
from anytree import Node, RenderTree, PreOrderIter
from anytree.exporter import DotExporter, JsonExporter
from anytree.importer import JsonImporter
from anytree.walker import Walker
from prettytable import PrettyTable

from datagen.common.config import PRINT_TABULAR_TREE_PATHS
from datagen.common.rootprod import RootProduct, RootNode
from datagen.common.treeutil import NodeCounter
from datagen.common.stocks import Stocks

from datagen.mono.boms_processing import Bom
from datagen.mono.quantity import Quantity
from datagen.mono.metainfo import MetaInfo
from datagen.mono.productgenerator import *
from datagen.mono.pathprods import PathProducts

log = logging.getLogger("main")
DUPLICATE_NODES_FILE = "./out/duplicate_nodes.txt"


# define some functions that will be used by the DotExporter class
def nodenamefunc(node: Node):
    return f'"{node.name}:{node.depth}"'


def edgeattrfunc(node: Node, child: Node):
    return f'label="{node.name}:{child.name}"'


def edgetypefunc(node: Node, child: Node):
    return '--'


def contains_duplicates(l: List) -> bool:
    """
    Checks if a list contains duplicates
    :param l: the list to be checked
    :return: True if the list contains duplicates, False otherwise
    """
    return len(l) != len(set(l))


def export_tree(n: Node, file_path: str, onscreen: bool = True) -> None:
    """
    Exports a node in JSON format
    :param n: the node to be exported
    :param file_path: the path of the exported json file
    :param onscreen: if the exported json will be displayed on stdout too
    :return: None
    """
    exporter = JsonExporter(indent=2, sort_keys=False)
    print(n)
    if onscreen:
        print(exporter.export(n))

    with open(file_path, "w") as f:
        # exporter.write(root, f)

        f.write(exporter.export(n))


def import_tree(file_path: str) -> Node:
    """
    Deserialize a tree from its associated JSON file
    :param file_path: the path to the file containing the onject serialization
    :return: the Python tree object
    """
    with open(file_path) as f:
        tree_as_dict = json.load(f)

    tree_as_str = json.dumps(tree_as_dict)
    return JsonImporter().import_(tree_as_str)


def render_tree(node: Node) -> None:
    for line in RenderTree(node):
        print(
            f"{line.pre} [opid={line.node.operationid}] [{line.node.productid}]  [{line.node.parentid}] [{line.node.code}]  [{line.node.pname}] [{line.node.machines}]")


def simple_render_tree(node: Node, bom) -> None:
    rendered_tree = ""
    for line in RenderTree(node):
        rendered_tree += f"{line.pre} [{line.node.operationid}]  [{line.node.parentid}] [{line.node.code}]\n"
        print(
            f"{line.pre} [{line.node.operationid}]  [{line.node.parentid}] [{line.node.code}]")

    with open(get_abs_file_path(f"boms/{bom.output_file}.tree"), "w") as f:
        f.write(rendered_tree)


def export_dot(node, file_path) -> None:
    """
    Exports a node in .dot format to be
    :param node:
    :param file_path:
    :return:
    """
    DotExporter(node, graph="graph", nodenamefunc=nodenamefunc, nodeattrfunc=lambda n: "shape=box",
                edgeattrfunc=edgeattrfunc,
                edgetypefunc=edgetypefunc).to_dotfile(file_path)


def print_tree_path(nodes: Tuple[Node, ...], bom: Bom) -> None:
    """
    Prints the paths of the BOM in a table representation
    """
    table = PrettyTable()
    table.field_names = ["name", "depth", "productid", "parentid", "code", "pname"]

    for node in nodes:
        table.add_row([node.name, node.depth, node.productid, node.parentid, node.code, node.pname])

    with open(f"boms/{bom.output_file}.table", "a") as f:
        f.write(table.get_string())
    # print(table)


def walk_for_duplicates(start_node: Node, end_node: Node, bom: Bom) -> None:
    """
    Walks the tree from the start node to the end node and checks if there are duplicates
    :param start_node: the node from where the walking process begins
    :param end_node: the node where the walking process ends
    :param bom: the BOM object
    :return: None
    """
    w = Walker()

    res = w.walk(start_node, end_node)

    if PRINT_TABULAR_TREE_PATHS:
        print_tree_path(res[0], bom)

    if contains_duplicates(list(res[0])):
        with open(DUPLICATE_NODES_FILE, "a") as f:
            # TODO add the path to the file
            f.write(f"There are duplicates on the current path")
        print(f"There are duplicates on the current path")


def walk(node, callback) -> None:
    """
    Walks through the tree and apply a callback function
    :param node: the root (or upper) node in the tree from where the walking process begins
    :param callback: the function called for every walked node
    :return:
    """
    for crt_node in PreOrderIter(node):
        callback(crt_node)


def decorate_stocks_on_node(node: Node) -> None:
    node.raw_material_id=random.choice(Stocks().stocks).id
    node.raw_material_quantity=random.randint(1, 10)

def create_children(node: Node,
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
        decorate_stocks_on_node(node)
        return

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

            if (product not in PathProducts.products) and (product not in children_products) and (
                    product is not RootNode().node):
                log.debug(f'{product.productid} is added to the path')
                is_eligible_product = True
                PathProducts.add_product(product)
                children_products.append(product)
            else:
                log.debug(f'{product.productid} is a duplicate product. Picking a new one...')
                print(f'{product.productid} is a duplicate product. Picking a new one...')
                continue

        operation_id = Sequencer().index
        MetaInfo().add_metainfo(product, operation_id)

        new_node = (
                    f"Node('s{i}', "
                    f"parent=node, "
                    f"parentid={node.operationid}, "
                    f"operationid={operation_id}, "
                    f"productid={product.productid}, "
                    f"code='{product.code}', "
                    f"pname='{product.pname}', "
                    f"quantity={Quantity.get_quantity(bom.quantity.min, bom.quantity.step, bom.quantity.max)}, "
                    f"machines={str(product.machines)})"
        )

        NodeCounter.counter += 1
        log.debug(f"Current number of nodes in the tree is {NodeCounter.counter}")

        create_children(eval(new_node), number_of_children, depth - 1, products, seed, bom,
                        random_children=random_children)  # recurse!
        PathProducts.remove_product(product)

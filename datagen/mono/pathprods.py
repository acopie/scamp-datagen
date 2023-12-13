from anytree import Node

from datagen.mono.productgenerator import Product


class PathProducts:
    """
    This singleton holds the products on a tree path

    @author Adrian
    """

    instance = None
    products = list()

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
    def remove_product(cls, p: Product):
        """
        Remove a product belonging to a specific path in BOM tree
        """
        cls.products.remove(p)

    @classmethod
    def reset(cls):
        """Resets the existent product items in the products list"""
        cls.products.clear()

class PathNodes:
    """
    This singleton holds the nodes on a tree path

    @author Adrian
    """
    instance = None
    nodes = list()

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            return super().__new__(*args, **kwargs)

    @classmethod
    def add_node(cls, n: Node) -> None:
        """
        Adds a node belonging to a specific path in BOM tree
        """
        if n not in cls.nodes:
            cls.nodes.append(n)

    @classmethod
    def reset(cls):
        """Resets the existent product items in the products list"""
        cls.nodes.clear()



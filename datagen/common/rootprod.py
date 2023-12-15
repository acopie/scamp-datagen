"""
Module which holds the root product and the root node of the BOM tree. It is used to avoid the root product to be
duplicated

@author: Adrian
"""


from datagen.common.importer import SProduct
from anytree import Node


class RootProduct:
    """
    Class representing a singleton which holds the root product. It is used when the product entries are generated
    to be populated in the BOM tree, to avoid the root product to be used elsewhere that the root.

    @author Adrian
    """

    instance: type['RootProduct'] = None
    product: SProduct = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            return super().__new__(*args, **kwargs)

    @classmethod
    def add_root(cls, p: SProduct):
        """
        Adds a root product which will be used at every product generation
        """
        cls.product = p

    @classmethod
    def reset(cls):
        """
        Resets the existent root product to be used for another BOM
        """

        cls.product = None


class RootNode:
    """
    Class representing a singleton which holds the root node.

    @author Adrian
    """

    instance = None
    node = None

    def __new__(cls):
        if cls.instance is None:
            return super().__new__(cls)

    @classmethod
    def add_node(cls, n: Node):
        """
        Adds a root product which will be used at every product build
        """
        cls.node = n

    @classmethod
    def reset(cls):
        """
        Resets the existent root product to be used for another BOM
        """
        cls.node = None



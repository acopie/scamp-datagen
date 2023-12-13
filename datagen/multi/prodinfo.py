"""
This module is related to the information that is related to the products in the system.

@author: Adrian
"""

from datagen.multi.quantity import Quantity
from datagen.multi.vert_tree import VerticalTreeDepth


class ProductInfo:
    def __init__(self, name: str, max_depth: int, max_children: int, randomize_children: bool,
                 output_file: str, delivery_date: str,
                 quantity: Quantity, vertical_tree_depth: VerticalTreeDepth = None):
        # the name of the BOM. Must be unique across our system
        self.name: str = name
        self.max_depth: int = max_depth
        self.max_children: int = max_children
        self.randomize_children: bool = randomize_children
        self.output_file: str = output_file
        self.delivery_date: str = delivery_date
        self.quantity: Quantity = Quantity(quantity)
        self.vertical_tree_depth: VerticalTreeDepth = VerticalTreeDepth(vertical_tree_depth.get("min"),
                                                                        vertical_tree_depth.get("max"),
                                                                        vertical_tree_depth.get("step"),
                                                                        vertical_tree_depth.get("probability")) if vertical_tree_depth else None

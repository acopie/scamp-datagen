"""
This module holds the global settings for the multi-product BOM generator

@author: Adrian
"""


class Globals:
    def __init__(self, prod_number, start_date, root_directory):
        """
        @param prod_number: the number of products to be generated. for every BOM
            entry, will be generated prod_number products and they will be used further to
            populate the BOM tree
        @param start_date: the date from which the products will be generated. All the
            components of the BOM will be generated starting from this date.
        @param root_directory: the root directory where the generated data will be stored
        """
        self.products_number: int = prod_number
        self.start_date: str = start_date
        self.root_directory: str = root_directory

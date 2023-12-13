"""
This module holds the start date of the batch of products that will be generated. We need this info in order to compute
the machines maintenance intervals. The maintenance intervals are considered starting from the global starting date of
the whole batch to the farthest delivery date of all the products in the batch.

@author: Adrian
"""


class StartDate:

    # so far it is enough to consider teh start date as a string
    start_date: str = None

    @classmethod
    def add_start_date(cls, start_date) -> None:
        cls.start_date = start_date

    @classmethod
    def get_start_date(cls) -> str:
        return cls.start_date
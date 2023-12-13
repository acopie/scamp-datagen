"""
This module will hold the farthest delivery date considering all the products that will be realized in a batch.
We need this information in order to generate the maintenance intervals for the machines. The maintenance intervals
are considered starting from the global starting date of all the products batch and ending with the farthest delivery
date.

@author: Adrian
"""

from datetime import datetime


class EndDeliveryDate:
    # keep the date as a datetime object since we need to do some computations with it
    endDeliveryDate: datetime = None

    @classmethod
    def add_end_delivery_date(cls, end_delivery_date) -> None:
        cls.endDeliveryDate = end_delivery_date

    @classmethod
    def get_end_delivery_date(cls) -> datetime:
        return cls.endDeliveryDate

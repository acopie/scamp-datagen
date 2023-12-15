"""
Module containing the date and datetime classes used in the data generator

@author: Adrian
"""


from datetime import datetime as system_datetime, date as system_date

"""
Class that implements a global date format over the whole data generator 

@author Adrian
"""


def datemask():
    """
    global date format
    :return:
    """
    return "%Y-%m-%d %H:%M:%S.%f"


class date(system_date):
    """
    Our implementation of date, extending the default date
    """
    def __str__(self):
        """
        Our __str__() representation of date
        """
        return f"{self.day}/{self.month}/{self.year}";


class datetime(system_datetime):
    """
    Our implementation of datetime  class, extending the default datetime class
    """
    def __str__(self):
        """
        Our __str__() representation of datetime
        """
        return f"{self.day}/{self.month}/{self.year} {self.hour}:{self.minute}:{self.second}"

    def date(self):
        """
        Creates a date object based on the instance day, mont and year fields
        """
        return date(self.day, self.month, self.year)


if __name__ == "__main__":
    print(datetime.now())
    print(str(datetime))

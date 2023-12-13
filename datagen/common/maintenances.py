print(f"maintenances ---> {__name__}")

from json import JSONEncoder
import datagen.multi.maintenance


class Maintenances(object):
    """
    Holds the Maintenance objects generated during the product creation phase
    """

    maintenances_list = set()

    @classmethod
    def add(cls, maintenance: datagen.multi.maintenance.Maintenance) -> None:
        """
        add a Maintenance object to the list of maintenances
        :param maintenance:
        :return:
        """
        cls.maintenances_list.add(maintenance)

    @classmethod
    def reset(cls) -> None:
        """
        empties the list of maintenances
        :return: None
        """
        cls.maintenances_list.clear()

    @classmethod
    def get_maintenances(cls) -> list:
        return list(set(cls.maintenances_list))

    @classmethod
    def to_json(cls):
        maintenance_list = list(cls.maintenances_list)
        maintenance_list.sort(key=lambda M: (M.machineid, M.start_date))
        return [maintenance.to_json() for maintenance in maintenance_list]


class MaintenancesEncoder(JSONEncoder):

    @classmethod
    def encode(cls, o):
        return o.__dict__

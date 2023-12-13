"""
This module is related to the machines information in the system

@author: Adrian
"""


class UnitAssemblyTime:
    def __init__(self, min: int, max: int, step: int, time_units: str):
        self.min = min
        self.max = max
        self.step = step
        self.time_units = time_units


class MaintenanceDuration:
    def __init__(self, min_duration: int, max_duration: int, step: int, time_units: str):
        self.min_duration  = min_duration
        self.max_duration = max_duration
        self.step = step
        self.time_units = time_units


class MaintenanceInterval:
    def __init__(self, duration: int, time_units: str):
        self.duration = duration
        self.time_units = time_units


class OEE:
    def __init__(self, min: int, max: int, distribution: str):
        self.min = min
        self.max = max
        self.distribution = distribution


class SetupTime:
    def __init__(self, min: int, max: int, step: int, time_units: str):
        self.min = min
        self.max = max
        self.step = step
        self.time_units = time_units


class MachineInfo:
    def __init__(self,
                 start_date: str,
                 prod_number: int,
                 root_directory: str,
                 machines_number: int,
                 max_alternatives_machines_number: int,
                 randomize_alternative_machines: bool,
                 allow_identical_machines: bool,
                 percent_of_identical_machines: float,
                 unit_assembly_time: UnitAssemblyTime,
                 maintenance_duration: MaintenanceDuration,
                 maintenance_interval: MaintenanceInterval,
                 maintenance_probability: float,
                 oee: OEE,
                 setup_time: SetupTime):

        self.start_date: str = start_date
        self.prod_number: int = prod_number
        self.root_directory: str = root_directory
        self.machines_number: int = machines_number
        self.max_alternatives_machines_number: int = max_alternatives_machines_number
        self.randomize_alternative_machines: bool = randomize_alternative_machines
        self.allow_identical_machines: bool = allow_identical_machines
        self.percent_of_identical_machines: float = percent_of_identical_machines
        self.unit_assembly_time: UnitAssemblyTime = unit_assembly_time
        self.maintenance_duration: MaintenanceDuration = maintenance_duration
        self.maintenance_interval: MaintenanceInterval = maintenance_interval
        self.maintenance_probability: float = maintenance_probability
        self.oee = oee
        self.setup_time: SetupTime = setup_time
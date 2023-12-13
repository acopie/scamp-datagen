import datetime as dt
import math
import random

from typing import Tuple, Any, List

import datagen.common.sequencer
import datagen.common.scampdate

from datagen.mono.bomcache import BomCache


class NoStartTimeException(Exception):
    def __init__(self):
        self.message = "Start date is not defined. Execute first the start_time() method to properly set the start " \
                       "date. "


class MaintenanceDuration(object):
    def __init__(self, dct):
        self.min_duration = dct["min_duration"]
        self.max_duration = dct["max_duration"]
        self.step = dct["step"]
        self.time_units = dct["time_units"]


class MaintenanceInterval:

    def __init__(self, dct):
        self.duration = dct.get("duration", 0)
        self.time_units = dct.get("time_units", "")


class Maintenance(object):
    """
    This class models a maintenance action for a specific machine. There could be one or many maintenance intervals
    during the product lifecycle, so this class allows the existence of these interludes
    """

    def __init__(self, machine, start_date, end_date):

        # the unique id per maintenance entry
        self.id = datagen.common.sequencer.Sequencer().index

        # the id of the machine for which we attach a maintenance
        self.machineid = machine.id

        # # the possible maintenance interval
        # self.maintenance_interval = maintenance_interval

        # # list of maintenances for a machine
        # self.machine_maintenances = self.build_maintenance_dates()

        # maintenance start date
        self.start_date = start_date

        # maintenance end date
        self.end_date = end_date

    def __eq__(self, other: Any) -> bool:
        if isinstance(self, other.__class__):
            return self.start_date == other.start_date and \
                self.end_date == other.end_date and \
                self.machineid == other.machineid
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash((self.machineid,))

    @staticmethod
    def to_hours(val: int, time_units: str) -> int:

        conversions = {
            'seconds': 1 // 3600,
            'minutes': 1 / 60,
            'hours': 1,
            'days': 24,
            'weeks': 24 * 7,
        }

        try:
            unit_to_be_converted = conversions.get(time_units.lower(), "hours")
        except KeyError:
            raise ValueError(f"Invalid time units {time_units}")

        return val * unit_to_be_converted

    @staticmethod
    def to_seconds(val: int, time_units: str) -> int:

        conversions = {
            'seconds': 1,
            'minutes': 1 * 60,
            'hours': 1 * 60 * 60,
            'days': 24 * 60 * 60,
            'weeks': 24 * 7 * 60 * 60,
        }

        try:
            unit_to_be_converted = conversions.get(time_units.lower(), "seconds")
        except KeyError:
            raise ValueError(f"Invalid time units {time_units}")

        return val * unit_to_be_converted

    # @staticmethod
    # def to_seconds(hours: int) -> int:
    #     return hours * 3600

    @classmethod
    def get_maintenance_intervals(cls) -> List:
        """
        Computes the maintenance intervals possible inside the product's lifecycle
        """
        bom = BomCache.get_bom()
        prod_start_date = bom.start_date
        prod_end_date = bom.delivery_date

        maintenance_interval_value = bom.maintenance_interval.duration
        maintenance_interval_time_units = bom.maintenance_interval.time_units

        maintenance_interval_hours = cls.to_hours(maintenance_interval_value, maintenance_interval_time_units)
        maintenance_interval_seconds = cls.to_seconds(maintenance_interval_hours, "hours")

        # how long it takes to make a product
        duration = dt.datetime.strptime(prod_end_date, datagen.common.scampdate.datemask()) - dt.datetime.strptime(
            prod_start_date, datagen.common.scampdate.datemask())
        duration_in_sec = duration.total_seconds()

        maintenance_occurrencies = int(duration_in_sec / maintenance_interval_seconds)
        maintenance_intervals = []

        for i in range(maintenance_occurrencies):
            interval = list()
            start_interval = dt.datetime.strptime(prod_start_date, datagen.common.scampdate.datemask()) + \
                             dt.timedelta(hours=(i * maintenance_interval_hours))
            end_interval = dt.datetime.strptime(prod_start_date, datagen.common.scampdate.datemask()) + \
                           dt.timedelta(hours=((i + 1) * maintenance_interval_hours))
            if end_interval <= dt.datetime.strptime(bom.delivery_date, datagen.common.scampdate.datemask()):
                interval.append(start_interval)
                interval.append(end_interval)
                maintenance_intervals.append(interval)

        return maintenance_intervals

    def build_maintenance_dates(self) -> Tuple[str, str]:

        bom = BomCache.get_bom()
        step = bom.maintenance_duration.step
        min_duration = bom.maintenance_duration.min_duration
        max_duration = bom.maintenance_duration.max_duration
        time_units = bom.maintenance_duration.time_units

        maintenance_interval_value = bom.maintenance_interval.duration
        maintenance_interval_time_units = bom.maintenance_interval.time_units

        maintenance_interval_hours = self.to_hours(maintenance_interval_value, maintenance_interval_time_units)

        # determine the value of the step param, expressed in hours
        step_in_hours = self.to_hours(step, time_units)

        # number of steps in the interval [start_interval, end_interval]
        steps_number = int(maintenance_interval_hours // step_in_hours)

        # delta between max_duration and min_duration
        maintenance_delta = self.to_hours(max_duration, time_units) - self.to_hours(min_duration, time_units)

        # number of possible steps inside the maintenance period
        steps_in_maintenance = math.floor(int(maintenance_delta / step_in_hours))

        # flag to check if the generated pair of dates satisfies the limit conditions
        right_pair_values = False

        # to create the maintenance dates, we take a random number from the interval [1, steps_number]
        # and we use it as time delta to define the maintenance_start_date. Then, we add the defined step to
        # define the maintenance_end_date. We check then against the limits of the product dates

        maintenance_dates = []

        for k in range(len(self.maintenance_interval)):
            while not right_pair_values:

                # create a list containing possible value for the maintenance, containing the min and the max duration.
                # the values are expressed in hours
                possible_maintenances = {self.to_hours(min_duration, time_units),
                                         self.to_hours(max_duration, time_units)}

                random_start = random.randint(1, steps_number)
                maintenance_start_date = self.maintenance_interval[k][0] + dt.timedelta(hours=random_start)
                random_duration = self.to_hours(min_duration, time_units) + random.randint(1,
                                                                                           steps_in_maintenance) * step_in_hours
                possible_maintenances.add(random_duration)

                # extract a random value of duration from the possible ones
                random_interval = random.choice(list(possible_maintenances))
                maintenance_end_date = maintenance_start_date + dt.timedelta(hours=random_interval)

                maintenance_interval_end_date = self.maintenance_interval[k][1]

                if maintenance_start_date < maintenance_interval_end_date \
                        and maintenance_end_date < maintenance_interval_end_date \
                        and maintenance_start_date < maintenance_end_date:
                    maintenance_dates_tmp = (maintenance_start_date.strftime(datagen.common.scampdate.datemask()),
                                             maintenance_end_date.strftime(datagen.common.scampdate.datemask()))
                    maintenance_dates.append(maintenance_dates_tmp)
                    right_pair_values = False
                    break

        # avoid the maintenance_interval field to be serialized, se we delete it
        del self.maintenance_interval

        return maintenance_dates

    @classmethod
    def build_maintenance_dates_ex(cls, start_maintenance_interval, end_maintenance_interval) -> Tuple[str, str]:
        """
        Computes the maintenance dates inside a maintenance interval. For example, a maintenance interval is defined
        by a start date and an end date, and the result of the computation is an inner interval, smaller.
        """

        bom = BomCache.get_bom()
        step = bom.maintenance_duration.step
        min_duration = bom.maintenance_duration.min_duration
        max_duration = bom.maintenance_duration.max_duration
        time_units = bom.maintenance_duration.time_units

        maintenance_interval_value = bom.maintenance_interval.duration
        maintenance_interval_time_units = bom.maintenance_interval.time_units

        maintenance_interval_hours = cls.to_hours(maintenance_interval_value, maintenance_interval_time_units)

        # determine the value of the step param, expressed in hours
        step_in_hours = cls.to_hours(step, time_units)

        # number of steps in the interval [start_interval, end_interval]
        steps_number = int(maintenance_interval_hours // step_in_hours)

        # delta between max_duration and min_duration
        maintenance_delta = cls.to_hours(max_duration, time_units) - cls.to_hours(min_duration, time_units)

        # number of possible steps inside the maintenance period
        steps_in_maintenance = math.floor(int(maintenance_delta / step_in_hours))

        # flag to check if the generated pair of dates satisfies the limit conditions
        right_pair_values = False

        # to create the maintenance dates, we take a random number from the interval [1, steps_number]
        # and we use it as time delta to define the maintenance_start_date. Then, we add the defined step to
        # define the maintenance_end_date. We check then against the limits of the product dates

        maintenance_dates = []

        while not right_pair_values:

            # create a list containing possible value for the maintenance, containing the min and the max duration.
            # the values are expressed in hours
            possible_maintenances = {cls.to_hours(min_duration, time_units),
                                     cls.to_hours(max_duration, time_units)}

            random_start = random.randint(1, steps_number)
            maintenance_start_date = start_maintenance_interval + dt.timedelta(hours=random_start)
            random_duration = cls.to_hours(min_duration, time_units) + random.randint(1,
                                                                                      steps_in_maintenance) * step_in_hours
            possible_maintenances.add(random_duration)

            # extract a random value of duration from the possible ones
            random_interval = random.choice(list(possible_maintenances))
            maintenance_end_date = maintenance_start_date + dt.timedelta(hours=random_interval)

            maintenance_interval_end_date = end_maintenance_interval

            if maintenance_start_date < maintenance_interval_end_date \
                    and maintenance_end_date < maintenance_interval_end_date \
                    and maintenance_start_date < maintenance_end_date:
                maintenance_dates_tmp = (maintenance_start_date.strftime(datagen.common.scampdate.datemask()),
                                         maintenance_end_date.strftime(datagen.common.scampdate.datemask()))
                maintenance_dates.append(maintenance_dates_tmp)
                right_pair_values = False
                break

        return maintenance_dates_tmp

    def to_json(self):
        return self.__dict__

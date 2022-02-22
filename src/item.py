"""Take in all info about one item and process"""

from datapoint import IdfOutputPoint, IdfInfoPoint, DevSettingPoint
from epreader import CSVReader, IDFReader
import pandas as pd
from typing import Dict
import datetime


class Item:
    """Containing the item data structure and methods to read data from external files"""

    def __init__(self, item):
        """

        Args:
            item: item dict from the json file
        """
        self.item = item
        self.points = {}
        self.pointnamelist = []
        self.buildpoints = []
        self.idf_variables_dict = {}
        self.timeserieslength = None
        self.df = pd.DataFrame()
        self.DF_YEAR = 2000
        self.setdatapoints()

    def ep_datetime(self, month, day, ep_datetime_type: str):
        if ep_datetime_type == "start":
            return datetime.datetime(
                self.DF_YEAR, month, day, 0, 0
            ) + datetime.timedelta(minutes=1)
        if ep_datetime_type == "end":
            return datetime.datetime(
                self.DF_YEAR, month, day, 23, 59
            ) + datetime.timedelta(minutes=1)

    def dfdaterange(self, start: tuple, end: tuple):
        starttime = self.ep_datetime(start[0], start[1], "start")
        endtime = self.ep_datetime(end[0], end[1], "end")
        return starttime, endtime

    def set_dates_from_simulation_period(self):
        period_list = self.item["simulation_period"]
        if isinstance(period_list, str):
            period_list = [period_list]

        # set the idf obj spec and df checking dates (self.df_datetimes)
        run_full_year = False
        for each in period_list:
            if each.lower().strip() in "annual":
                run_full_year = True
                self.df_datetimes.append(
                    (
                        datetime.datetime(self.DF_YEAR, 1, 1),
                        datetime.datetime(self.DF_YEAR, 12, 31, 23, 59),
                    )
                )
                self.idf_simcontrol["run_annual"] = True
                self.idf_runperiod = {
                    "begin_month": 1,
                    "begin_day": 1,
                    "end_month": 12,
                    "end_day": 31,
                }

            if each.lower().strip() in "design day":
                self.df_datetimes.append(self.dfdaterange((1, 1), (12, 31)))
                self.idf_simcontrol["run_sizing"] = True
            if each.lower().strip() in "summer design day":
                self.df_datetimes.append(self.dfdaterange((7, 21), (7, 21)))
                self.idf_simcontrol["run_sizing"] = True
            if each.lower().strip() in "winter design day":
                self.df_datetimes.append(self.dfdaterange((12, 21), (12, 21)))
                self.idf_simcontrol["run_sizing"] = True
            if each.lower().strip() in "specific periods":
                if run_full_year:
                    print(
                        "WARNING: setting annual and specific periods simulaton at the same time"
                    )
                run_period_dict = self.item["run_period"]
                self.df_datetimes.append(
                    self.dfdaterange(
                        (run_period_dict["begin_month"], run_period_dict["begin_day"]),
                        (run_period_dict["end_month"], run_period_dict["begin_day"]),
                    )
                )
                self.idf_simcontrol["run_annual"] = True
                self.idf_runperiod = {
                    "begin_month": run_period_dict["begin_month"],
                    "begin_day": run_period_dict["begin_day"],
                    "end_month": run_period_dict["end_month"],
                    "end_day": run_period_dict["end_day"],
                }

    def setdatapoints(self):
        """set different types of data points for use by other modules"""
        self.points = self.item["datapoints_source"]
        for pointtype, points in self.points.items():
            print("=======")
            print(pointtype)
            print(points)

            for pointname, pointinfo in points.items():
                self.pointnamelist.append(pointname)
                if pointtype == "idf_objects":
                    self.buildpoints.append(IdfInfoPoint(pointname, pointinfo))
                if pointtype == "idf_output_variables":
                    new_point = IdfOutputPoint(pointname, pointinfo)
                    self.buildpoints.append(new_point)
                    self.idf_variables_dict[new_point.variable_name] = pointname
                if pointtype == "dev_settings":
                    self.buildpoints.append(DevSettingPoint(pointname, pointinfo))

        # Drop None values in pointname and buildpoints caused by no points for certain point types.
        self.pointnamelist = [i for i in self.pointnamelist if i]
        self.buildpoints = [i for i in self.buildpoints if i]

    def read_output_variables(self, csv_path):
        """helper: read idf output variable csv


        read energyplus simulation output variables from the csv file and save them in pandas dataframe (self.df)
            and point objects value field

        Args:
            csv_path: path to the energyplus simulation output variables csv file

        """

        if csv_path is None:
            return None

        csv = CSVReader(csv_path)
        self.df = csv.getseries(list(self.idf_variables_dict.keys()))
        self.df = self.df.rename(columns=self.idf_variables_dict)
        self.timeserieslength = self.df.shape[0]
        for point in self.buildpoints:
            if isinstance(point, IdfOutputPoint):
                point.value = self.df[point.name]

    def read_idf_obj_values(self, idf_path, idd_path):
        """helper: read idf input object fields

        read energyplus input idf object field, then populate into self.df as timeseries values

        Args:
            idf_path: path to the simulation input idf file
            idd_path: path to the idd file

        """
        if idf_path is None:
            return None

        idf = IDFReader(idf_file=idf_path, idd_file=idd_path)
        for point in self.buildpoints:
            if isinstance(point, IdfInfoPoint):
                non_objtype_filters = {}
                for k, v in point.filters.items():
                    if k != "idf_object_type":
                        non_objtype_filters[k] = v
                point.value = idf.getidffieldval(
                    objtype=point.filters["idf_object_type"],
                    filters_dict=non_objtype_filters,
                    excluters_dict=point.exclusions,
                    fieldname=point.field,
                )
                self.df[point.name] = point.value

    def read_points_values(self, csv_path=None, idf_path=None, idd_path=None):
        """method for user to read all types of simulation i/o data

        Args:
            csv_path: path to the output csv file containing output variable simulation data
            idf_path: path to the simulation input idf file
            idd_path: path to the idd file

        Returns:
            pandas dataframe containing all data queried

        """
        self.read_output_variables(csv_path)
        self.read_idf_obj_values(idf_path, idd_path)

        return self.df


class TimeSeriesFilterElement:
    def __init__(self, filter_str: str):
        """

        Args:
            filter_str:
                e.g. 1  setter: $light_power_check_max = recipes.threshed_max($Electric_light_power,
                    $light_power_range_upperbound)
                e.g. 2 filter: $Daylight_schedule > 0.99
        """
        self.filter_str = filter_str
        if "setter:" in filter_str:
            self.type = "setter"
            self.content = filter_str.split("setter:")[1].strip()
        elif "filter:" in filter_str:
            self.type = "filter"
            self.content = filter_str.split("filter:")[1].strip()
        else:
            print("ERROR! Invalid apply type")

    def __repr__(self):
        """for debugging use"""
        return str(self.__dict__)


class TimeSeriesFilters:
    def __init__(self, filters_dict: Dict):
        self.apply = filters_dict["apply"]
        self.sequence = []
        for each in filters_dict["filters_setters_sequence"]:
            self.sequence.append(TimeSeriesFilterElement(each))

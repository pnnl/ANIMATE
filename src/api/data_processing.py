import sys, os, logging, datetime
import pandas as pd

sys.path.append("..")
from epreader import *
from datetimeep import *


class DataProcessing:
    def __init__(
        self,
        data_path: str = None,
        data_source: str = None,
        timestamp_column_name: str = None,
    ):
        """Instantiate a data processing object to load datasets and manipulate data before feeding it to the verification process.

        Args:
            data (str): Path to the data (CSV format) to be loaded for processing.
            data_source (str): Data source name. Use `EnergyPlus` or `Other`.
            timestamp_column_name (str): Name of the column header that contains the time series timestamps.
        """
        if data_path == None:
            logging.error("A `data_path` argument should be provided.")
            if data_source == None:
                logging.error("A `data_source` argument should be provided.")
            return None

        # check if data file exists
        if os.path.isfile(data_path):
            try:
                if data_source != "EnergyPlus":
                    self.data = pd.read_csv(data_path)
                    if not timestamp_column_name in self.data.columns:
                        logging.error(
                            f"The data does not contain a column header named {data_path}."
                        )
                        return None
                    else:
                        self.data.set_index(timestamp_column_name, inplace=True)
                    try:
                        self.data = pd.to_datetime(self.data.index)
                    except:
                        logging.error(
                            f"The data in {timestamp_column_name} could not be converted to Python datetime object. Make sure that the data is consistent defined as a set of date strings."
                        )
                        return None
                else:
                    # Use CSVReader to parse EnergyPlus timestamps
                    data = CSVReader(csv_file=data_path).getseries()
                    data = DateTimeEP(data, 2000).transform()
                    data.drop("Date/Time", inplace=True, axis=1)
                    self.data = data
            except:
                logging.error(
                    f"An error occured when opening {data_path}. Please make sure that the file can be opened, and/or that it contains the correct headers."
                )
                return None
        else:
            logging.error(f"The file {data_path} does not exists.")
            return None

    def slice(self, start_time: datetime, end_time: datetime, inplace=False):
        """Discard any data before `start_time` and after `end_time`.

        Args:
            start_time (datetime): Python datetime object used as the slice start date of the data
            end_time (datetime): Python datetime object used as the slice end date of the data
            inplace (bool, optional): Modify the object directly. Defaults to False.
        """
        if isinstance(start_time, datetime.datetime):
            if isinstance(end_time, datetime.datetime):
                if start_time > end_time:
                    logging.error(
                        f"The end_time cannot be an earlier data than start_time."
                    )
                else:
                    if inplace:
                        self.data = self.data[start_time:end_time]
                    else:
                        return self.data[start_time:end_time]
            else:
                logging.error(f"The end_time argument is not a Python datetime object.")
        else:
            logging.error(f"The start_time argument is not a Python datetime object.")
        return None

    def add_parameter(self, name: str = None, value: float = None, inplace=False):
        """Add a parameter to `data`. The parameter will be added as a constant value for all index of `data`

        Args:
            name (str): Name of the parameter
            value (float): Value of the parameter.
            inplace (bool): Modify the object directly. Defaults to False.
        """
        if name is None:
            logging.error(f"A parameter name should be specified.")
            return None

        if value is None:
            logging.error(f"A parameter value should be specified.")
            return None

        if inplace:
            self.data[name] = value
        else:
            d = self.data
            d[name] = value
            return d

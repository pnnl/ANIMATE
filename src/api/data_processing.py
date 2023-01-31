import sys, os, logging, datetime, copy
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

sys.path.append("..")
from epreader import *
from datetimeep import *
from typing import Union


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
            return None

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

    def slice(
        self, start_time: datetime, end_time: datetime, inplace: bool = False
    ) -> Union[None, pd.DataFrame]:
        """Discard any data before `start_time` and after `end_time`.

        Args:
            start_time (datetime): Python datetime object used as the slice start date of the data.
            end_time (datetime): Python datetime object used as the slice end date of the data.
            inplace (bool, optional): Modify the dataset directly. Defaults to False.

        Returns:
            pd.DataFrame: Modified dataset
        """
        if isinstance(start_time, datetime.datetime):
            if isinstance(end_time, datetime.datetime):
                if start_time > end_time:
                    logging.error(
                        "The end_time cannot be an earlier data than start_time."
                    )
                else:
                    if inplace:
                        self.data = self.data[start_time:end_time]
                    else:
                        return self.data[start_time:end_time]
            else:
                logging.error("The end_time argument is not a Python datetime object.")
        else:
            logging.error("The start_time argument is not a Python datetime object.")
        return None

    def add_parameter(
        self, name: str = None, value: float = None, inplace: bool = False
    ) -> Union[None, pd.DataFrame]:
        """Add a parameter to `data`. The parameter will be added as a constant value for all index of `data`.

        Args:
            name (str): Name of the parameter
            value (float): Value of the parameter.
            inplace (bool): Modify the dataset directly. Defaults to False.

        Returns:
            pd.DataFrame: Modified dataset
        """
        if name is None:
            logging.error("A parameter name should be specified.")
            return None

        if value is None:
            logging.error("A parameter value should be specified.")
            return None

        if inplace:
            self.data[name] = value
        else:
            d = self.data
            d[name] = value
            return d

    def apply_function(
        self,
        variable_names: list = None,
        new_variable_name: str = None,
        function_to_apply: str = None,
        inplace: bool = False,
    ) -> Union[None, pd.DataFrame]:
        """Apply an aggregation function to a list of variables from the dataset.

        Args:
            variable_names (str): List of variables used as input to the function.
            new_variable_name (str): Name of the new variable containing the result of the function for each time stamp.
            function_to_apply (str): Name of the function to apply. Choices are: `sum`, `min`, `max`or `average`.
            inplace (bool): Modify the dataset directly. Defaults to False.

        Returns:
            pd.DataFrame: Modified dataset
        """
        if variable_names is None:
            logging.error("A list of variables was not specified.")
            return None
        if isinstance(variable_names, list):
            if len(variable_names) == 0:
                logging.error("The variable name list is empty.")
                return None
            else:
                for v in variable_names:
                    missing_variables = 0
                    if not v in list(self.data.columns):
                        logging.warning(f"The variable {v} is not in the dataset.")
                        missing_variables += 1
                    if missing_variables == len(variable_names):
                        logging.error(
                            "None of the variables passed in the variable name list argument are actually in the dataset."
                        )
                        return None
        else:
            logging.error(
                f"A list of variable names should be passed as an argument not a {type(variable_names)}."
            )
            return None

        if new_variable_name is None:
            logging.error("A new variable name should be provided.")
            return None

        if not function_to_apply.lower() in ["sum", "min", "max", "average"]:
            logging.error(
                f"The function to apply should be `sum`, `min`, `max`, or `average, not {function_to_apply.lower()}."
            )
            return None

        agg = self.data.loc[:, variable_names].apply(
            lambda r: eval(
                f"{function_to_apply.lower().replace('average', 'sum(r)/len')}(r)"
            ),
            axis=1,
        )
        if inplace:
            self.data[new_variable_name] = agg
        else:
            d = self.data
            d[new_variable_name] = agg
            return d

    def summary(self) -> dict:
        """Provide a summary of the dataset.

        Returns:
            Dict: Dictionary containing the following information: 1) Number of data points, 2) Resolution, 3) For each variables: minimum, maximum, mean, standard deviation.
        """
        data_summary = {}
        data_summary["number_of_data_points"] = len(self.data)

        # Calculate average timestampe difference, i.e. average resolution
        # Report in seconds
        d = self.data
        d["date"] = self.data.index
        data_summary["average_resolution_in_second"] = (
            d["date"].diff().fillna(pd.Timedelta(seconds=0))[1:].mean().seconds
        )
        d.drop("date", inplace=True, axis=1)

        data_summary["variables_summary"] = {}
        for v in list(d.columns):
            data_summary["variables_summary"][v] = {}
            data_summary["variables_summary"][v]["minimum"] = d[v].min()
            data_summary["variables_summary"][v]["maximum"] = d[v].max()
            data_summary["variables_summary"][v]["mean"] = d[v].mean()
            data_summary["variables_summary"][v]["standard_deviation"] = np.std(d[v])

        return data_summary

    def concatenate(
        self, datasets: list = None, axis: int = None, inplace: bool = False
    ) -> Union[None, pd.DataFrame]:
        """Concatenate datasets.

        Args:
            datasets (list): List of datasets (pd.DataFrame) to concatenate with `data`.
            axis (int): 1 or 0. 1 performs a vertical concatenation and 0 performs an horizontal concatenation.
            inplace (bool, optional): Modify the dataset directly. Defaults to False.

        Returns:
            pd.DataFrame: Modified dataset
        """
        if not isinstance(datasets, list):
            logging.error(
                f"A list of datasets must be provided. The datasets argument that was passed is {type(datasets)}."
            )
            return None

        if len(datasets) == 0:
            logging.error("The list of dataset that was provided is empty.")
            return None

        if not axis in [0, 1]:
            logging.error("The axis argument should either be 1, or 0.")
            return None

        datasets.append(self.data)

        if axis == 1:
            # argument validation
            datasets_columns = [sorted(list(d.columns)) for d in datasets]
            if not all(c == datasets_columns[0] for c in datasets_columns):
                logging.error("The datasets must contain the same column headers.")
                return None

            # perform concatenation
            concatenated_datasets = datasets[0]
            for ds in datasets[1:]:
                concatenated_datasets = concatenated_datasets.append(ds)

        else:  # axis == 0
            # argument validation
            datasets_indexes = [d.index for d in datasets]
            if not all(len(i) == len(datasets_indexes[0]) for i in datasets_indexes):
                logging.error("The datasets must have the same indexes.")
                return None
            if not all(all(i == datasets_indexes[0]) for i in datasets_indexes):
                logging.error("The datasets must have the same indexes.")
                return None

            # perform concatenation
            concatenated_datasets = datasets[0]
            for ds in datasets[1:]:
                concatenated_datasets = pd.concat(
                    [concatenated_datasets, ds], ignore_index=False, axis=1
                )

        if inplace:
            self.data = concatenated_datasets
        else:
            return concatenated_datasets

    def check(self) -> dict:
        """Perform a sanity check on the data.

        Returns:
            Dict: Dictionary showing the number of missing values for each variables as well as the outliers.
        """
        data_headers = list(self.data.columns)
        if len(data_headers) == 0:
            logging.eror("The data does not include any hearders.")
            return None

        check_summary = {}
        for c in data_headers:
            check_summary[c] = {}
            # Look for missing data
            missing_values_count = self.data[c].isnull().sum()
            check_summary[c]["number_of_missing_values"] = missing_values_count

            # Look for outliers
            # 3x the standard deviation
            data = self.data[c].dropna()
            outliers = data[
                ~data.apply(lambda v: np.abs(v - data.mean()) / data.std() < 3)
            ]

            if len(outliers) == 0:
                outliers = None
            check_summary[c]["outliers"] = outliers

        return check_summary

    def fill_missing_values(
        self, method: str = None, variable_names: list = None, inplace: bool = False
    ) -> Union[None, pd.DataFrame]:
        """Fill missing values (NaN) in `data`.

        Args:
            method (str): Method to use to fill the missing values: 'linear' (treat values as equally spaced) or 'pad' (use existing values).
            variable_names (list): List of variable names that need missing values to be filled.
            inplace (bool): Modify the dataset directly. Defaults to False.

        Returns:
            pd.DataFrame: Modified dataset
        """

        if not method in ["linear", "pad"]:
            logging.error(
                f"The method should either be linear or bad but not {method}."
            )
            return None

        if not isinstance(variable_names, list):
            logging.error(
                f"A list of variable names must be provided. The variables_name argument that was passed is {type(variable_names)}."
            )
            return None

        if len(variable_names) == 0:
            logging.error("The list of variable names that was provided is empty.")
            return None

        d = copy.deepcopy(self.data)
        for v in variable_names:
            if not v in list(self.data.columns):
                logging.error(f"{v} is not included in the data.")
            else:
                if inplace:
                    self.data[v].interpolate(method=method, inplace=True)
                else:
                    d[v].interpolate(method=method, inplace=True)

        if not inplace:
            return d

    def plot(
        self, variable_names: list = None, kind: str = None
    ) -> matplotlib.axes.Axes:
        if not isinstance(variable_names, list):
            logging.error(
                f"A list of variable names must be provided. The variables_name argument that was passed is {type(variable_names)}."
            )
            return None

        if len(variable_names) == 0:
            logging.error("The list of variable names that was provided is empty.")
            return None

        not_found_count = 0
        for v in variable_names:
            if not v in list(self.data.columns):
                logging.warning(f"{v} is not included in the data.")
                not_found_count += 1
        if not_found_count == len(variable_names):
            logging.error(
                "None of the specified variables were found in data, the plot cannot be generated."
            )
            return None
        elif not_found_count < 2 and kind == "scatter":
            logging.error("A scatter plot requires at least two variables.")
            return None

        if not kind in ["timeseries", "scatter"]:
            logging.error(
                f"The kind of plot should be either timeseries or scatter but not {kind}."
            )
            return None

        # Create groups
        if kind == "timeseries":
            groups = [v for v in variable_names[0:]]
        elif kind == "scatter":
            groups = [(variable_names[0], v) for v in variable_names[1:]]
        else:
            return None

        fig, ax = plt.subplots()
        for g in groups:
            if kind == "timeseries":
                ax.plot(
                    self.data.index,
                    self.data[g],
                    label=g,
                    marker="o",
                    linestyle="",
                    alpha=1 / len(groups),
                )
            elif kind == "scatter":
                ax.plot(
                    self.data[g[0]],
                    self.data[g[1]],
                    label=g[1],
                    marker="o",
                    linestyle="",
                    alpha=1 / len(groups),
                )
        ax.legend()
        plt.show()
        return ax

# ANIMATE APIs design

Authors: Xuechen Lei, Jeremy Lerond, Yun Joon Jung

Date Modified: 01/21/2023

---

## Intro

The ANIMATE application programming iterfaces (APIs) are a collection of functions for performing common tasks with ANIMATE. These APIs are Python methods implementations with stable and well-documented interface. These methods are organized into different API categories (as Python classes) based on their functionalities and subjects.

## Verification Library API

Use this API to manage the verification items library

`class VerificationLibrary`

---

- [x] `__init__(`_lib_path: str_`)`
  Instantiate a verification library class object and load specified library items as `self.lib_items`.

  - **Parameters**
    - **lib_path**: path to the verification library file or folder. If the path ends with `*.json`, then library items defined in the json file are loaded. If the path points to a directory, then library items in all jsons in this directory and its subdirectories are loaded. Library item need to have unique name defined in the json files and python files.

---

- [x] `get_library_item(`_item_`)`
  Get the json definition and meta information of a specific library item.

  - **Parameters**
    - **items**: str. Verification item name to get.
  - **Returns** `Dict` with four specific keys:
    - `library_item_name`: unique str name of the library item
    - `library_json`: library item json definition in the library json file.
    - `library_json_path`: path of the library json file that contains this library item.
    - `library_python_path`: path of the python file that contains the python implementation of this library item.

---

- `get_library_items(`_items=[]_`)`
  Get the json definition and meta information of a list of specific library items.

  - **Parameters**
    - **items**: list of str, default []. Library items to get. By default, get all library items loaded at instantiation.
  - **Returns** list of `Dict` with four specific keys:
    - `library_item_name`: unique str name of the library item
    - `library_json`: library item json definition in the library json file.
    - `library_json_path`: path of the library json file that contains this library item.
    - `library_python_path`: path of the python file that contains the python implementation of this library item.

---

- `summarize_library(`_items=[]_`)`
  Summarize information of a list of library items.

  - **Parameters**
    - **items**: list of str, default []. Library items to summarize. By default, summarize all library items loaded at instantiation.
  - **Returns**: `Dict` that contains summary information of library items.

---

<!-- - `generate_library_item_update_template()`
Generate a dictionary with predefined keys so that a library item

- `update_existing_library_items()`
- `update_existing_library_items()`
- probably should not allow update / add new library python definition during runtime, this is risky and hard to quality control -->

- `validate_library(`_items=[]_`)`
  Check the validity of library items definition. This validity check includes checking the completeness of json specification (against library json schema) and Python verification class definition (against library class interface) and the match between the json and python implementation.

  - **Parameters**
    - **items**: list of str, default []. Library items to validate. By default, summarize all library items loaded at instantiation.
  - **Returns**: `pandas.DataFrame` that contains validity information of library items.

---

- `get_applicable_library_items_by_datapoints(`_datapoints_`)`
  Based on provided datapoints lists, identify potentially applicable library items from all loaded items. Use this function with caution as it 1) requires aligned data points naming across all library items; 2) does not check the topological relationships between datapoints.

  - **Parameters**
    - **datapoints**: list of str datapoints names.
  - **Returns**: `Dict` with keys being the library item names and values being the required datapoints for the corresponding keys.

---

- `get_required_datapoints_by_library_items(`_items=[]_`)`
  Summarize datapoints that need to be used to support specified library items. Use this function with caution as it 1) requires aligned data points naming across all library items; 2) does not check the topological relationships between datapoints.

  - **Parameters**
    - **items**: list of str, default []. Library items to summarize datapoints from. By default, summarize all library items loaded at instantiation.
  - **Returns**: `Dict` with keys being the datapoint name and values being a sub `Dict` with the following keys:
    - `number_of_items_using_this_datapoint`: int, number of library items that use this datapoint.
    - `library_items_list`: List, of library item names that use this datapoint.

**note for consistent naming**:

- manage a static mapping of standardized variable names and descriptions
- validate the point name definition of library items against these mapping when validating library items

---

## Data Processing API

### Data Processing API documentation

This API loads datasets and manipulate data before feeding it to the verification process.

`class DataProcessing`

- `__init__(`_data: str_`)`

  Class object initialization.

  - **parameters**:
    - **data**: Path to the data (CSV format) to be loaded for processing. Data will be stored in a `pandas.DataFrame()` object.
  - **Returns**: class object with `self.data` loaded with a `pandas.DataFrame`.

- `slice(`_start_time: datetime, end_time: datetime object_, inplace=False`)`

  Discard any data in `self.data` before or after _start_time_ and _end_time_

  - **parameters**:
    - _start_time_: `datetime.date()` object that represents the first cut-off date to slice the data.
    - _end_time_: `datetime.date()` object that represents the second cut-off date to slice the data.
    - _inplace_: bool, whether to do inplace modification of the data. By default, False.
  - **return**: `pandas.DataFrame()` that only contain a slice of the original `self.data`

- `add_parameter(`_name: str, value: float_, inplace=False`)`

  Add a parameter to `self.data`. The parameter will be added as a constant value for all index of `self.data`

  - **parameters**:
    - _name_: name of the parameter to add
    - _value_: value of the parameter

- `concatenate(`\*datasets: list(pandas.DataFrame), inplace=False`)`

  Concatenate datasets with `self.data`

  - **parameters**:
    - _datasets_: list of datasets to concatenate with `self.data`
    - inplace:
    - axis: 1: concatenate vertical (timestamp / row); 0: concatenate horizontally (datapoint / column).
      - when 1: check if all datasets have same columns, if not, break;
      - when 0: check if all datasets have same datetime index, if not, break.
    - **return**: `pandas.DataFrame` that contains the concatenated datasets

- `apply_func(`_var_names: list(str), new_var_name: str, function: str_`)`

  Apply a basic aggregate function to a list of variables from `self.data`

  - **parameters**:
    - _var_names_: list of variables from `self.data` to be used for the aggregation function
    - _new_var_name_: name of the new variable that will contain the aggregated data
    - _function_: one of the following aggregate function 'sum', 'max', 'min', or 'average'
    - **return**: `pandas.DataFrame` containing all existing and a newly computed column.

- `check()`

  Perform a sanity check on the data.

  - **return**: dict showing the following information:
    - Number of missing values for each variables
    - Outliers for each variable

**for data sanity check, once we link the data with datapoint type through verification case, we can check data validity against different rules of different data types. e.g. sat should not be < -30**

- `summary()`

  Provide a summary of the data

  - **return**: dict showing the following information
    - Number of data points
    - Resolution
    - For each variables
      - Minimum
      - Maximum
      - Mean
      - Standard deviation

- `plot(`_variable_names: list(str), kind= str_`)`

  Create plots of timesteries data, or scatter plot between two variables

  - **parameters**:
    - _variable_names_: list of variables from `self.data` to be plotted
    - _kind_: 'timeseries', or 'scatter'; If 'timeseries' is used, all variable names provided in `variable_names` will be plotted against the index timestamp from `self.data`; If 'scatter' is used, the first variables provided in the list will be used as the x-axis, the other will be on the y-axis
  - **return**: `matplotlib.axes.Axes`

- `downsample(`_rule: str_`)`

  Downsample `self.data` according to a user provided rule

  - **parameters**:
    - _rule_: follows the same convention as [pandas.DataFrame.resample](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects)

- `interpolate(`\*method: str, variable_names: list`)`

  Interpolate missing values (NaN) in `self.data` following a user specified method

  - **parameters**:
    - _method_: 'linear', 'pad' as described [here](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html)
    - _variable_names_: list of variable names used for interpolation of missing values

- `check_for_verif(`_verification_case_`)`

  Checks that all variables necessary for a specific verification item are present

  - **parameters**:
    - _verification_case_: verification case object generated by the verification case API
  - **return**: dict that includes the following keys: `result` which is a bool, and `notes` which provides the list of missing variables from `self.data` to correctly perform the verification

**maybe create duals in Verification Case API / Verification API**

### Data Processing API Examples

```python
import animate as an
from datetime import date

# Load the data
dp = an.DataProcessing("./data.csv")

# Slice the data
dp.data = dp.slice(start_time=datetime.date(2007, 12, 5), end_time=datetime.date(2007, 12, 31))

# Add a parameter
dp.add_parameter(name="test", value="3.412")

# Concatenate data
dp_n = an.DataProcessing("./data2.csv")
dp.data = dp.concatenate(datasets=[dp_n])

# Verficication of the data
dp.check()
dp.summary()

# Visualization of the data
# 1 - Timeseries plot
dp.plot(variable_names=["Zone 1 Temp", "Zone 2 Temp"])

# 2 - Scatter plot
dp.plot(variable_names=["Outdoor Air Temp", "Mixed Air Temp"])

# Interpolate missing data
dp.interpolate(method='linear', variable_names=['Outdoor Air Temperature])

# Downsampling
dp.downsampling(rule='1H')

# Check data for verification case
case_1 = an.VerificationCase("./verification_case_1.json") # <- this API is not documented here
dp.check_for_verif(verification_case=case_1)

```

## Verification Case API

### Verification Case API documentation

`class VerificationCase`

- `__init__()`

  Class object initialization. Define `self.case_suite` as a Dict. keys being automatically generated unique id of case, values being the fully defined verification case Dict.

- `load_verification_cases_from_json(`_json_case_path: str_`)`

  Add verification cases from specified json file into `self.case_suite`

  - **Parameter**
    - _json_case_path_: Dict, path to the json file containing fully defined verification cases.
  - **Returns**: List, unique ids of verification cases loaded in `self.case_suite`

- `load_verification_case_from_dict(`_case: Dict_`)`

  Add one verification case defined as a Dict into `self.case_suite`

  - **Parameter**
    - _case_: Dict, fully defined verification case in `Dict` format
  - **Returns**: unique id of the case stored in self.case_suite[unique_id]

- `load_verification_cases_from_list(`_cases: List_`)`

  Add multiple verification cases into `self.case_suite`

  - **Parameter**
    - _cases_: List, containing fully defined verification cases Dict.
  - **Returns** unique id of the cases stored in self.case_suite[unique_id]

- `static create_verificaton_case_suite_from_base_case(`_base_case: dict, update_key_value: Dict_, keep_base_case=True`)`

  Create slightly different multiple verification cases by changing keys and values as specified in `update_key_value`. Design illustrated with example below.

  - **parameters**:
    - _base_case_: Dict. Base verification input information.
    - _update_key_value_: Dict with structured keys pointing to fields to be updated and leaf values being list of values to be populated with.
    - _keep_base_case_: Bool, whether to keep the base case in returned list of verification cases. Default to False.
  - **Returns** List. A list of Dict, each dict is a generated case from the base case.

Example:

Base case:

```json
{
  "data_points": {
    "sat": {
      "variable_name": "ahu1_sat"
    },
    "rat": {
      "variable_name": "ahu1_rat"
    }
  }
}
```

Objective: change sat from ahu1_sat to ahu2_sat and ahu3_sat, and accordingly, change rat to the corresponding list (ahu1_rat, ahu2_rat, ahu3_rat).

Define update_key_value as

```json
{
  "data_points": {
    "sat": {
      "variable_name": ["ahu1_sat", "ahu2_sat", "ahu3_sat"]
    },
    "rat": {
      "variable_name": ["ahu1_rat", "ahu2_rat", "ahu3_rat"]
    }
  }
}
```

- `get_verification_case_template(`_tamplate_format: str_`)`

  return a verification case template with contents being descriptive placeholders.

  - **return**: Dictionary that has the `new_library_verification_cases.json` format

- `static validate_verification_case_structure(`_case: dict, verbose: bool=False_`)`

  Validate verification case structure (e.g., check whether `run_simulation`, `simulation_IO`, etc. exist or not). Check if required key / values pairs exist in the case. check if datatype of values are appropriate, e.g. file path is str.

  -**parameters**:

  - `_case_`: case information that will be validated.
  - `_verbose_`: whether to output verbose information. Default to False.
  - **return**: Bool, indicating whether the case structure is valid or not (bool).

<!-- - `static validate_verification_cases(`_list_IDs: list, verbose: bool_`)`

  Validate cases (e.g., check whether `run_simulation`, `simulation_IO`, etc. exist or not). Check if required key / values pairs exist in the case. check if datatype of values are appropriate, e.g. file path is str

  -**parameters**: -`_list_IDs_`: list of IDS that will be validated. -`_verbose_`: whether additional explanation is required.

  - **return**: list, the first element indicates whether the file is valid or not (bool). The second element outputs additional info (str)if vebose arg is set to `True`. -->

- `static validate_verification_case_validity(`_case: dict, verbose: bool=False, run_path:str='_'`)`

  Validate the contents in the verification case. Deeper validation to things like, if the idf file path is pointing at a valid idf file. This is more advanced and optional feature.

  - **parameters**:
    - `_case_`: case information that will be validated.
    - `_verbose_`: whether to output verbose information. Default to False.
    - `_run_path_`: str, directory path where the user intends to run the verification case from. This is used to check for validity of relative paths used in the verification case definition. By default, use current working directory.
  - **return**: Bool, indicating whether the case content is valid or not (bool).

<!-- - `validate_verification_cases_validity(`_list_IDs, verbose: bool_`)`

  Validate the contents in the verification cases (e.g., `simulation_IO` value type is `str`, etc.). Deeper validation to things like, if the idf file path is pointing at a valid idf file. This is more advanced and optional feature.

  - **parameters**: -`_list_IDs_`: list of IDS that will be validated. -`_verbose_`: validate output option. If `verbose=True` is used and validation failed, output additional info.
  - **return**: list, the first element indicates whether the file is valid or not (bool). The second element outputs additional info (str)if verbose arg is set to `True`. -->

- `save_case_suite_to_json(`_json_path: str, case_ids=[]_`)`

  Save verification cases in `self.case_suite` to a dedicated file.

  - **parameters**:
    - _json_path_: str. json file path to save the cases
    - _case_ids_: List. Unique ids of verificationc cases to save. By default, save all cases in `self.case_suite`

- `static save_verification_cases_to_json(`_json_path: str, cases: list_`)
  - **parameters**:
    - _json_path_: str. json file path to save the cases
    - _case_ids_: List. List of complete verification cases Dictionary to save.

<!-- - `generate_verification_case_with_BRICK(`_BRICK_instance_path:str , verification_file_path: str_`)`

  Generate verification case(s) with BRICK instance

  - **parameters**: -_BRICK_instance_path_: Path that a brick instance is located (e.g., `./resources/brick_instance.ttl`). -_verification_file_path_: Path that the generated verification item is saved (e.g., `./schema/new_library_verification_cases.json`). -->

### Verification Case API Examples

```python
import animate as an

# create verification items in suite
SAT_case = {
    "id": "example_id",
    "no": 1,
    "run_simulation": true,
    "simulation_IO": {
        "idf": "../test_cases/doe_prototype_cases/ASHRAE901_Hospital_STD2019_Atlanta.idf",
        "idd": "../resources/Energy+V9_0_1.idd",
        "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
        "output": "eplusout.csv",
        "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe"
    },
    "expected_result": "fail",
    "datapoints_source": {
        "idf_output_variables": {
            "T_zone": {
                "subject": "PERIMETER_ZN_1",
                "variable": "Zone Air Temperature",
                "frequency": "TimeStep"
            }
        },
        "parameters": {}
    },
    "verification_class": "NightCycleOperation"
}


# define Verification object
verification_instnace = an.Verification()

# load existing verification case
verification_instance.load_verification_case("./schema/new_library_verification_cases.json")

# add a case to the existing case
verification_instance.generate_verification_case(SAT_case)

# create verification cases in suite
update_key_value = {
"datapoints_source": {
    "idf_output_variables": {
        "T_zone": {
            "subject": ["PERIMETER_ZN_2", "PERIMETER_ZN_3", "PERIMETER_ZN_4"],
            "variable": "Zone Air Temperature",
            "frequency": "TimeStep"
        }
    }
  }

verification_instance.create_verificaton_case_suite_from_base_case(SAT_case, update_key_value)

# validate the case format
verification_instance.validate_verification_cases_validity(["example_id"], verbose=False)

# validate the cases
verification_instance.validate_verification_cases(["example_id"], verbose=False)

# save the updated cases
verification_instance.save_verification_case("./schema/new_library_verification_cases.json")

```

## Verification API

### Verification API documentation

`class Verification`

- `__init__(`_verification: verification object_`)`

  Class initialization

  - **parameters**:
    - **verification**: ANIMATE verification object

- `configure(`_output_path: str_`)`

  Configure verification environnement

  - **parameters**:
    - _output_path_: path to the output directory used to store the markdown verification summary file
    - potential other configuration options
      - verbose
      - plot options
      - multiprocessing (num_threads)

- `run(`_plotting_option: str, fig_size= list_`)`

  Run verification

  - **parameters**:
    - _plotting_option_: 'all-compact', 'all-expand', 'day-compact', 'day-expand'
    - _fig_size_: list that provides the height and width of the figures
    - **maybe we can move these options to the configure parameters**
  - **return**: dict that includes the verification results

### Verification API Examples

### API Examples

```python
import animate as an

# Load verfication case
verif = an.Verification("./verification_case.json")

# Configure verification
verif.configure()

# Run verification
verif.run()
```

## Reporting API

### Reporting API documentation

- `__init__(`_verification_md: str, result_md_path: str, report_format: str_`)`

  Class initialization

  - **parameters**:
    - **verification_md**: Path to the result markdown files after verifications to be loaded for reporting.
    - **result_md_path**: Path where the summarized markdown file is saved. the default path is (`./results`)
    - **report_format**: File format to be output (focus on markdown, later we can consider html, pdf, csv, etc.)

- `report_multiple_cases(case_ids)`

  - **Parameters**
    - **case_ids**: List, of unique verification case ids. **Note, we need to assign unique verification case ids at case creation and check for verification case id uniqueness in case suite**
      Report multiple case result by implementing `summarize_md.py`

### Reporting API Examples

```
import animate as an

# Initiate the Reporting class
result_md = an.Reporting("./results/*.md", "./results", "markdown")

# report single case
result_md.report_single_case()

# report multiple cases
result_md.report_multiple_cases()
```

## Utilities API

### Utilities API documentation

`class Utilities`

**all methods under this class are static**

- `timestamp_alignment(`_df1: pd.DataFrame, df2: pd:DataFrame, how="inner"_`)`

  align two different dataframe data based on timestamps. We can use `pandas.DataFrame.merge` method. More explanations are shown in this [LINK](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html).

  - **parameters**: -_df1_: DataFrame that is aligned with `df2`. -_df1_: DataFrame that is aligned with `df1`. -_how_: same as the `how` arg in the merge method. {‘left’, ‘right’, ‘outer’, ‘inner’, ‘cross’}, default ‘inner’
  - **return**: DataFrame that has aligned timestamps

- `add_DST(`_df:pd.DataFrame, year:str_`)`

  Add daylight saving time (`DST_Time`) column in `self.df` dataframe.

  - **parameters**: -_df_: DataFrame -_year_: year to be considered for DST
    - **return**: df DataFrame that has DST_TIME column

### Utilities API Examples

```python
import animate as an

# define Utilities object

Utilities_instance = an.Utilities()

# align two dataframe that have different timestamps
df1 = pd.date_range("2018-01-01", periods=36, freq="5T") # 5 min interval
df2 = pd.date_range("2018-01-01", periods=12, freq="15T") # 15 min interval

aligned_df = Utilities_instance.timestamp_alignment(df1, df2, how="inner")

# DST
self.df = Utilities_instance.add_DST(self.df, 2017)
```

## Workflow API

The workflow API define a complete workflow of running ANIMATE verification job(s). It is designed to be an orchestration tool that coordinates the use of other categories of APIs.

`class VerificationLibrary`

- `static` `get_workflow_template()`
  - **Returns** a `Dict` template of workflow definition with descriptions of fields to be filled.

---

- `static` `list_existing_workflows(`_workflow_dir=''_`)`
  List existing workflows (defined as json files) under a specific directory path.

  - **Parameters**
    - **workflow_dir**: str, path to the directory containing workflow definitions (including sub directories). By default, point to the path of the example folder.
  - **Returns** `Dict` with keys being workflow names and values being a `Dict` with the follwoing keys:
    - `workflow_json_path`: path to the file of the workflow
    - `workflow`: `Dict` of the workflow, loaded from the workflow json definition.

---

- `__init__(`_workflow_path: str_`)`
  Instantiate a Workflow class object and load specified workflow as a `Dict` in `self.workflow`.

  - **Parameters**
    - **workflow_path**: str. path to the workflow definition json file.
  - **Returns**: Workflow class object with specified workflow as a `Dict` in `self.workflow`.

---

- `validate_workflow_definition(workflow)`
  Validate a workflow definition.

  - **Parameters**
    - **workflow**: str or Dict. If str, this is assumed to be the path to the workflow definition json file; If Dict, this is assumed to be loaded from the workflow json definition.
  - **Returns** `Dict` with the following keys:
    - `workflow_validity`: bool flag of the validity of the workflow definition
    - `detail`: detailed info about the validity check.

---

- `save(json_path)`
  Save the workflow as a json file.
  - **Parameters**
    - **json_path**: path to the file to be saved.

---

- `dryrun_workflow(verbose=False)`
  **Advanced feature, optional for now.**
  - **Parameters**
    - `verbose`: bool. Wether to output detailed information. By default, False.
  - **Returns**: bool. Whether the dry run is successful or not.
  -

---

- `run_workflow(verbose=False)`
  - **Parameters**
    - `verbose`: bool. Wether to output detailed information. By default, False.
  - **Returns**: bool. Whether the run is successful or not.

---

### Workflow definition schema

```json
{{
    "workflow_name": "Name of the workflow",
    "meta": {
        "author": "author of the workflow",
        "date": "modified date",
        "version": "version number of the workflow",
        "description": "Narrative description of the workflow"
    },
    "third party imports": [
        "numpy",
        "pandas",
        "datetime"
    ],
    "states": [
        "Load data": {
            "Type": "MethodCall",
            "MethodCall": "DataProcessing",
            "Parameters": {
                "data": "xx.csv"
            },
            "Payloads": {
                "data": "$.data"
            },
            "Next": "Slice data"
        },
        "Slice data": {
            "Type": "MethodCall",
            "MethodCall": "Payloads['data'].slice",
            "Parameters": {
                "start_time": {
                    "Type": "Embedded MethodCall",
                    "MethodCall": "datetime.date.fromisoformat",
                    "Parameters": {
                        "fromisoformat": "20221001"
                    }
                },
                "end_time": {
                    "Type": "Embedded MethodCall",
                    "MethodCall": "datetime.date.fromisoformat",
                    "Parameters": {
                        "fromisoformat": "20230101"
                    }
                }
            },
            "Payloads": {
                "sliced_data": "$"
            },
            "Next": "Data Length Check"
        },
        "Data Length Check": {
            "Type": "Choice",
            "Choice": [
                "Variable": "len(Payloads['sliced_data']) > 1",
                "BooleanEquals": "True",
                "Next": "Initialize verification object"
            ]
        },
        "Initialize verification object": {
            "Type": "MethodCall",
            "MethodCall": "Verification",
            "Parameters": {
                "verification_cases_path": "x/yy.json"
            },
            "Payloads": {
                "verification": "$"
            },
            "Next": "Run verification"
        },
        "Run verification": {
            "Type": "MethodCall",
            "MethodCall": "Payloads['verification'].run",
            "Parameters": {},
            "Payloads": {
                "verification_md": "$.md",
                "verification_flag": "$.check_bool"
            },
            "Next": "Reporting"
        },
        "Reporting": {
            "Type": "MethodCall",
            "MethodCall": "Reporting",
            "Parameters": {
                "verification_md": "Payloads['verification_md']",
                "report_path": "x/yy.md",
                "report_format": "markdown"
            },
            "Payloads": {
                "verification": "$"
            },
            "End": "True"
        }
    ]
}}
```

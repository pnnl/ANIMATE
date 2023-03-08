import sys, logging, glob, json, inspect
from typing import Dict, List
import pandas as pd

sys.path.append("..")
from library import *


library_schema = {
    "library_item_id": (int, str, float),
    "description_brief": str,
    "description_detail": str,
    "description_index": list,
    "description_datapoints": dict,
    "description_assertions": list,
    "description_verification_type": str,
    "assertions_type": str,
}


class VerificationLibrary:
    def __init__(self, lib_path: str = None):
        """Instantiate a verification library class object and load specified library items as `self.lib_items`.

        Args:
            lib_path (str, optional): path to the verification library file or folder. If the path ends with `*.json`, then library items defined in the json file are loaded. If the path points to a directory, then library items in all jsons in this directory and its subdirectories are loaded. Library item need to have unique name defined in the json files and python files. Defaults to None.

        """

        self.lib_items = {}
        self.lib_items_json_path = {}
        self.lib_items_python_path = {}

        # check argument
        if lib_path == None:
            logging.error(
                "'lib_path' was not provided when instantiating the Verificationlibrary class object!"
            )
            return None

        if not isinstance(lib_path, str):
            logging.error(
                f"lib_path needs to be str of library file or foler path. It cannot be a {type(lib_path)}"
            )
            return None

        # load lib
        lib_path = lib_path.strip()

        lib_files_json_dict = {}
        if lib_path.split(".")[-1] == "json":
            lib_items_files = glob.glob(lib_path)
        else:
            if lib_path[-1] != "/":
                lib_path = lib_path + "/"
            lib_items_files = glob.glob(f"{lib_path}**/*.json", recursive=True)

        if len(lib_items_files) == 0:
            logging.error(f"There is no json file in {lib_path}")
            return None

        for lib_items_file_path in lib_items_files:
            with open(lib_items_file_path) as lib_items_file:
                lib_files_json_dict[lib_items_file_path] = json.load(lib_items_file)

        # store items
        for k, v in lib_files_json_dict.items():
            shared_keys = list(set(self.lib_items).intersection(v))
            if len(shared_keys) > 0:
                logging.warning(
                    f"{len(shared_keys)} repeated verification item names identified when loading: {shared_keys}"
                )

            self.lib_items.update(v)
            for lib_name, lib_content in v.items():
                self.lib_items_json_path[lib_name] = k
                if lib_name in globals().keys():
                    python_path = inspect.getfile(globals()[lib_name])
                else:
                    python_path = "Not Found"
                    logging.warning(
                        f"Python class file of loaded library item {lib_name} Not Found in the library"
                    )
                self.lib_items_python_path[lib_name] = python_path

    def get_library_item(self, item_name: str) -> Dict:
        """Get the json definition and meta information of a specific library item.

        Args:
            item_name (str): Verification item name to get.

        Returns:
            Dict: Library item information with four specific keys:
                - `library_item_name`: unique str name of the library item
                - `library_json`: library item json definition in the library json file.
                - `library_json_path`: path of the library json file that contains this library item.
                - `library_python_path`: path of the python file that contains the python implementation of this library item.
        """

        item_name = item_name.strip()

        if not item_name in self.lib_items.keys():
            logging.error(f"{item_name} is not in loaded library items.")
            return None

        item_dict = {
            "library_item_name": item_name,
            "library_definition": self.lib_items[item_name],
            "library_json_path": self.lib_items_json_path[item_name],
            "library_python_path": self.lib_items_python_path[item_name],
        }

        return item_dict

    def validate_library(self, items: List = []) -> pd.DataFrame:
        """Check the validity of library items definition. This validity check includes checking the completeness of json specification (against library json schema) and Python verification class definition (against library class interface) and the match between the json and python implementation.

        Args:
            items: list of str, default []. Library items to validate. By default, summarize all library items loaded at instantiation.

        Returns:
            pandas.DataFrame that contains validity information of library items.
        """

        # check `items` type
        if not isinstance(items, list):
            logging.error(f"items needs to be list. It cannot be a {type(items)}.")
            return None

        # validate lib
        validity_info = pd.DataFrame(
            columns=[
                "library_item_id",
                "description_brief",
                "description_detail",
                "description_index",
                "description_datapoints",
                "description_assertions",
                "description_verification_type",
                "assertions_type",
                "datapoints_match",
            ]
        )
        for item in items:
            validity_info_data = []

            # verify the library.json file
            for lib_key in library_schema.keys():
                # check if lib keys exist. "description_detail" key is optional
                if lib_key not in ["description_detail"] and not self.lib_items[
                    item
                ].get(lib_key):
                    logging.error(
                        f"{lib_key} doesn't exist. Please make sure to have {lib_key}."
                    )
                    return None

                # check if key is in the correct type
                try:
                    if not isinstance(
                        self.lib_items[item][lib_key], library_schema[lib_key]
                    ):
                        logging.error(
                            f"The type of `{lib_key}` key needs to be {str(library_schema[lib_key])}. It cannot be a {type(self.lib_items[item][lib_key])}."
                        )
                        return None

                    else:
                        validity_info_data.append(type(self.lib_items[item][lib_key]))

                except KeyError:
                    # # if `description_detail` key doesn't exist, output a warning.
                    validity_info_data.append(None)
                    logging.warning(f"{lib_key} doesn't exist.")

            # check if datapoints in library file and class are identical
            if (
                list(self.lib_items[item]["description_datapoints"].keys())
                != globals()[item].points
            ):
                logging.error(
                    f"{item}'s points in {self.lib_items_json_path[item].split('/')[-1]} and {self.lib_items_python_path[item].split(chr(92))[-1]} are not identical."
                )  # chr(92) is '\\. This is used b/c using '\\' not allowed in f-string.
                return None
            else:
                validity_info_data.append(True)

            validity_info.loc[item] = validity_info_data

        return validity_info

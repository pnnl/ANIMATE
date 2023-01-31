import sys, os, logging, glob, json, inspect, uuid

from typing import Dict

sys.path.append("..")


class VerificationCase:
    def __init__(self, case: Dict = None, file_path: str = None):
        """Instantiate a verification case class object and load verification case(s) in `self.case_suite` as a Dict. keys are automatically generated unique id of cases, values are the fully defined verification case Dict.

        Args:
            case: case dictionary that includes verification items.
            file_path: path to the verification case file. If the path ends with `*.json`, then the items in the JSON file are loaded. If the path points to a directory, then verification case item JSON files are loaded.
        """

        self.case_suite = {}
        if case is not None:
            # check `case` type
            if isinstance(case, dict):
                # check if the input dict is in the right format.
                # will employ 'validate_verification_case_structure' static method once it's added.

                # create a case_suite consisting of key: unique id, value: verification case
                for ele in case["cases"]:
                    self.case_suite[uuid.uuid1()] = ele
            else:
                logging.error(
                    f"The type of the 'case' argument has to be str, but {type(case)} type is provided. Please verify the 'case' argument."
                )

        if file_path is not None:
            # check 'file_path' type
            if isinstance(file_path, str):
                # check if json or directory path is provided.
                if file_path[-4:] == "json":
                    # check if 'file_path' exists
                    if os.path.isfile(file_path):
                        self.case_suite = self.read_case(file_path, self.case_suite)

                    else:
                        logging.error(
                            f"file_path: '{file_path}' doesn't exist. Please make sure if the provided path exists."
                        )
                else:  # when directory path is provided.
                    # check if the directory exists.
                    if os.path.exists(file_path):
                        # find all the JSON files in file_path directory.
                        json_file_names = glob.glob(os.path.join(file_path, "*.json"))

                        # check if JSON file(s) exists.
                        if len(json_file_names) != 0:
                            for file in json_file_names:
                                self.case_suite = self.read_case(
                                    file_path, self.case_suite
                                )
                        else:
                            logging.warning(
                                "There is no JSON files in the given file_path."
                            )
                    else:
                        logging.error(
                            "The provided directory doesn't exist. Please make sure to provide a correct file_path."
                        )
            else:
                logging.error(
                    f"The type of the 'file_path' argument has to be str, but {type(file_path)} type is provided. Please verify the 'file_path' argument."
                )

    def read_case(self, file_name, case_suite):
        # load the cases from file_path
        with open(file_name, "r") as f:
            loaded_cases = json.load(f)

        # check if the input dict is in the right format.
        # will employ 'validate_verification_case_structure' static method once it's added.

        for ele in loaded_cases["cases"]:
            case_suite[uuid.uuid1()] = ele

        return case_suite

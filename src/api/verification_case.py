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
            # check
            if isinstance(case, dict):
                # check if the input dict is in the right format
                # will employ 'validate_verification_case_structure' static method once it's added

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
                # check if json or directory path is provided
                if file_path[-4:] == "json":
                    # check if 'file_path' exists
                    if os.path.isfile(file_path):
                        self.case_suite = self.read_case(file_path, self.case_suite)

                    else:
                        logging.error(
                            f"file_path: '{file_path}' doesn't exist. Please make sure if the provided path exists."
                        )
                else:  # when directory path is provided
                    # check if the directory exists
                    if os.path.exists(file_path):
                        # find all the JSON files in file_path directory
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
                            f"The provided directory doesn't exist. Please make sure to provide a correct file_path."
                        )
            else:
                logging.error(
                    f"The type of the 'file_path' argument has to be str, but {type(file_path)} type is provided. Please verify the 'file_path' argument."
                )

    def read_case(self, file_name: str, case_suite: Dict) -> Dict:
        # load the cases from file_path
        with open(file_name, "r") as f:
            loaded_cases = json.load(f)

        # check if the input dict is in the right format
        # will employ 'validate_verification_case_structure' static method once it's added

        for ele in loaded_cases["cases"]:
            case_suite[uuid.uuid1()] = ele

        return case_suite

    def load_verification_cases_from_json(self, json_case_path: str) -> list:
        """Add verification cases from specified json file into self.case_suite

        Args:
            json_case_path: str, path to the json file containing fully defined verification cases.

        Returns:
          List, unique ids of verification cases loaded in self.case_suite
        """

        # check if json_case_path type is str
        if isinstance(json_case_path, str):
            # check if the json_case_path exists
            if os.path.isfile(json_case_path):
                self.case_suite = self.read_case(json_case_path, self.case_suite)
            else:
                logging.error(
                    "Please make sure that the 'json_case_path' argument is correct."
                )
        else:
            logging.error(
                f"The type of the 'json_case_path' argument has to be str, but {type(json_case_path)} type is provided. Please verify the 'json_case_path' argument."
            )

        return list(self.case_suite.keys())

    def save_case_suite_to_json(self, json_path: str, case_ids: list = []):
        """Save verification cases to a dedicated file. If case_ids is empty, all the cases in `self.case_suite` is saved. If case_ids includes specific cases' hash, the hashes in the list are only saved.

        Args:
            json_path: str. path to the json file to save the cases.
            case_ids: List. Unique ids of verification cases to save. By default, save all cases in `self.case_suite`
        """

        # check json_path type
        if not isinstance(json_path, str):
            logging.error(
                f"The type of the 'json_path' argument has to be str, but {type(json_path)} type is provided. Please verify the 'json_path' argument."
            )
            return None

        # check case_ids type
        if not isinstance(case_ids, list):
            logging.error(
                f"The type of the 'case_ids' argument has to be str, but {type(case_ids)} type is provided. Please verify the 'case_ids' argument."
            )
            return None

        # if json_path is saved in a different dir, check if it exists
        json_path_split = json_path.split("/")
        dir_path = "/".join(json_path_split[:-1])
        if len(dir_path) > 2:  # when json_path includes directory path
            if not os.path.exists(dir_path):
                logging.error(
                    f"{dir_path} directory doesn't exist. Please make sure to provide an already existing directory."
                )
                return None

        # organize the cases in the correct format
        case_suite_in_template_format = {"cases": []}
        case_suite_in_template_format_append = case_suite_in_template_format[
            "cases"
        ].append

        # save all the cases in self.case_suite
        if len(case_ids) == 0:
            if len(self.case_suite) != 0:
                for case in self.case_suite.items():
                    case_suite_in_template_format_append(case[1])
            else:
                logging.warning(
                    "There is no case to save. Please make sure if any cases are loaded."
                )
        else:  # save selective case(s)
            for case_id in case_ids:
                # check if case_id exists
                if case_id in self.case_suite:
                    case_suite_in_template_format_append(self.case_suite[case_id])
                else:
                    logging.error(
                        f"{case_id} hash doesn't exist in the self.case_suite. Please make sure to provide a correct case_ids argument."
                    )
        # save the case suite
        with open(json_path, "w") as fw:
            json.dump(case_suite_in_template_format, fw, indent=4)

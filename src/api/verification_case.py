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

    @staticmethod
    def validate_verification_case_structure(case: Dict, verbose: bool = False) -> bool:
        """Validate verification case structure (e.g., check whether `run_simulation`, `simulation_IO`, etc. exist or not). Check if required key / values pairs exist in the case. check if datatype of values are appropriate, e.g. file path is str.

        Args:
            case: dict. case information that will be validated.
            verbose: bool. whether to output verbose information. Default to False.

        Returns:
            Bool, indicating whether the case structure is valid or not.
        """

        def _validate_case_structure_helper(schema, instance, verbose):
            is_cases_valid = True
            for key, value in schema.items():
                if isinstance(value, dict):
                    is_cases_valid = _validate_case_structure_helper(
                        value, instance[key], verbose
                    )
                    if not is_cases_valid:
                        break
                else:
                    if key in instance:
                        if type(instance[key]) != schema[key]:
                            if verbose:
                                logging.error(
                                    f"The type of '{key}' key must be {schema[key]}, but {type(instance[key])} is provided."
                                )
                            return False
                    else:
                        if verbose:
                            logging.error(
                                f"'{key}' key is NOT in the `case` argument. Please make sure to include the '{key}' key in the `case` argument. "
                            )
                        return False

                    if key == "idf_output_variables":
                        for idf_key, idf_value in instance[key].items():
                            if not isinstance(instance[key][idf_key], dict):
                                if verbose:
                                    logging.error(
                                        f"idf_output_variables is NOT dict type."
                                    )
                                return False

                            if not instance[key][idf_key].get("subject"):
                                if verbose:
                                    print(
                                        f"'subject' key doesn't exist in {instance[key][idf_key]}. Please make sure to include the 'subject' key."
                                    )
                                return False

                            if not isinstance(
                                instance[key][idf_key].get("subject"), str
                            ):
                                if verbose:
                                    logging.error(
                                        f"The type of '{idf_key}' subject's value must be str, but {type(instance[key][idf_key].get('subject'))} is provided."
                                    )
                                return False

                            if not instance[key][idf_key].get("variable"):
                                if verbose:
                                    logging.error(
                                        f"'variable' key doesn't exist in {instance[key][idf_key]}. Please make sure to include the 'variable' key."
                                    )
                                return False

                            if not isinstance(
                                instance[key][idf_key].get("variable"), str
                            ):
                                if verbose:
                                    logging.error(
                                        f"The type of '{idf_key}' variable's value must be str, but {type(instance[key][idf_key].get('variable'))} is provided."
                                    )
                                return False

                            if not instance[key][idf_key].get("frequency"):
                                if verbose:
                                    logging.error(
                                        f"'frequency' key doesn't exist in {instance[key][idf_key]}. Please make sure to include the 'frequency' key."
                                    )
                                return False

                            if not isinstance(
                                instance[key][idf_key].get("frequency"), str
                            ):
                                if verbose:
                                    logging.error(
                                        f"The type of '{idf_key}' frequency's value must be str, but {type(instance[key][idf_key].get('frequency'))} is provided."
                                    )
                                return False

                    if key == "parameters":
                        for idf_key, idf_value in instance[key].items():
                            if not isinstance(
                                instance[key][idf_key], float
                            ) and not isinstance(instance[key][idf_key], int):
                                if verbose:
                                    logging.error(
                                        f"The type of '{idf_key}' value must be either float or int, but {type(instance[key][idf_key])} is provided."
                                    )
                                return False

            return is_cases_valid

        # check case type
        if not isinstance(case, Dict):
            logging.error(
                f"The case argument type must be dict, but {type(case)} is provided."
            )
            return None

        # check verbose type
        if not isinstance(verbose, bool):
            logging.error(
                f"The verbose argument type must be bool, but {type(verbose)} is provided."
            )
            return None

        # case schema used for
        case_schema = {
            "no": int,
            "run_simulation": bool,
            "simulation_IO": {
                "idf": str,
                "idd": str,
                "weather": str,
                "output": str,
                "ep_path": str,
            },
            "expected_result": str,
            "datapoints_source": {"idf_output_variables": dict, "parameters": dict},
            "verification_class": str,
        }
        return _validate_case_structure_helper(case_schema, case, verbose)

    @staticmethod
    def save_verification_cases_to_json(json_path: str, cases: list):
        """Save verification cases to a dedicated file. The cases list consists of verification case dicts.

        Args:
            json_path: str. json file path to save the cases.
            cases: List. List of complete verification cases Dictionary to save.

        """

        # check json_path type
        if not isinstance(json_path, str):
            logging.error(
                f"The json_path argument type must be str, but {type(json_path)} is provided."
            )
            return None

        # check cases type
        if not isinstance(cases, list):
            logging.error(
                f"The cases argument type must be list, but {type(cases)} is provided."
            )
            return None

        # check if json_path extension is .json
        if json_path[-5:] != ".json":
            logging.error(f"The json_path argument must end with '.json' extension.")
            return None

        # organize the cases in the correct format
        case_suite_in_template_format = {"cases": []}
        case_suite_in_template_format_append = case_suite_in_template_format[
            "cases"
        ].append
        for case in cases:
            case_suite_in_template_format_append(case)

        # save the case suite
        with open(json_path, "w") as fw:
            json.dump(case_suite_in_template_format, fw, indent=4)

import sys, logging, json
from typing import Union

sys.path.append("./src")
sys.path.append("..")
from api import VerificationLibrary, DataProcessing, VerificationCase


class Workflow:
    def __init__(self, workflow_path: str = None, workflow_dict: dict = None):
        """Instantiate a Workflow class object and load specified workflow as a `dict` in `self.workflow`

        Args:
            workflow_path (str, optional): path to the workflow definition json file. Defaults to None.
            workflow_dict (dict, optional): dict of the workflow. Defaults to None.
        """
        pass

    @staticmethod
    def get_workflow_template() -> dict:
        """Provide a `Dict` template of workflow definition with descriptions of fields to be filled

        Returns:
            dict: workflow definition template
        """
        pass

    @staticmethod
    def list_existing_workflows(workflow_dir: str = None) -> dict:
        """List existing workflows (defined as json files) under a specific directory path.

        Args:
            workflow_dir (str, optional): path to the directory containing workflow definitions (including sub directories). By default, point to the path of the example folder. @JXL TODO example folder to be specified

        Returns:
            dict: `dict` with keys being workflow names and values being a `Dict` with the following keys:
                - `workflow_json_path`: path to the file of the workflow
                - `workflow`: `Dict` of the workflow, loaded from the workflow json definition
        """
        pass

    @staticmethod
    def validate_workflow_definition(workflow: Union[str, dict]) -> dict:
        """Validate a workflow definition.

        Args:
            workflow (Union[str, dict]): If str, this is assumed to be the path to the workflow definition json file; If dict, this is assumed to be loaded from the workflow json definition.

        Returns:
            dict: `dict` with the following keys:
                - `workflow_validity`: bool flag of the validity of the workflow definition
                - `detail`: detailed info about the validity check.
        """
        pass

    def validate(self) -> dict:
        """Validate `self.workflow`

        Returns:
            dict: `dict` with the following keys:
                - `workflow_validity`: bool flag of the validity of the workflow definition
                - `detail`: detailed info about the validity check.
        """
        return self.validate_workflow_definition(self.workflow)

    def save(self, json_path: str = None) -> None:
        """Save the workflow as a json file.

        Args:
            json_path (str, optional): path to the file to be saved. Defaults to None.
        """

        pass

    def run_workflow(self, verbose: bool = False) -> bool:
        """Execute the workflow defined in self.workflow

        Args:
            verbose (bool, optional): bool. Wether to output detailed information. Defaults to False.

        Returns:
            bool: Whether the run is successful or not.

        """
        pass


class WorkflowEngine:
    def __init__(self, workflow):
        self.end_state_name = None
        self.start_state_name = None
        self.payloads = {}
        self.states = {}
        self.workflow_dict = {}
        self.running_sequence = []

        if isinstance(workflow, str):
            self.load_workflow_json(workflow)

        if isinstance(workflow, dict):
            self.workflow_dict = workflow

        self.load_states()
        self.run_workflow()

    def import_package(self):
        # @JXL TODO: import packages specified in workflow

    def load_workflow_json(self, workflow_path):
        with open(workflow_path) as f:
            self.workflow_dict = json.load(f)

    def load_states(self):
        for state_name, state_dict in self.workflow_dict["states"].items():
            # there should be no duplicate names
            if state_name in self.states:
                logging.error(
                    f"State name [{state_name}] is not unique in the loaded workflow. This is NOT allowed."
                )
                return None

            self.states[state_name] = state_dict
            if "Start" in state_dict and state_dict["Start"] == "True":
                self.start_state_name = state_name

            if "End" in state_dict and state_dict["End"] == "True":
                self.end_state_name = state_name
                continue

            if (state_dict["Type"] != "Choice") and ("Next" not in state_dict):
                logging.error(
                    f"Non-Choice state [{state_name} is not an End state and it has no Next state. This is NOT allowed."
                )

    def run_state(self, state_name):
        state_dict = self.states[state_name]
        state_type = state_dict["Type"]
        next_state = None

        if state_type == "MethodCall":
            self.payloads = MethodCall(state_dict, self.payloads).run().get_payloads()
            if "Next" in state_dict:
                next_state = state_dict["Next"]

        if state_type == "Choice":
            next_state = Choice(state_dict, self.payloads).check_choices()

        if (state_name != self.end_state_name) and (next_state is not None):
            return next_state
        else:
            return None

    def run_workflow(self, max_states=1000):
        current_state_name = self.start_state_name
        state_count = 0
        while current_state_name is not None:
            self.running_sequence.append(current_state_name)
            current_state_name = self.run_state(current_state_name)
            state_count += 1
            if state_count > max_states:
                break

    def summarize_workflow_run(self):
        print(
            f"A total of {len(self.running_sequence)} states were executed with the following sequence:"
        )
        step_count = 0
        for element in self.running_sequence:
            step_count += 1
            print(f"State {step_count}: {element}")

        return {
            "total_states_executed": step_count,
            "state_running_sequence": self.running_sequence,
        }


class MethodCall:
    def __init__(self, state_dict, payloads):
        self.payloads = payloads
        self.parameters = {}
        self.state_dict = state_dict
        self.dollar = None
        self.build_parameters(state_dict)

    def build_parameters(self, state_dict):
        if isinstance(state_dict["Parameters"], dict):
            for k, v in state_dict["Parameters"].items():
                self.parameters[k] = self.build_param_value(v)
        if isinstance(state_dict["Parameters"], list):
            # some python built-in methods only accept positional arguments
            self.parameters = [
                self.build_param_value(x) for x in state_dict["Parameters"]
            ]

    def build_param_value(self, v):
        if isinstance(v, dict):
            # if parameter value is a dict, then it needs to be an embedded method call style
            new_v = self.embedded_call(v)
            return new_v

        if isinstance(v, int) or isinstance(v, float):
            return v

        if isinstance(v, str):
            # special string treatment
            if v.split("[")[0] == "Payloads":
                # only in this case we eval
                return eval(v)
            else:
                # in all other string param value, we consider it is a string. This is for clarity and security. More complicated parameter should use embedded methodcall
                return v

    def run(self):
        Payloads = self.payloads
        method_call = eval(self.state_dict["MethodCall"])
        if isinstance(self.parameters, dict):
            self.dollar = method_call(**self.parameters)
        if isinstance(self.parameters, list):
            self.dollar = method_call(*self.parameters)
        return self

    def get_method_return(self):
        return self.dollar

    def get_payloads(self):
        for k, v in self.state_dict["Payloads"].items():
            if isinstance(v, str):
                # only eval if v is string
                self.payloads[k] = eval(v.replace("$", "self.dollar"))
            else:
                self.payloads[k] = v
        return self.payloads

    def embedded_call(self, embedded_case_dict):
        if embedded_case_dict["Type"] != "Embedded MethodCall":
            logging.error(
                f"If parameter value is a dict, it needs to be of type 'Embedded MethodCall'. Problematic state definition: {embedded_case_dict}"
            )
            return None

        return MethodCall(embedded_case_dict, self.payloads).run().get_method_return()


class Choice:
    def __init__(self, state_dict, payloads):
        self.payloads = payloads
        self.state_dict = state_dict

    def check_choices(self):
        for choice in self.state_dict["Choices"]:
            choice_return = self.check_choice(choice)
            if isinstance(choice_return, str):
                return choice_return
            # if current choice does not give a next step, then check the next one
            continue

        # no valid next step has been identified. check if there is a default state, if not, log error
        if "Default" in self.state_dict:
            return self.state_dict["Default"]
        else:
            logging.error("Among all choices, no valid next step identified. Abort!")
            return None

    def check_choice(self, choice):
        if not isinstance(choice, dict):
            logging.error("choice has to be a dict")
            return None
        if "Value" not in choice:
            # when 'Value' is not in choice, a logical expression key is expected
            # check only one logic expression in the key
            eligible_logic = ["ALL", "ANY", "NONE"]
            keycheck_flag = [(ek in choice) for ek in eligible_logic]
            if sum(keycheck_flag) != 1:
                logging.error(
                    "For logical expression choices state, there needs to be exactly one key of either 'ALL', or 'ANY', or 'NONE'."
                )
                return None

            if "ALL" in choice:
                flag_list = [self.get_choice_value(x) for x in choice["AND"]]
                choice_value = all(flag_list)
            if "NONE" in choice:
                flag_list = [self.get_choice_value(x) for x in choice["NONE"]]
                choice_value = not any(flag_list)
            if "ANY" in choice:
                choice_value = False
                for subchoice in choice["ANY"]:
                    if self.get_choice_value(subchoice):
                        choice_value = True
                        break

        else:
            # 'leaf' choice implementation
            choice_value = self.get_choice_value(choice)

        if choice_value:
            return choice["Next"]
        else:
            return False

    def get_choice_value(self, choice):
        Payloads = self.payloads
        left = choice["Value"]
        right = choice["Equals"]

        # only eval when it is a string
        if isinstance(left, str):
            left = eval(choice["Value"])
        if isinstance(right, str):
            right = eval(choice["Equals"])

        if left == right:
            return True
        else:
            return False


def main():
    Workflow("./tests/api/data/testworkflow.json")


if __name__ == "__main__":
    main()

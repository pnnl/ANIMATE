import datetime
import sys, logging, glob, json, inspect
from typing import Dict

sys.path.append("./src")
sys.path.append("..")
from library import *
from api import DataProcessing
from abc import ABC, abstractmethod


class Workflow:
    def __init__(self, workflow):
        # self.workflow_name = ""
        # self.meta = {
        #     "author": "",
        #     "date": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M"),
        #     "version": "",
        #     "description": "",
        # }
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

            if "Next" not in state_dict:
                logging.error(
                    f"State [{state_name} is not an End state and it has no Next state. This is NOT allowed."
                )

    def run_state(self, state_name):
        state_dict = self.states["state_name"]
        type = state_dict["Type"]

        state_call = {"MethodCall": MethodCall, "Choice": Choice}
        if type == "MethodCall":
            self.payloads = (
                state_call[type](state_dict, self.payloads).run().get_payloads()
            )

        if type == "Choice":
            pass
            # TODO: JXL no payload change, just point to the next step

        if state_name != self.end_state_name:
            return state_dict["Next"]
        else:
            return None

    def run_workflow(self):
        current_state_name = self.start_state_name
        next_state_name = self.states[current_state_name]["Next"]

        while current_state_name is not None:
            self.running_sequence.append(current_state_name)
            current_state_name = self.run_state(current_state_name)

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
                # expecting Payloads['xx']
                return  # @JXL place holder for doing Payloads value

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
            self.payloads[k] = eval(v.replace("$", "self.dollar"))
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

    def check_choice(self, choice):
        if not isinstance(choice, dict):
            logging.error("choice has to be a dict")
            return None
        if "Value" not in choice:
            # when 'Value' is not in choice, a logical expression key is expected
            if "AND" in choice:
                pass  # placeholder to get and implemented
                choice_value = None
            # placeholder to get other logical relationships implemented.
        else:
            # 'leaf' choice implementation
            choice_value = self.get_choice_value(choice)

        if choice_value:
            return choice["Next"]
        else:
            return False

    def get_choice_value(self, choice):
        left = eval(choice["Variable"])
        right = eval(choice["Equals"])
        if left == right:
            return True
        else:
            return False


def main():
    Workflow("./tests/api/data/testworkflow.json")


if __name__ == "__main__":
    main()

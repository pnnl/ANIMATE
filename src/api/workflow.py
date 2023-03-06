import datetime
import sys, logging, glob, json, inspect
from typing import Dict
sys.path.append("./src")
sys.path.append("..")
from library import *
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
        self.payload = {}
        self.states = {}
        self.workflow_dict = {}

        if isinstance(workflow, str):
            self.load_workflow_json(workflow)

        if isinstance(workflow, dict):
            self.workflow_dict = workflow

        self.load_states()


    def load_workflow_json(self, workflow_path):

        with open(workflow_path) as f:
            self.workflow_dict = json.load(f)

    def load_states(self):
        for state_name, state_dict in self.workflow_dict['states'].items():
            # there should be no duplicate names
            if state_name in self.states:
                logging.error(
                    f"State name [{state_name}] is not unique in the loaded workflow. This is NOT allowed."
                )
                return None

            self.states[state_name] = state_dict
            if 'Start' in state_dict and state_dict['Start'] == 'True':
                self.start_state_name = state_name

            if 'End' in state_dict and state_dict['End'] == 'True':
                self.end_state_name = state_name
                continue

            if 'Next' not in state_dict:
                logging.error(
                    f"State [{state_name} is not an End state and it has no Next state. This is NOT allowed."
                )


    def run_state(self, state_dict):
        type = state_dict["type"]
        state_call = {"MethodCall": MethodCall}
        self.payload = state_call[type](state_dict)


#
# class State(ABC):
#
#     def __init__(self, state_dict):
#         self.type = state_dict['type']
#


class MethodCall:
    def __init__(self, state_dict):
        pass
def main():
    Workflow('./tests/api/data/testworkflow.json')

if __name__ == "__main__":
    main()

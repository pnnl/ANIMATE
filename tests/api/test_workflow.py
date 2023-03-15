import unittest, sys, datetime, copy

sys.path.append("./src")

from api import Workflow

class TestWorkflow(unittest.TestCase):
    def test_run_workflow(self):
        workflow = Workflow(workflow="./demo/api_demo/demo_workflow.json")
        workflow.run_workflow(verbose=True)
import unittest, sys, datetime, copy

sys.path.append("./src")

from api import Workflow

class TestWorkflow(unittest.TestCase):
    def test_run_workflow(self):
        workflow = Workflow(workflow="./tests/api/data/testworkflow.json")
        workflow.run_workflow(verbose=True)
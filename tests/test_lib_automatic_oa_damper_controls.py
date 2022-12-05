import unittest, sys

sys.path.append("../src")
from lib_unit_test_runner import *
from library_test import *

import json
import pandas as pd


class TestAutomaticOADamperControl(unittest.TestCase):
    def test_something(self):
        points = ["o", "m_oa", "eco_onoff", "tol"]
        data = [[0, 1, 0, 0.001]]
        df = pd.DataFrame(data, columns=points)
        # case_str = """
        # {
        #     "datapoints_source":{},
        #     "verification_class": "AutomaticOADamperControl"
        # }"""
        # case_str = """
        # {
        #         "expected_result": "pass",
        #         "datapoints_source": {
        #             "test_variables": {
        #                 "o": {},
        #                 "m_oa": {},
        #                 "eco_onoff": {}
        #             },
        #             "parameters": {
        #                 "tol": 24.0
        #             }
        #         },
        #         "verification_class": "AutomaticOADamperControl"
        #     }
        #     """
        # case = json.loads(case_str)
        results = run_test_verification_with_data("AutomaticOADamperControl", df)
        print(results)
        self.assertEqual(results[0], False)


if __name__ == "__main__":
    unittest.main()

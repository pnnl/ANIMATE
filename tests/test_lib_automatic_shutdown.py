import unittest, sys

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestAutomaticShutdown(unittest.TestCase):
    def test_automatic_shutdown(self):
        points = ["hvac_set"]
        # data generation
        data_pass = np.zeros((48, 1))
        data_pass[5:17] = 1
        data_pass[32:45] = 1

        data_fail = np.zeros((48, 1))
        data_fail[5:17] = 1
        data_fail[29:41] = 1

        df_pass = pd.DataFrame(
            data_pass,
            columns=points,
            index=pd.date_range("2020", periods=len(data_pass), freq="H"),
        )

        df_fail = pd.DataFrame(
            data_fail,
            columns=points,
            index=pd.date_range("2020", periods=len(data_fail), freq="H"),
        )

        results = [
            run_test_verification_with_data("AutomaticShutdown", df_pass).get_checks[0],
            run_test_verification_with_data("AutomaticShutdown", df_fail).get_checks[0],
        ]
        expected_results = [True, False]

        # Perform verification
        for i in range(len(results)):
            self.assertTrue(results[i] is expected_results[i])

        # Print out results
        data = np.concatenate((df_pass, df_fail), axis=1)
        df = pd.DataFrame(data, columns=results)
        df.to_csv("./tests/outputs/TestAutomaticShutdown_test_automatic_shutdown.csv")


if __name__ == "__main__":
    unittest.main()

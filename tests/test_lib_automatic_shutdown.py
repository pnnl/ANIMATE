import unittest, sys

sys.path.append("../src")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestAutomaticShutdown(unittest.TestCase):
    def perform_automatic_shutdown_unit_test(self, interval, *data_input):
        point = ["hvac_set"]
        result = []
        for data in data_input:
            df = pd.DataFrame(
                data,
                columns=point,
                index=pd.date_range("2020", periods=len(data), freq=interval),
            )

            result.append(
                run_test_verification_with_data("AutomaticShutdown", df).get_checks[0]
            )

        return result

    def test_automatic_shutdown_hourly_interval(self):
        # data generation
        data_pass = np.zeros((48, 1))
        data_pass[5:17] = 1
        data_pass[32:45] = 1

        data_fail_all_ones = np.ones((48, 1))
        data_fail_all_zeros = np.zeros((48, 1))

        data_fail = np.zeros((48, 1))
        data_fail[5:17] = 1
        data_fail[29:41] = 1

        hourly_interval_results = self.perform_automatic_shutdown_unit_test(
            "H", data_pass, data_fail, data_fail_all_ones, data_fail_all_zeros
        )
        five_min_interval_results = self.perform_automatic_shutdown_unit_test(
            "5T", data_pass, data_fail
        )
        results = [*hourly_interval_results, *five_min_interval_results]
        expected_results = [True, False, False, False, True, False]

        # Perform verification
        for i in range(len(results)):
            self.assertTrue(results[i] is expected_results[i])

        # Print out results
        data = np.concatenate(
            (
                data_pass,
                data_fail,
                data_fail_all_ones,
                data_fail_all_zeros,
                data_pass,
                data_fail,
            ),
            axis=1,
        )
        df = pd.DataFrame(data, columns=results)
        df.to_csv("./tests/outputs/TestAutomaticShutdown_test_automatic_shutdown.csv")


if __name__ == "__main__":
    unittest.main()

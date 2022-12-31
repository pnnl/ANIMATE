import unittest, sys

sys.path.append("./src")
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
        data_pass_hourly = np.zeros((48, 1))
        data_pass_hourly[5:17] = 1
        data_pass_hourly[32:45] = 1

        data_fail_hourly = np.zeros((48, 1))
        data_fail_hourly[5:17] = 1
        data_fail_hourly[29:41] = 1

        data_fail_all_ones = np.ones((48, 1))
        data_fail_all_zeros = np.zeros((48, 1))

        data_pass_5_min = np.zeros((576, 1))
        data_pass_5_min[81:285] = 1
        data_pass_5_min[369:552] = 1

        data_fail_5_min = np.zeros((576, 1))
        data_fail_5_min[81:264] = 1
        data_fail_5_min[369:552] = 1

        hourly_interval_results = self.perform_automatic_shutdown_unit_test(
            "H",
            data_pass_hourly,
            data_fail_hourly,
            data_fail_all_ones,
            data_fail_all_zeros,
        )

        five_min_interval_results = self.perform_automatic_shutdown_unit_test(
            "5T", data_pass_5_min, data_fail_5_min
        )
        results = [*hourly_interval_results, *five_min_interval_results]
        expected_results = [True, False, False, False, True, False]

        # Perform verification
        for i in range(len(results)):
            self.assertTrue(results[i] is expected_results[i])

        # Print out results
        data1 = np.concatenate(
            (
                data_pass_hourly,
                data_fail_hourly,
                data_fail_all_ones,
                data_fail_all_zeros,
            ),
            axis=1,
        )
        data2 = np.concatenate(
            (
                data_pass_5_min,
                data_fail_5_min,
            ),
            axis=1,
        )
        df1 = pd.DataFrame(data1, columns=results[:4])
        df2 = pd.DataFrame(data2, columns=results[4:])
        # df1.to_csv("./tests/outputs/TestAutomaticShutdown_test_automatic_shutdown1.csv")
        # df2.to_csv("./tests/outputs/TestAutomaticShutdown_test_automatic_shutdown2.csv")


if __name__ == "__main__":
    unittest.main()

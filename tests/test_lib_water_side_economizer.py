import unittest, sys

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestWaterSideEconomizer(unittest.TestCase):
    def test_water_side_economizer(self):
        points = [
            "T_oa",
            "T_oa_wse_op",
            "P_mech_cool",
            "T_chw_s_sp",
            "T_chw_s",
            "T_chw_ret",
            "tol_sp",
        ]

        data = [
            [10, 50, 0, 44, 44, 54, 2],
            [60, 50, 0, 44, 44, 54, 2],
            [10, 50, 0, 44, 54, 54, 2],
            [60, 50, 0, 44, 54, 54, 2],
            [10, 50, 0, 44, 50, 54, 2],
            [10, 50, 10000, 44, 44, 54, 2],
            [60, 50, 10000, 44, 44, 54, 2],
            [10, 50, 10000, 44, 54, 54, 2],
            [60, 50, 10000, 44, 54, 54, 2],
            [10, 50, 10000, 44, 50, 54, 2],
        ]
        df = pd.DataFrame(data, columns=points)

        results = list(
            run_test_verification_with_data("WaterSideEconomizer", df).result
        )
        expected_results = [
            True,
            np.nan,
            np.nan,
            np.nan,
            False,
            False,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
        ]

        # Perform verification
        for i in range(len(data[0])):
            self.assertTrue(results[i] is expected_results[i])

        # Print out results
        df["results"] = results
        df["expected_results"] = expected_results
        df.to_csv(
            "./tests/outputs/TestWaterSideEconomizer_test_water_side_economizer.csv"
        )


if __name__ == "__main__":
    unittest.main()

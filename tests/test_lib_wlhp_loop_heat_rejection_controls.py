import unittest, sys

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestWLHPLoopHeatRejectionControl(unittest.TestCase):
    def test_wlhp_loop_heat_rejection_controls(self):
        points = ["T_loop", "m_pump", "tol"]

        data = [
            [[30, 1, 1], [10, 1, 1]],
            [[25, 1, 1], [20, 1, 1]],
        ]
        results = []
        for d in range(len(data)):
            df = pd.DataFrame(data[d], columns=points)

            results.append(
                bool(
                    run_test_verification_with_data(
                        "WLHPLoopHeatRejectionControl", df
                    ).result.values[0]
                )
            )

        expected_results = [
            True,
            False,
        ]

        # Perform verification
        for i in range(len(data[d])):
            self.assertTrue(results[i] is expected_results[i])

        # Print out results
        df["results"] = results
        df["expected_results"] = expected_results
        df.to_csv(
            "./tests/outputs/TestWLHPLoopHeatRejectionControl_test_wlhp_loop_heat_rejection_controls.csv"
        )


if __name__ == "__main__":
    unittest.main()

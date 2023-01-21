import unittest, sys

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestHeatRejectionFanVariableFlowControlsCells(unittest.TestCase):
    def test_lib_heat_rejection_fan_var_flow_controls_cells(self):
        points = [
            "ct_op_cells",
            "ct_cells",
            "m",
            "P_fan_ct",
            "m_des",
            "min_flow_frac_per_cell",
        ]

        data = [
            [[1, 4, 0.001, 5000, 0.004, 1.0]],
            [[1, 4, 0.001, 5000, 0.004, 0.250]],
        ]

        results = []
        df_agg = pd.DataFrame()
        for d in range(len(data)):
            df = pd.DataFrame(data[d], columns=points)
            df_agg = pd.concat([df_agg, df])
            results.append(
                run_test_verification_with_data(
                    "HeatRejectionFanVariableFlowControlsCells", df
                ).result.values[0]
            )

        expected_results = [True, False]
        # Perform verification
        for i in range(len(results)):
            self.assertTrue(bool(results[i]) is expected_results[i])

        # Print out results
        df_agg["results"] = results
        df_agg["expected_results"] = expected_results
        df_agg.to_csv(
            "./tests/outputs/TestHeatRejectionFanVariableFlowControlsCells_test_lib_heat_rejection_fan_var_flow_controls_cells.csv"
        )


if __name__ == "__main__":
    unittest.main()

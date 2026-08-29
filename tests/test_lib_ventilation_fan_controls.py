import unittest, sys

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import pandas as pd


class TestVentilationFanControls(unittest.TestCase):
    def test_ventilation_fan_controls(self):
        points = ["Q_load_req", "fan_onoff", "P_fan"]
        data = [
            [0, 0, 0],
            [0, 0, 200],
            [0, 1, 0],
            [0, 1, 250],
            [1, 0, 0],
            [1, 0, 300],
            [1, 1, 0],
            [1, 1, 450],
        ]
        df = pd.DataFrame(data, columns=points)

        results = list(
            run_test_verification_with_data("VentilationFanControl", df).result
        )
        expected_results = [True, False, True, True, True, True, True, True]

        # Perform verification
        for i in range(len(data[0])):
            self.assertTrue(results[i] is expected_results[i])

        # Print out results
        df["results"] = results
        df["expected_results"] = expected_results
        df.to_csv(
            "./tests/outputs/TestVentilationFanControls_test_ventilation_fan_controls.csv"
        )


if __name__ == "__main__":
    unittest.main()

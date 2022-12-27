import unittest, sys

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import pandas as pd


class TestServiceWaterHeatingSystemControl(unittest.TestCase):
    def test_service_water_heating_system_control(self):
        points = ["T_wh_inlet", "tol_temp"]
        data = [[30, 0.5], [50, 0.5]]
        df = pd.DataFrame(data, columns=points)

        results = list(
            run_test_verification_with_data(
                "SWHRestroomOutletMaximumTemperatureControls", df
            ).result
        )
        expected_results = [True, False]

        # Perform verification
        for i in range(len(data[0])):
            self.assertTrue(results[i] is expected_results[i])

        # Print out results
        df["results"] = results
        df["expected_results"] = expected_results
        df.to_csv(
            "./tests/outputs/TestServiceWaterHeatingSystemControl_test_swh_restroom_outlet_maximum_temperature_controls.csv"
        )


if __name__ == "__main__":
    unittest.main()

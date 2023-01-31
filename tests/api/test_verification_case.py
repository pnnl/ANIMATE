import unittest, sys, os

sys.path.append("./src")
from api import VerificationCase


class TestDataProcessing(unittest.TestCase):
    def test_constructor(self):

        # test both `case` and `file_path` args aren't provided.
        vc = VerificationCase(case=None, file_path=None)
        assert vc.case_suite == {}

        # test when the wrong case arg provided.
        with self.assertLogs() as logobs:
            testing_case = [
                {
                    "cases": {
                        "no": 1,
                        "run_simulation": True,
                        "simulation_IO": {
                            "idf": "../test_cases/doe_prototype_cases/ASHRAE901_Hospital_STD2019_Atlanta_Case1.idf",
                            "idd": "../resources/Energy+V9_0_1.idd",
                            "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                            "output": "eplusout.csv",
                            "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
                        },
                        "expected_result": "pass",
                        "datapoints_source": {
                            "idf_output_variables": {
                                "T_sa_set": {
                                    "subject": "VAV_1 Supply Equipment Outlet Node",
                                    "variable": "System Node Setpoint Temperature",
                                    "frequency": "detailed",
                                }
                            },
                            "parameters": {},
                        },
                        "verification_class": "Testing",
                    }
                }
            ]  # wrong data type
            vc = VerificationCase(case=testing_case, file_path=None)
            self.assertEqual(
                "ERROR:root:The type of the 'case' argument has to be str, but <class "
                "'list'> type is provided. Please verify the 'case' argument.",
                logobs.output[0],
            )

        # test when the wrong file_path type is provided.
        with self.assertLogs() as logobs:
            file_path = ["wrong_file_path_type.json"]
            vc = VerificationCase(case=None, file_path=file_path)
            self.assertEqual(
                "ERROR:root:The type of the 'file_path' argument has to be str, but <class "
                "'list'> type is provided. Please verify the 'file_path' argument.",
                logobs.output[0],
            )

        # test when the json file doesn't exist.
        with self.assertLogs() as logobs:
            file_path = "./not_existing_path/testing.json"
            vc = VerificationCase(case=None, file_path=file_path)
            self.assertEqual(
                "ERROR:root:file_path: './not_existing_path/testing.json' doesn't exist. Please make sure if the provided path exists.",
                logobs.output[0],
            )

        # test when the given directory doesn't exist.
        with self.assertLogs() as logobs:
            file_path = "./not_existing_path"
            vc = VerificationCase(case=None, file_path=file_path)
            self.assertEqual(
                "ERROR:root:The provided directory doesn't exist. Please make sure to provide a correct file_path.",
                logobs.output[0],
            )

    def test_load_verification_cases_from_json_wrong_input_type(self):
        # test when the wrong file_path type is provided
        with self.assertLogs() as logobs:
            vc = VerificationCase(case=None, file_path=None)
            vc.load_verification_cases_from_json(["wrong_file_path_type.json"])
            self.assertEqual(
                "ERROR:root:The type of the 'json_case_path' argument has to be str, but <class "
                "'list'> type is provided. Please verify the 'json_case_path' argument.",
                logobs.output[0],
            )

    def test_load_verification_cases_from_json_correct_hash_len(self):
        # test whether the length of returned hash is correct
        json_case_path = "./data/verification_case_unit_test.json"
        vc1 = VerificationCase(case=None, file_path=None)
        list_of_hash = vc1.load_verification_cases_from_json(json_case_path)
        self.assertEqual(len(list_of_hash), 2)


if __name__ == "__main__":
    unittest.main()

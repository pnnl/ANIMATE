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
        json_case_path = "./tests/api/data/verification_case_unit_test.json"
        vc = VerificationCase(case=None, file_path=None)
        list_of_hash = vc.load_verification_cases_from_json(json_case_path)
        assert len(list_of_hash) == 2

    def test_save_case_suite_to_json_wrong_json_path_type(self):
        # test when not existing dir is provided
        with self.assertLogs() as logobs:
            vc = VerificationCase(
                case=None, file_path="./tests/api/data/verification_case_unit_test.json"
            )
            vc.save_case_suite_to_json(["./not_existing_dir/testing.json"])
            self.assertEqual(
                "ERROR:root:The type of the 'json_path' argument has to be str, but <class "
                "'list'> type is provided. Please verify the 'json_path' argument.",
                logobs.output[0],
            )

    def test_save_case_suite_to_json_not_existing_dir_in_json_path(self):
        # test when not existing dir is provided
        with self.assertLogs() as logobs:
            vc = VerificationCase(
                case=None, file_path="./tests/api/data/verification_case_unit_test.json"
            )
            vc.save_case_suite_to_json("./not_existing_dir/testing.json", case_ids={})
            self.assertEqual(
                "ERROR:root:The type of the 'case_ids' argument has to be str, but <class "
                "'dict'> type is provided. Please verify the 'case_ids' argument.",
                logobs.output[0],
            )

    def test_save_case_suite_to_json_correct_json_path(self):
        # test when just file name (without including dir) is provided
        vc = VerificationCase(
            case=None, file_path="./tests/api/data/verification_case_unit_test.json"
        )
        file_path = "./tests/api/result/from_test_save_case_suite_to_json_correct_json_path.json"
        vc.save_case_suite_to_json(file_path)
        assert os.path.isfile(file_path)

    def test_save_case_suite_to_json_check_file_saving(self):
        # test the given case is saved correctly.
        case_dict = {
            "cases": [
                {
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
            ]
        }
        saving_file_path = "./tests/api/result/from_test_save_case_suite_to_json_check_file_saving.json"
        vc = VerificationCase(
            case=None, file_path="./tests/api/data/verification_case_unit_test.json"
        )
        vc.save_case_suite_to_json(saving_file_path)
        assert os.path.isfile(saving_file_path)

    def test_validate_verification_case_structure_wrong_input_type(self):
        # test when wrong case type is provided.
        with self.assertLogs() as logobs:
            case = []
            VerificationCase(
                case=None, file_path=None
            ).validate_verification_case_structure(case)
            self.assertEqual(
                "ERROR:root:The case argument type must be dict, but <class 'list'> is provided.",
                logobs.output[0],
            )

        # test when wrong verbose type is provided.
        with self.assertLogs() as logobs:
            case = {}
            verbose = "pass"
            VerificationCase(
                case=None, file_path=None
            ).validate_verification_case_structure(case, verbose)
            self.assertEqual(
                "ERROR:root:The verbose argument type must be bool, but <class 'str'> is provided.",
                logobs.output[0],
            )

    def test_validate_verification_case_structure_wrong_case(self):
        # test when `run_simulation` key is wrong
        case_wrong_run_simulation = {
            "no": 1,
            "run_simulation": "PASS",  # supposed to be True
            "simulation_IO": {
                "idf": "../test_cases/doe_prototype_cases/ASHRAE901_Hospital_STD2004_Atlanta_Case2.idf",
                "idd": "../resources/Energy+V9_0_1.idd",
                "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                "output": "eplusout.csv",
                "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
            },
            "expected_result": "fail",
            "datapoints_source": {
                "idf_output_variables": {
                    "T_sa_set": {
                        "subject": "VAV_1 Supply Equipment Outlet Node",
                        "variable": "System Node Setpoint Temperature",
                        "frequency": "detailed",
                    }
                },
                "parameters": {"T_z_coo": 24.0},
            },
            "verification_class": "SupplyAirTempReset",
        }

        assert (
            VerificationCase(
                case=None, file_path=None
            ).validate_verification_case_structure(case_wrong_run_simulation)
            == False
        )

        # test when 'subject' key is missing
        case_missing_subject = {
            "no": 1,
            "run_simulation": True,
            "simulation_IO": {
                "idf": "../test_cases/doe_prototype_cases/ASHRAE901_Hospital_STD2004_Atlanta_Case2.idf",
                "idd": "../resources/Energy+V9_0_1.idd",
                "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                "output": "eplusout.csv",
                "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
            },
            "expected_result": "fail",
            "datapoints_source": {
                "idf_output_variables": {
                    "T_sa_set": {
                        # intentionally missed subject key
                        "variable": "System Node Setpoint Temperature",
                        "frequency": "detailed",
                    }
                },
                "parameters": {"T_z_coo": 24.0},
            },
            "verification_class": "SupplyAirTempReset",
        }

        assert (
            VerificationCase(
                case=None, file_path=None
            ).validate_verification_case_structure(case_missing_subject)
            == False
        )

        # test when `verification_class` is wrong
        case_missing_verification_class = {
            "no": 2,
            "run_simulation": True,
            "simulation_IO": {
                "idf": "../test_cases/doe_prototype_cases/ASHRAE901_Hospital_STD2004_Atlanta_Case2.idf",
                "idd": "../resources/Energy+V9_0_1.idd",
                "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                "output": "eplusout.csv",
                "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
            },
            "expected_result": "fail",
            "datapoints_source": {
                "idf_output_variables": {
                    "T_sa_set": {
                        "subject": "VAV_1 Supply Equipment Outlet Node",
                        "variable": "System Node Setpoint Temperature",
                        "frequency": "detailed",
                    }
                },
                "parameters": {"T_z_coo": 24.0},
            },
            "verification_class": [
                "SupplyAirTempReset"
            ],  # intentionally put list instead of str
        }

        assert (
            VerificationCase(
                case=None, file_path=None
            ).validate_verification_case_structure(case_missing_verification_class)
            == False
        )

    def test_save_verification_cases_to_json(self):
        example_cases = [
            {
                "no": 1,
                "run_simulation": True,
                "simulation_IO": {
                    "idf": "../test_cases/doe_prototype_cases/ASHRAE901_Hospital_STD2004_Atlanta_Case2.idf",
                    "idd": "../resources/Energy+V9_0_1.idd",
                    "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                    "output": "eplusout.csv",
                    "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
                },
                "expected_result": "fail",
                "datapoints_source": {
                    "idf_output_variables": {
                        "T_sa_set": {
                            "subject": "VAV_1 Supply Equipment Outlet Node",
                            "variable": "System Node Setpoint Temperature",
                            "frequency": "detailed",
                        }
                    },
                    "parameters": {"T_z_coo": 24.0},
                },
                "verification_class": "SupplyAirTempReset",
            }
        ]
        json_path = "./tests/api/result/wrong_json_path.json"

        # when wrong json_path type is provided
        with self.assertLogs() as logobs:
            wrong_json_path = ["./tests/api/resultwrong_json_path.json"]
            VerificationCase(case=None, file_path=None).save_verification_cases_to_json(
                wrong_json_path, example_cases
            )
            self.assertEqual(
                "ERROR:root:The json_path argument type must be str, but <class 'list'> is provided.",
                logobs.output[0],
            )

        # when wrong cases type is provided
        with self.assertLogs() as logobs:
            wrong_cases_type = {
                "no": 1,
                "run_simulation": True,
                "simulation_IO": {
                    "idf": "../test_cases/doe_prototype_cases/ASHRAE901_Hospital_STD2004_Atlanta_Case2.idf",
                    "idd": "../resources/Energy+V9_0_1.idd",
                    "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                    "output": "eplusout.csv",
                    "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
                },
                "expected_result": "fail",
                "datapoints_source": {
                    "idf_output_variables": {
                        "T_sa_set": {
                            "subject": "VAV_1 Supply Equipment Outlet Node",
                            "variable": "System Node Setpoint Temperature",
                            "frequency": "detailed",
                        }
                    },
                    "parameters": {"T_z_coo": 24.0},
                },
                "verification_class": "SupplyAirTempReset",
            }
            VerificationCase(case=None, file_path=None).save_verification_cases_to_json(
                json_path, wrong_cases_type
            )
            self.assertEqual(
                "ERROR:root:The cases argument type must be list, but <class 'dict'> is provided.",
                logobs.output[0],
            )

        # when wrong json_path extension is provided
        with self.assertLogs() as logobs:
            wrong_json_path = "./tests/api/result/wrong_json_path.csv"
            VerificationCase(case=None, file_path=None).save_verification_cases_to_json(
                wrong_json_path, example_cases
            )
            self.assertEqual(
                "ERROR:root:The json_path argument must end with '.json' extension.",
                logobs.output[0],
            )

        # test if json is saved correctly
        VerificationCase(case=None, file_path=None).save_verification_cases_to_json(
            json_path, example_cases
        )
        assert os.path.isfile(json_path)


if __name__ == "__main__":
    unittest.main()

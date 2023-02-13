import unittest, sys, os, copy


sys.path.append("./src")

from api import VerificationCase


class TestDataProcessing(unittest.TestCase):
    def test_constructor(self):
        # test both `case` and `file_path` args are `None `
        vc = VerificationCase(case=None, file_path=None)
        assert vc.case_suite == {}

        # test when only correct `case` is provided
        case = {
            "no": 3,
            "run_simulation": True,
            "simulation_IO": {
                "idf": "../test_cases/doe_prototype_cases/ASHRAE901_Hospital_STD2019_Atlanta_Case3.idf",
                "idd": "../resources/Energy+V9_0_1.idd",
                "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                "output": "eplusout.csv",
                "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
            },
            "expected_result": "pass",
            "datapoints_source": {
                "idf_output_variables": {
                    "T_sa_set": {
                        "subject": "VAV_2 Supply Equipment Outlet Node",
                        "variable": "System Node Setpoint Temperature",
                        "frequency": "detailed",
                    }
                },
                "parameters": {"T_z_coo": 24.0},
            },
            "verification_class": "SupplyAirTempReset",
        }
        case_original = copy.deepcopy(case)
        vc = VerificationCase(case=case, file_path=None)
        vs_case_suite = copy.deepcopy(vc.case_suite.popitem()[1])
        del vs_case_suite[
            "case_id_in_suite"
        ]  # delete `case_id_in_suite` key b/c random unique id's assigned
        assert vs_case_suite == case_original

        # test when the wrong `case` arg is provided
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
                "ERROR:root:The `case` argument's type must be typing.Dict, but <class 'list'> is provided.",
                logobs.output[0],
            )

        # test when the correct `file_path` is provided
        file_path = "./tests/api/data/verification_case_unit_test.json"
        vc = VerificationCase(case=None, file_path=file_path)
        assert len(vc.case_suite) == 2

        # test when the `file_path` doesn't exist
        with self.assertLogs() as logobs:
            file_path = "./not_existing_path/testing.json"
            vc = VerificationCase(case=None, file_path=file_path)
            self.assertEqual(
                f"ERROR:root:`./not_existing_path/testing.json' doesn't exist. Please make sure that the 'file_path' argument is correct.",
                logobs.output[0],
            )

        # # test when the wrong `file_path` type is provided
        with self.assertLogs() as logobs:
            file_path = ["wrong_file_path_type.json"]
            vc = VerificationCase(case=None, file_path=file_path)
            self.assertEqual(
                "ERROR:root:The `file_path` argument's type must be <class 'str'>, but <class "
                "'list'> is provided.",
                logobs.output[0],
            )

        # # test when the given directory doesn't exist
        with self.assertLogs() as logobs:
            file_path = "./not_existing_path"
            vc = VerificationCase(case=None, file_path=file_path)
            self.assertEqual(
                "ERROR:root:The provided directory doesn't exist. Please make sure to provide a correct file_path.",
                logobs.output[0],
            )

    def test_load_verification_cases_from_json(self):
        # test when the wrong file_path type is provided
        with self.assertLogs() as logobs:
            vc = VerificationCase(case=None, file_path=None)
            vc.load_verification_cases_from_json(["wrong_file_path_type.json"])
            self.assertEqual(
                "ERROR:root:The `json_case_path` argument's type must be <class 'str'>, but <class "
                "'list'> is provided.",
                logobs.output[0],
            )

        # test whether the length of returned hash is correct
        json_case_path = "./tests/api/data/verification_case_unit_test.json"
        vc = VerificationCase(case=None, file_path=None)
        list_of_hash = vc.load_verification_cases_from_json(json_case_path)
        assert len(list_of_hash) == 2

    def test_save_case_suite_to_json(self):
        # test when `json_path` doesn't exist
        with self.assertLogs() as logobs:
            vc = VerificationCase(
                case=None,
                file_path="./tests/api//data/verification_case_unit_test.json",
            )
            vc.save_case_suite_to_json(["./not_existing_dir/testing.json"])
            self.assertEqual(
                "ERROR:root:The `json_path` argument's type must be <class 'str'>, but <class "
                "'list'> is provided.",
                logobs.output[0],
            )

        # test when wrong `case_ids` type is provided
        with self.assertLogs() as logobs:
            vc = VerificationCase(
                case=None, file_path="./tests/api/data/verification_case_unit_test.json"
            )
            vc.save_case_suite_to_json(
                json_path="./testing.json", case_ids="this is wrong case_ids type"
            )
            self.assertEqual(
                "ERROR:root:The `case_ids` argument's type must be typing.List, but <class "
                "'str'> is provided.",
                logobs.output[0],
            )

        # test the given case is saved correctly.
        saving_file_path = "./tests/api//result/from_test_save_case_suite_to_json_check_file_saving.json"
        vc = VerificationCase(
            case=None, file_path="./tests/api/data/verification_case_unit_test.json"
        )
        vc.save_case_suite_to_json(saving_file_path)
        assert os.path.isfile(saving_file_path)
        os.remove(saving_file_path)

    def test_create_verificaton_case_suite_from_base_case(self):
        example_base_case = {
            "no": 1,
            "run_simulation": True,
            "simulation_IO": {
                "idf": "../testing.idf",
                "idd": "../Energy+V9_0_1.idd",
                "weather": "./USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                "output": "eplusout.csv",
                "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
            },
            "expected_result": "fail",
            "datapoints_source": {
                "idf_output_variables": {
                    "oa_flow": {
                        "subject": "VAV_1_OAInlet Node",
                        "variable": "System Node Standard Density Volume Flow Rate",
                        "frequency": "TimeStep",
                    },
                    "oa_db": {
                        "subject": "Environment",
                        "variable": "Site Outdoor Air Drybulb Temperature",
                        "frequency": "TimeStep",
                    },
                },
                "parameters": {"oa_threshold": 300},
            },
            "verification_class": "Testing",
        }
        update_key_value = {
            "simulation_IO": {
                "idf": ["Testing_file1.idf", "Testing_file2.idf"],
            },
            "datapoints_source": {
                "idf_output_variables": {
                    "oa_flow": {
                        "subject": ["VAV_1_OAInlet Node", "VAV_2_OAInlet Node"],
                        "variable": [
                            "System Node Standard Density Volume Flow Rate",
                            "Current Density Volume",
                        ],
                    },
                    "oa_db": {
                        "variable": [
                            "Site Outdoor Air Drybulb Temperature",
                            "Site Outdoor Air Relative Humidity",
                        ],
                    },
                },
                "parameters": {"oa_threshold": [999, 1000]},
            },
        }

        # test when correct `base_case` and `update_key_value` are provided
        returned_updated_base_cases_list = VerificationCase(
            case=None, file_path=None
        ).create_verificaton_case_suite_from_base_case(
            example_base_case, update_key_value, keep_base_case=True
        )
        assert len(returned_updated_base_cases_list) == 3

        # test when wrong `base_case` type is provided.
        with self.assertLogs() as logobs:
            wrong_base_case_type = [{"wrong_base_case_type_key": "testing"}]
            VerificationCase(
                case=None, file_path=None
            ).create_verificaton_case_suite_from_base_case(
                wrong_base_case_type, update_key_value, keep_base_case=False
            )
            self.assertEqual(
                "ERROR:root:The `base_case` argument type must be Dict, but <class 'list'> type is provided.",
                logobs.output[0],
            )

        # test when wrong `update_key_value` type is provided.
        with self.assertLogs() as logobs:
            wrong_update_key_value_type = [{"wrong_update_key_type_key": "testing"}]
            VerificationCase(
                case=None, file_path=None
            ).create_verificaton_case_suite_from_base_case(
                example_base_case, wrong_update_key_value_type, keep_base_case=False
            )
            self.assertEqual(
                "ERROR:root:The `update_key_value` argument type must be Dict, but <class 'list'> type is provided.",
                logobs.output[0],
            )

        # test when wrong `keep_base_case` type is provided.
        with self.assertLogs() as logobs:
            VerificationCase(
                case=None, file_path=None
            ).create_verificaton_case_suite_from_base_case(
                example_base_case, update_key_value, keep_base_case="Fail"
            )
            self.assertEqual(
                "ERROR:root:The `keep_base_case` argument must be bool, but <class 'str'> type is provided.",
                logobs.output[0],
            )

        # test when lengths of modifying lists are different.
        with self.assertLogs() as logobs:
            wrong_update_key_value = {
                "simulation_IO": {
                    "idf": ["Testing_file1.idf", "Testing_file2.idf"],  # length: 2
                },
                "datapoints_source": {
                    "idf_output_variables": {
                        "oa_flow": {
                            "subject": ["VAV_1_OAInlet Node", "VAV_2_OAInlet Node"],
                            "variable": [
                                "System Node Standard Density Volume Flow Rate",
                                "Current Density Volume",
                            ],
                        },
                        "oa_db": {
                            "variable": [
                                "Site Outdoor Air Drybulb Temperature",
                                "Site Outdoor Air Relative Humidity",
                            ],
                        },
                    },
                    "parameters": {
                        "oa_threshold": [999, 1000, 1200]
                    },  # length: 3 --> The list lengths are different.
                },
            }

            VerificationCase(
                case=None, file_path=None
            ).create_verificaton_case_suite_from_base_case(
                example_base_case, wrong_update_key_value, keep_base_case=False
            )
            self.assertEqual(
                "ERROR:root:The length of modifying values in lists must be the same.",
                logobs.output[0],
            )

    def test_validate_verification_case_structure(self):
        # test when correct `case` arg is provided
        vc = VerificationCase(case=None, file_path=None)
        correct_case = {
            "no": 4,
            "run_simulation": True,
            "simulation_IO": {
                "idf": "../test_cases/doe_prototype_cases/ASHRAE901_Hospital_STD2004_Atlanta_Case4.idf",
                "idd": "../resources/Energy+V9_0_1.idd",
                "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                "output": "eplusout.csv",
                "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
            },
            "expected_result": "fail",
            "datapoints_source": {
                "idf_output_variables": {
                    "T_sa_set": {
                        "subject": "VAV_2 Supply Equipment Outlet Node",
                        "variable": "System Node Setpoint Temperature",
                        "frequency": "detailed",
                    }
                },
                "parameters": {"T_z_coo": 24.0},
            },
            "verification_class": "SupplyAirTempReset",
        }
        assert vc.validate_verification_case_structure(correct_case)

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

        # test when `run_simulation` key is wrong
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
            wrong_json_path = ["./wrong_json_path.json"]
            VerificationCase(case=None, file_path=None).save_verification_cases_to_json(
                wrong_json_path, example_cases
            )
            self.assertEqual(
                "ERROR:root:The `json_path` argument type must be str, but <class 'list'> is provided.",
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
                "ERROR:root:The `cases` argument type must be list, but <class 'dict'> is provided.",
                logobs.output[0],
            )

        # when wrong json_path extension is provided
        with self.assertLogs() as logobs:
            wrong_json_path = "./wrong_json_path.csv"
            VerificationCase(case=None, file_path=None).save_verification_cases_to_json(
                wrong_json_path, example_cases
            )
            self.assertEqual(
                "ERROR:root:The `json_path` argument must end with '.json' extension.",
                logobs.output[0],
            )

        # test when correct `json_path` and `cases` arguments are provided
        VerificationCase(case=None, file_path=None).save_verification_cases_to_json(
            json_path, example_cases
        )
        assert os.path.isfile(json_path)
        os.remove(json_path)


if __name__ == "__main__":
    unittest.main()

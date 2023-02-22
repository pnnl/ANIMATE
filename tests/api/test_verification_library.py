import unittest, sys, logging, json

sys.path.append("./src")
from api import VerificationLibrary

lib_path = "./schema/library.json"


class TestVerificationLibrary(unittest.TestCase):
    def test_constructor_empty(self):
        with self.assertLogs() as logobs:
            vl_obj = VerificationLibrary()
            self.assertEqual(
                "ERROR:root:'lib_path' was not provided when instantiating the Verificationlibrary class object!",
                logobs.output[0],
            )

    def test_constructor_nonstr(self):
        with self.assertLogs() as logobs:
            vl_obj = VerificationLibrary(123)
            self.assertEqual(
                f"ERROR:root:lib_path needs to be str of library file or foler path. It cannot be a {type(123)}",
                logobs.output[0],
            )

    def test_constructor_load_json(self):
        with open(lib_path) as f:
            exp_items = json.load(f)

        self.assertTrue(len(exp_items) >= 2)

        vl_obj = VerificationLibrary(lib_path)
        self.assertEqual(len(vl_obj.lib_items), len(exp_items))
        self.assertEqual(len(vl_obj.lib_items_json_path), len(exp_items))
        self.assertEqual(len(vl_obj.lib_items_python_path), len(exp_items))

    def test_get_library_item(self):
        vl_obj = VerificationLibrary(lib_path)

        item = vl_obj.get_library_item("AutomaticShutdown")
        self.assertEqual(item["library_item_name"], "AutomaticShutdown")
        self.assertTrue(isinstance(item["library_definition"], dict))
        self.assertEqual(item["library_python_path"].split(".")[-1], "py")
        self.assertEqual(item["library_json_path"].split(".")[-1], "json")

    def test_get_library_item_invalid(self):
        vl_obj = VerificationLibrary(lib_path)

        with self.assertLogs() as logobs:
            item = vl_obj.get_library_item("NonExistLibItem")
            self.assertEqual(
                "ERROR:root:NonExistLibItem is not in loaded library items.",
                logobs.output[0],
            )

    def test_get_required_datapoints_by_library_items(self):
        vl_obj = VerificationLibrary(lib_path)

        req_datapoints_by_lib_items = vl_obj.get_required_datapoints_by_library_items(
            ["T_sa_set", "oa_threshold"]
        )
        assert req_datapoints_by_lib_items == {
            "T_sa_set": {
                "number_of_items_using_this_datapoint": 1,
                "library_items_list": ["SupplyAirTempReset"],
            },
            "oa_threshold": {
                "number_of_items_using_this_datapoint": 3,
                "library_items_list": [
                    "EconomizerHighLimitA",
                    "EconomizerHighLimitC",
                    "EconomizerHighLimitD",
                ],
            },
        }

    def test_get_required_datapoints_by_library_items_invalid(self):
        vl_obj = VerificationLibrary(lib_path)

        with self.assertLogs() as logobs:
            vl_obj.get_required_datapoints_by_library_items(
                {"T_sa_set", "oa_threshold"}  # wrong datapoints type
            )
            self.assertEqual(
                f"ERROR:root:The `datapoints` argument type must be List, but {type({'T_sa_set', 'oa_threshold'})} type is provided.",
                logobs.output[0],
            )


if __name__ == "__main__":
    unittest.main()

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

    def test_get_applicable_library_items_by_datapoints(self):
        vl_obj = VerificationLibrary(lib_path)
        applicable_lib_items = vl_obj.get_applicable_library_items_by_datapoints(
            ["T_sa_set", "T_z_coo", "v_oa", "s_ahu", "s_eco", "no_of_occ"]
        )  # datapoints for `SupplyAirTempReset` and `DemandControlVentilation`
        self.assertEqual(
            applicable_lib_items["SupplyAirTempReset"],
            list(
                vl_obj.lib_items["SupplyAirTempReset"]["description_datapoints"].keys()
            ),
        )
        self.assertEqual(
            applicable_lib_items["DemandControlVentilation"],
            list(
                vl_obj.lib_items["DemandControlVentilation"][
                    "description_datapoints"
                ].keys()
            ),
        )

    def test_get_applicable_library_items_by_datapoints_invalid_datapoints(self):
        vl_obj = VerificationLibrary(lib_path)

        with self.assertLogs() as logobs:
            vl_obj.get_applicable_library_items_by_datapoints({"T_sa_set", "T_z_coo"})
            self.assertEqual(
                "ERROR:root:datapoints' type must be List. It can't be <class 'set'>.",
                logobs.output[0],
            )

        with self.assertLogs() as logobs:
            vl_obj.get_applicable_library_items_by_datapoints([])
            self.assertEqual(
                "ERROR:root:`datapoints' is an empty list. Please provide with datapoint names.",
                logobs.output[0],
            )

        with self.assertLogs() as logobs:
            vl_obj.get_applicable_library_items_by_datapoints(["T_sa_set", {"T_z_coo"}])
            self.assertEqual(
                "ERROR:root:element's type in the datapoints argument must be str. It can't be <class 'set'>.",
                logobs.output[0],
            )

    def test_get_library_items(self):
        vl_obj = VerificationLibrary(lib_path)

        items = vl_obj.get_library_items(
            ["AutomaticShutdown", "DemandControlVentilation"]
        )
        self.assertEqual(items[0]["library_item_name"], "AutomaticShutdown")
        self.assertTrue(isinstance(items[0]["library_definition"], dict))
        self.assertEqual(items[0]["library_python_path"].split(".")[-1], "py")
        self.assertEqual(items[0]["library_json_path"].split(".")[-1], "json")

        self.assertEqual(items[1]["library_item_name"], "DemandControlVentilation")
        self.assertTrue(isinstance(items[1]["library_definition"], dict))
        self.assertEqual(items[1]["library_python_path"].split(".")[-1], "py")
        self.assertEqual(items[1]["library_json_path"].split(".")[-1], "json")

    def test_get_library_items_invalid(self):
        vl_obj = VerificationLibrary(lib_path)

        # check `items` arg type
        with self.assertLogs() as logobs:
            vl_obj.get_library_items({"AutomaticShutdown"})  # wrong items type
            self.assertEqual(
                "ERROR:root:items' type must be List. It can't be <class 'set'>.",
                logobs.output[0],
            )

        # check when `items` is empty
        with self.assertLogs() as logobs:
            vl_obj.get_library_items([])  # wrong items type
            self.assertEqual(
                "ERROR:root:items' arg is empty. Please provide with verification item(s).",
                logobs.output[0],
            )


if __name__ == "__main__":
    unittest.main()

import unittest, sys, datetime

sys.path.append("./src")

from api import DataProcessing


class TestDataProcessing(unittest.TestCase):
    def test_constructor_empty(self):
        with self.assertLogs() as logobs:
            dp = DataProcessing()
            self.assertEqual(
                "ERROR:root:A `data_path` argument should be provided.",
                logobs.output[0],
            )
            self.assertEqual(
                "ERROR:root:A `data_source` argument should be provided.",
                logobs.output[1],
            )

    def test_missing_datafile(self):
        with self.assertLogs() as logobs:
            filep = "./data/missing_file.csv"
            dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
            self.assertEqual(
                f"ERROR:root:The file {filep} does not exists.", logobs.output[0]
            )

    def test_missing_datafile_error(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_err.csv"
            dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
            self.assertEqual(
                f"ERROR:root:An error occured when opening {filep}. Please make sure that the file can be opened, and/or that it contains the correct headers.",
                logobs.output[0],
            )

    def test_data_file(self):
        filep = "./tests/api/data/data_eplus.csv"
        t = DataProcessing(data_path=filep, data_source="EnergyPlus")
        assert len(t.data) == 2

    def test_datafile_error_parsing(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_err_parse.csv"
            dp = DataProcessing(
                data_path=filep, data_source="Other", timestamp_column_name="Date/Time"
            )
            self.assertEqual(
                f"ERROR:root:The data in Date/Time could not be converted to Python datetime object. Make sure that the data is consistent defined as a set of date strings.",
                logobs.output[0],
            )

    def test_slice_add_parameter(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_complete.csv"
            dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
            dp.slice("2000-01-01 11:00", "2000-01-01 11:00")
            self.assertEqual(
                f"ERROR:root:The start_time argument is not a Python datetime object.",
                logobs.output[0],
            )
            dp.slice(datetime.datetime(2000, 1, 1, 11), "2000-01-01 11:00")
            self.assertEqual(
                f"ERROR:root:The end_time argument is not a Python datetime object.",
                logobs.output[1],
            )
            dp.add_parameter()
            self.assertEqual(
                f"ERROR:root:A parameter name should be specified.",
                logobs.output[2],
            )
            dp.add_parameter(name="test")
            self.assertEqual(
                f"ERROR:root:A parameter value should be specified.",
                logobs.output[3],
            )
        assert "test" in list(dp.add_parameter(name="test", value=-999).columns)
        dp.add_parameter(name="test", value=-999, inplace=True)
        assert "test" in list(dp.data.columns)
        s = dp.slice(
            datetime.datetime(2000, 1, 1, 11), datetime.datetime(2000, 1, 1, 13)
        )
        assert len(s) == 3
        dp.slice(
            datetime.datetime(2000, 1, 1, 12),
            datetime.datetime(2000, 1, 1, 13),
            inplace=True,
        )
        assert len(dp.data) == 2

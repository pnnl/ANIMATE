from unittest import TestCase

import src, os, sys, re
from src.libcases import assemble_verification_items
from src.libcases import run_libcase
import matplotlib.pyplot as plt


class TestCHWReset(TestCase):
    def test_chwreset(self):
        # Initialize verification
        cpath = os.getcwd()
        items = assemble_verification_items(
            cases_path=cpath + "/tests/test_chwreset.json",
            lib_items_path=cpath + "/schema/library.json",
        )

        # Run verification using a dataset with CHW reset
        item = items[0]
        run_libcase(item, plot_option=None)

        # Check expected outcome
        out = sys.stdout.getvalue()
        res = re.findall("Verification Passed(.*.)}", out)
        self.assertTrue(
            "True" in res[0],
            "The chilled water reset verification rule should have correctly identified a reset.",
        )

        # Run verification using a dataset without CHW reset
        item = items[1]
        run_libcase(item, plot_option=None)

        # Check expected outcome
        out = sys.stdout.getvalue()
        res = re.findall("Verification Passed(.*.)}", out)
        self.assertTrue(
            "False" in res[1],
            f"The chilled water reset verification rule should have NOT identified a reset.",
        )

# %% Import packages
import datetime
from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from src.checklib import CheckLibBase, RuleCheckBase


class ZoneCoolingSetpointMaximum(CheckLibBase):
    points = ["T_cool_set"]

    def verify(self):
        self.result = self.df["T_cool_set"] >= 32.22

    def check_bool(self) -> bool:
        if len(self.result[self.result == True] > 0):
            return True
        else:
            return False

    def check_detail(self) -> Dict:
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
        }

        print("Verification results dict: ")
        print(output)
        return output

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


class EconomizerHighLimitC(RuleCheckBase):
    points = [
        "oa_db",
        "oa_threshold",
        "oa_min_flow",
        "oa_flow",
        "oa_enth",
        "oa_enth_threshold",
    ]

    def verify(self):
        self.result = ~(
            (self.df["oa_flow"] > self.df["oa_min_flow"])
            & (
                (self.df["oa_db"] > self.df["oa_threshold"])
                | (self.df["oa_enth"] > self.df["oa_enth_threshold"])
            )
        )

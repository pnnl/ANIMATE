# %% Import packages
from abc import ABC, abstractmethod
from src.checklib import CheckLibBase
from src.checklib import RuleCheckBase
import datetime
from datetime import timedelta, date
from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


class EconomizerHighLimitB(RuleCheckBase):
    points = ["oa_flow", "oa_db", "ret_a_temp", "oa_min_flow"]

    def verify(self):
        self.result = ~(
            (self.df["oa_flow"] > self.df["oa_min_flow"])
            & (self.df["ret_a_temp"] < self.df["oa_db"])
        )

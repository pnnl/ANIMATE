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


class EconomizerHighLimitA(RuleCheckBase):
    points = ["oa_db", "oa_threshold", "oa_min_flow", "oa_flow"]

    def verify(self):
        self.result = ~(
            (self.df["oa_flow"] > self.df["oa_min_flow"])
            & (self.df["oa_db"] > self.df["oa_threshold"])
        )

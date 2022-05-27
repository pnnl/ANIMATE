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


class ZoneTempControl(RuleCheckBase):
    points = ["T_z_set_cool", "T_z_set_heat"]

    def verify(self):
        self.result = (self.df["T_z_set_cool"] - self.df["T_z_set_heat"]) > 2.77

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


class HWReset(RuleCheckBase):
    points = [
        "T_oa_db",
        "T_oa_max",
        "T_oa_min",
        "T_hw",
        "m_hw",
        "T_hw_max_st",
        "T_hw_min_st",
    ]

    def verify(self):
        self.result = (
            (
                self.df["m_hw"] <= 0
            )  # add boundary relaxation in the rules for this one and chwreset
            | (
                (self.df["T_oa_db"] <= self.df["T_oa_min"])
                & (self.df["T_hw"] >= self.df["T_hw_max_st"] * 0.99)
            )
            | (
                (self.df["T_oa_db"] >= (self.df["T_oa_max"]))
                & (self.df["T_hw"] <= self.df["T_hw_min_st"] * 1.01)
            )
            | (
                (
                    (self.df["T_oa_db"] >= self.df["T_oa_min"])
                    & (self.df["T_oa_db"] <= self.df["T_oa_max"])
                )
                & (
                    (self.df["T_hw"] >= self.df["T_hw_min_st"] * 0.99)
                    & (self.df["T_hw"] <= self.df["T_hw_max_st"] * 1.01)
                )
            )
        )

    # Add a correlation scatter plot of T_oa_db and T_hw
    def plot(self, plot_option, plt_pts=None):
        print(
            "Specific plot method implemented, additional scatter plot is being added!"
        )
        plt.subplots()
        sns.scatterplot(x="T_oa_db", y="T_hw", data=self.df)
        plt.title("Scatter plot between T_oa_db and T_hw")

        super().plot(plot_option, plt_pts)

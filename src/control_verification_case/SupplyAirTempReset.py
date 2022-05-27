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


class SupplyAirTempReset(RuleCheckBase):
    points = ["T_sa_set", "T_z_coo"]

    def verify(self):

        t_sa_set_max = max(self.df["T_sa_set"])
        t_sa_set_min = min(self.df["T_sa_set"])

        self.result = (t_sa_set_max - t_sa_set_min) >= (
            self.df["T_z_coo"] - t_sa_set_min
        ) * 0.25 * 0.99  # 0.99 being the numeric threshold

    def plot(self, plot_option, plt_pts=None):
        print(
            "Specific plot method implemented, additional distribution plot is being added!"
        )
        sns.distplot(self.df["T_sa_set"])
        plt.title("All samples distribution of T_sa_set")
        plt.savefig(f"{self.results_folder}/All_samples_distribution_of_T_sa_set.png")

        super().plot(plot_option, plt_pts)

    def calculate_plot_day(self):
        """over write method to select day for day plot"""
        for one_day in self.daterange(date(2000, 1, 1), date(2001, 1, 1)):
            daystr = f"{str(one_day.year)}-{str(one_day.month)}-{str(one_day.day)}"
            daydf = self.df[daystr]
            day = self.result[daystr]
            if daydf["T_sa_set"].max() - daydf["T_sa_set"].min() > 0:
                return day, daydf
            return day, daydf
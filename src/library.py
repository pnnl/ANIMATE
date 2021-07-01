# %% Import packages
from abc import ABC, abstractmethod
from checklib import CheckLibBase
from checklib import RuleCheckBase
import datetime
from datetime import timedelta, date
from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class IntegratedEconomizerControl(CheckLibBase):
    points = ["oa_min_flow", "oa_flow", "ccoil_out"]

    def verify(self):
        self.flag = (self.df["oa_flow"] > self.df["oa_min_flow"]) & (
            self.df["ccoil_out"] > 0
        )

    def check_bool(self) -> bool:
        if len(self.flag[self.flag == True] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.flag),
            "Pass #": len(self.flag[self.flag == True]),
            "Fail #": len(self.flag[self.flag == False]),
            "Note": "No plots for verification of Integrated Economizer Control, this verification is considered passed as long as any sample passes",
        }
        print(output)


class SupplyAirTempReset(RuleCheckBase):
    points = ["T_sa_set", "T_z_coo"]

    def verify(self):

        t_sa_set_max = max(self.df["T_sa_set"])
        t_sa_set_min = min(self.df["T_sa_set"])

        self.result = (t_sa_set_max - t_sa_set_min) >= (
            self.df["T_z_coo"] - t_sa_set_min
        ) * 0.25

        print("debug use")


class EconomizerHighLimitA(RuleCheckBase):
    points = ["oa_db", "oa_threshold", "oa_min_flow", "oa_flow"]

    def verify(self):
        self.result = ~(
            (self.df["oa_flow"] > self.df["oa_min_flow"])
            & (self.df["oa_db"] > self.df["oa_threshold"])
        )


class EconomizerHighLimitB(RuleCheckBase):
    points = ["oa_flow", "oa_db", "ret_a_temp", "oa_min_flow"]

    def verify(self):
        self.result = ~(
            (self.df["oa_flow"] > self.df["oa_min_flow"])
            & (self.df["ret_a_temp"] < self.df["oa_db"])
        )


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
            & (self.df["oa_db"] > self.df["oa_threshold"])
            & (self.df["oa_enth"] > self.df["oa_enth_threshold"])
        )


class EconomizerHighLimitD(RuleCheckBase):
    points = [
        "oa_db",
        "oa_threshold",
        "oa_min_flow",
        "oa_flow",
        "oa_enth",
        "ret_a_enth",
    ]

    def verify(self):
        self.result = ~(
            (self.df["oa_flow"] > self.df["oa_min_flow"])
            & (self.df["ret_a_enth"] > self.df["oa_enth"])
            & (self.df["oa_db"] > self.df["oa_threshold"])
        )


class ZoneTempControl(RuleCheckBase):
    points = ["T_z_set_cool", "T_z_set_heat"]

    def verify(self):
        self.result = (self.df["T_z_set_cool"] - self.df["T_z_set_heat"]) > 5


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
            (self.df["m_hw"] <= 0)
            | (
                (self.df["T_oa_db"] <= self.df["T_oa_min"])
                & (self.df["T_hw"] == self.df["T_hw_max_st"])
            )
            | (
                (self.df["T_oa_db"] >= self.df["T_oa_max"])
                & (self.df["T_hw"] == self.df["T_hw_min_st"])
            )
            | (
                (
                    (self.df["T_oa_db"] >= self.df["T_oa_min"])
                    & (self.df["T_oa_db"] <= self.df["T_oa_max"])
                )
                & (
                    (self.df["T_hw"] >= self.df["T_hw_min_st"])
                    & (self.df["T_hw"] <= self.df["T_hw_max_st"])
                )
            )
        )


class CHWReset(RuleCheckBase):
    points = [
        "T_oa_db",
        "T_oa_max",
        "T_oa_min",
        "T_chw",
        "m_chw",
        "T_chw_max_st",
        "T_chw_min_st",
    ]

    def verify(self):
        self.result = (
            (self.df["m_chw"] <= 0)
            | (
                (self.df["T_oa_db"] <= self.df["T_oa_min"])
                & (self.df["T_chw"] == self.df["T_chw_max_st"])
            )
            | (
                (self.df["T_oa_db"] >= self.df["T_oa_max"])
                & (self.df["T_chw"] == self.df["T_chw_min_st"])
            )
            | (
                (
                    (self.df["T_oa_db"] >= self.df["T_oa_min"])
                    & (self.df["T_oa_db"] <= self.df["T_oa_max"])
                )
                & (
                    (self.df["T_chw"] >= self.df["T_chw_min_st"])
                    & (self.df["T_chw"] <= self.df["T_chw_min_st"])
                )
            )
        )

"""
This file contains all verification item claases
"""
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
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.stats import pearsonr
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from kneed import KneeLocator
from numpy import cov


class IntegratedEconomizerControl(CheckLibBase):
    points = ["oa_min_flow", "oa_flow", "ccoil_out"]

    def verify(self):
        self.result = (self.df["oa_flow"] > self.df["oa_min_flow"]) & (
            self.df["ccoil_out"] > 0
        )

    def check_bool(self) -> bool:
        if len(self.result[self.result == True] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
        }
        print(output)
        return output


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
            & (
                (self.df["oa_db"] > self.df["oa_threshold"])
                | (self.df["oa_enth"] > self.df["oa_enth_threshold"])
            )
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
            & (
                (self.df["ret_a_enth"] < self.df["oa_enth"])
                | (self.df["oa_db"] > self.df["oa_threshold"])
            )
        )


class ZoneTempControl(RuleCheckBase):
    points = ["T_z_set_cool", "T_z_set_heat"]

    def verify(self):
        self.result = (self.df["T_z_set_cool"] - self.df["T_z_set_heat"]) > 2.77


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
                & (self.df["T_chw"] >= self.df["T_chw_max_st"] * 0.99)
            )
            | (
                (self.df["T_oa_db"] >= self.df["T_oa_max"])
                & (self.df["T_chw"] <= self.df["T_chw_min_st"] * 1.01)
            )
            | (
                (
                    (self.df["T_oa_db"] >= self.df["T_oa_min"])
                    & (self.df["T_oa_db"] <= self.df["T_oa_max"])
                )
                & (
                    (self.df["T_chw"] >= self.df["T_chw_min_st"] * 0.99)
                    & (self.df["T_chw"] <= self.df["T_chw_max_st"] * 1.01)
                )
            )
        )

    # Add a correlation scatter plot of T_oa_db and T_chw
    def plot(self, plot_option, plt_pts=None):
        print(
            "Specific plot method implemented, additional scatter plot is being added!"
        )
        sns.scatterplot(x="T_oa_db", y="T_chw", data=self.df)
        plt.title("Scatter plot between T_oa_db and T_chw")
        plt.show()

        super().plot(plot_option, plt_pts)


class ZoneHeatSetpointMinimum(CheckLibBase):
    points = ["T_heat_set"]

    def verify(self):
        self.result = self.df["T_heat_set"] <= 12.78

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


class ZoneHeatingResetDepth(CheckLibBase):
    points = ["T_heat_set"]

    def verify(self):
        self.df["t_heat_set_min"] = min(self.df["T_heat_set"])
        self.df["t_heat_set_max"] = max(self.df["T_heat_set"])

        self.result = (self.df["t_heat_set_max"] - self.df["t_heat_set_min"]) >= 5.55

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
            "max(T_heat_set)": self.df["t_heat_set_max"][0],
            "min(T_heat_set)": self.df["t_heat_set_min"][0],
        }

        print("Verification results dict: ")
        print(output)
        return output


class ZoneCoolingResetDepth(CheckLibBase):
    points = ["T_cool_set"]

    def verify(self):
        self.df["t_cool_set_min"] = min(self.df["T_cool_set"])
        self.df["t_cool_set_max"] = max(self.df["T_cool_set"])

        self.result = (self.df["t_cool_set_max"] - self.df["t_cool_set_min"]) >= 2.77

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
            "max(T_cool_set)": self.df["t_cool_set_max"][0],
            "min(T_cool_set)": self.df["t_cool_set_min"][0],
        }

        print("Verification results dict: ")
        print(output)
        return output


class NightCycleOperation(CheckLibBase):
    points = [
        "T_zone",
        "HVAC_operation_sch",
        "T_heat_set",
        "T_cool_set",
        "Fan_elec_rate",
    ]

    def night_cycle_operation(self, data):
        tol = 0.5
        if data["HVAC_operation_sch"] == 0:
            if data["Fan_elec_rate"] == 0:
                if (data["T_heat_set"] - tol >= data["T_zone"]) or (
                    data["T_zone"] >= data["T_cool_set"] + tol
                ):
                    data["night_cycle_observed"] = -1  # Fail, NC should be running
                else:
                    data["night_cycle_observed"] = 0
            elif data["Fan_elec_rate"] > 0:
                data["night_cycle_observed"] = 1
        return data

    def verify(self):
        self.df["night_cycle_observed"] = np.nan
        self.df = self.df.apply(lambda r: self.night_cycle_operation(r), axis=1)
        self.result = ~(self.df["night_cycle_observed"] == -1)

    def check_bool(self) -> bool:
        res = False
        if (
            len(self.df["night_cycle_observed"][self.df["night_cycle_observed"] == 1])
            > 0
            and len(
                self.df["night_cycle_observed"][self.df["night_cycle_observed"] == 0]
            )
            > 0
            and len(
                self.df["night_cycle_observed"][self.df["night_cycle_observed"] == -1]
            )
            == 0
        ):
            res = True
        return res

    def check_detail(self) -> Dict:
        output = {
            "Sample #": len(self.df["night_cycle_observed"]),
            "night cycle 'on' observed #": len(
                self.df["night_cycle_observed"][self.df["night_cycle_observed"] == 1]
            ),
            "night cycle 'off' observed #": len(
                self.df["night_cycle_observed"][self.df["night_cycle_observed"] == 0]
            ),
            "night cycle NA observed #": len(
                self.df["night_cycle_observed"][
                    np.isnan(self.df["night_cycle_observed"])
                ]
            ),
            "Fail #": len(
                self.df["night_cycle_observed"][self.df["night_cycle_observed"] == -1]
            ),
            "Pass #": len(
                self.df["night_cycle_observed"][self.df["night_cycle_observed"] == 1]
            ),
            "Verification Passed?": self.check_bool(),
        }

        print("Verification results dict: ")
        print(output)
        return output


class ERVTemperatureControl(CheckLibBase):
    points = [
        "MIN_OA_FLOW",
        "OA_FLOW",
        "NOM_FLOW",
        "HX_DSN_EFF_HTG",
        "HX_DSN_EFF_HTG_75_PCT",
        "HX_DSN_EFF_CLG",
        "HX_DSN_EFF_CLG_75_PCT",
        "T_OA",
        "T_SO",
        "T_SO_SP",
        "T_EI",
    ]

    def erv_temperature_control(self, data):
        economizer = True if data["OA_FLOW"] > data["MIN_OA_FLOW"] * 1.01 else False
        hx_running = True if data["T_OA"] != data["T_SO"] else False
        hx_sens_eff_dsn_htg = (
            data["HX_DSN_EFF_HTG_75_PCT"]
            + (data["HX_DSN_EFF_HTG"] - data["HX_DSN_EFF_HTG_75_PCT"])
            * ((data["OA_FLOW"] / data["NOM_FLOW"]) - 0.75)
            / 0.25
        )
        hx_sens_eff_dsn_clg = (
            data["HX_DSN_EFF_CLG_75_PCT"]
            + (data["HX_DSN_EFF_CLG"] - data["HX_DSN_EFF_CLG_75_PCT"])
            * ((data["OA_FLOW"] / data["NOM_FLOW"]) - 0.75)
            / 0.25
        )
        hx_sens_eff = (data["T_SO"] - data["T_OA"]) / (data["T_EI"] - data["T_OA"])
        data["erv_temperature_control"] = 0  # pass by default
        if not economizer and data["OA_FLOW"] > 0:  # non-economizer operation
            if data["T_SO"] > data["T_SO_SP"] + 0.5:
                if data["T_OA"] < data["T_EI"] and hx_running:  # deadband
                    data["erv_temperature_control"] = 1
                elif data["T_OA"] > data["T_EI"] and not (
                    hx_running
                    and hx_sens_eff_dsn_clg * 0.95
                    < hx_sens_eff
                    < hx_sens_eff_dsn_clg * 1.05
                ):  # cooling
                    data["erv_temperature_control"] = 1
            elif data["T_SO"] < data["T_SO_SP"] - 0.5:  # heating
                if not (
                    hx_running
                    and hx_sens_eff_dsn_htg * 0.9
                    < hx_sens_eff
                    < hx_sens_eff_dsn_htg * 1.1
                ):
                    data["erv_temperature_control"] = 1
        else:  # economizer operation
            if hx_running:
                data["erv_temperature_control"] = 1
        return data

    def verify(self):
        self.df["erv_temperature_control"] = np.nan
        self.df = self.df.apply(lambda r: self.erv_temperature_control(r), axis=1)
        self.result = self.df["erv_temperature_control"]

    def check_bool(self) -> bool:
        if len(self.result[self.result == 1]) > 0:
            return False
        else:
            return True

    def check_detail(self) -> Dict:
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == 0]),
            "Fail #": len(self.result[self.result == 1]),
            "Verification Passed?": self.check_bool(),
        }

        print("Verification results dict: ")
        print(output)
        return output


class AutomaticOADamperControl(CheckLibBase):
    points = ["no_of_occ", "m_oa", "eco_onoff", "tol"]

    def verify(self):
        self.result = ~(
            (self.df["no_of_occ"] < self.df["tol"])
            & (self.df["m_oa"] > 0)
            & (self.df["eco_onoff"] == 0)
        )

    def check_bool(self) -> bool:
        if len(self.result[self.result == True] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
        }
        print(output)
        return output


class FanStaticPressureResetControl(CheckLibBase):
    points = [
        "p_set",
        "p_set_min",
        "d_VAV_1",
        "d_VAV_2",
        "d_VAV_3",
        "d_VAV_4",
        "d_VAV_5",
        "tol",
    ]

    def verify(self):
        d_vav_points = ["d_VAV_1", "d_VAV_2", "d_VAV_3", "d_VAV_4", "d_VAV_5"]
        d_vav_df = self.df[d_vav_points].copy()
        self.df["result"] = 1  # 0: false 1: true

        for row_num, (index, row) in enumerate(self.df.iterrows()):
            if row_num != 0:
                if (d_vav_df.loc[index] > 0.9).any():
                    self.df.at[index, "result"] = 1  # true
                else:
                    if self.df.at[index, "p_set"] > self.df.at[index, "p_set_min"]:
                        if (
                            self.df.at[index, "p_set"]
                            < self.df.at[prev_index, "p_set"] + self.df["tol"]
                        ):
                            self.df.at[index, "result"] = 1
                        else:
                            self.df.at[index, "result"] = 0  # false
                    else:
                        self.df.at[index, "result"] = 1
            prev_index = index

        self.result = self.df["result"].copy()

    def check_bool(self) -> bool:
        if len(self.result[self.result == 1] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == 1]),
            "Fail #": len(self.result[self.result == 0]),
            "Verification Passed?": self.check_bool(),
        }
        print(output)
        return output

    def calculate_plot_day(self):
        """over write method to select day for day plot"""
        for one_day in self.daterange(
            date(self.df.index[0].year, self.df.index[0].month, self.df.index[0].day),
            date(
                self.df.index[-1].year, self.df.index[-1].month, self.df.index[-1].day
            ),
        ):
            daystr = f"{str(one_day.year)}-{str(one_day.month)}-{str(one_day.day)}"
            daydf = self.df[daystr]
            day = self.result[daystr]

            return day, daydf


class HeatRejectionFanVariableFlowControlsCells(CheckLibBase):
    points = [
        "ct_op_cells",
        "ct_cells",
        "m",
        "P_fan_ct",
        "m_des",
        "min_flow_frac_per_cell",
    ]

    def verify(self):
        self.df["ct_cells_op_theo_intermediate"] = (
            self.df["m"]
            / self.df["m_des"]
            * self.df["min_flow_frac_per_cell"]
            / self.df["ct_cells"]
        ) + 0.9999
        self.df["ct_cells_op_theo_intermediate"] = self.df[
            "ct_cells_op_theo_intermediate"
        ].astype("int")

        self.df["ct_cells_op_theo"] = self.df[
            ["ct_cells_op_theo_intermediate", "ct_cells"]
        ].min(axis=1)

        self.result = ~(
            (self.df["ct_op_cells"] > 0)
            & (self.df["ct_op_cells"] < self.df["ct_cells_op_theo"])
            & (self.df["P_fan_ct"] > 0)
        )

    def check_bool(self) -> bool:
        if len(self.result[self.result == True] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
        }
        print(output)
        return output


class ServiceWaterHeatingSystemControl(CheckLibBase):
    points = ["T_wh_inlet"]

    def verify(self):
        self.result = self.df["T_wh_inlet"] < 43.33

    def check_bool(self) -> bool:
        if len(self.result[self.result == True] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
        }
        print(output)


class VAVStaticPressureSensorLocation(CheckLibBase):
    points = ["p_fan_setpoint", "tol"]

    def verify(self):
        self.result = self.df["p_fan_setpoint"] < 298.608 + self.df["tol"]

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


class VentilationFanControl(CheckLibBase):
    points = ["Q_load", "no_of_occ", "P_fan"]

    def verify(self):
        self.result = ~(
            (self.df["Q_load"] == 0)
            & (self.df["no_of_occ"] == 0)
            & (self.df["P_fan"] != 0)
        )

    def check_bool(self) -> bool:
        if len(self.result[self.result == True] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
        }
        print(output)
        return output

    def calculate_plot_day(self):
        """over write method to select day for day plot"""
        for one_day in self.daterange(
            date(self.df.index[0].year, self.df.index[0].month, self.df.index[0].day),
            date(
                self.df.index[-1].year, self.df.index[-1].month, self.df.index[-1].day
            ),
        ):
            daystr = f"{str(one_day.year)}-{str(one_day.month)}-{str(one_day.day)}"
            daydf = self.df[daystr]
            day = self.result[daystr]

            return day, daydf


class WLHPLoopHeatRejectionControl(RuleCheckBase):
    points = ["T_max_heating_loop", "T_min_cooling_loop", "m_pump", "tol"]

    def verify(self):
        self.df["T_max_heating_loop_max"] = (
            self.df.query("m_pump >0")["T_max_heating_loop"]
        ).max()
        self.df["T_min_cooling_loop_min"] = (
            self.df.query("m_pump >0")["T_min_cooling_loop"]
        ).min()

        self.result = (
            self.df["T_max_heating_loop_max"] - self.df["T_min_cooling_loop_min"]
        ) > 11.11 + self.df["tol"]


class AutomaticShutdown(RuleCheckBase):
    points = ["hvac_set"]

    def verify(self):
        copied_df = (
            self.df.copy()
        )  # copied not to store unnecessary intermediate variables in self.df dataframe
        copied_df.reset_index(
            inplace=True
        )  # convert index column back to normal column
        copied_df = copied_df.rename(
            columns={"index": "Date"}
        )  # rename the index column to Date
        copied_df["hvac_set_diff"] = copied_df[
            "hvac_set"
        ].diff()  # calculate the difference between previous and current rows
        copied_df = copied_df.dropna(axis=0)  # drop NaN row
        copied_df = copied_df.loc[
            copied_df["hvac_set_diff"] != 0.0
        ]  # filter out 0.0 values
        copied_df["Date"] = pd.to_datetime(
            copied_df["Date"], format="%Y-%m-%d %H:%M:%S"
        )
        df2 = copied_df.groupby(pd.to_datetime(copied_df["Date"]).dt.date).apply(
            lambda x: x.iloc[[0, -1]]
        )  # group by start/end time

        copied_df["start_time"] = df2["hvac_set_diff"].iloc[::2]  # even number row
        copied_df["end_time"] = df2["hvac_set_diff"].iloc[1::2]  # odd number row

        copied_df["min_start_time"] = copied_df.query("start_time == 1")["Date"].min()
        copied_df["max_start_time"] = copied_df.query("start_time == 1")["Date"].max()
        copied_df["min_end_time"] = copied_df.query("end_time == -1")["Date"].min()
        copied_df["max_end_time"] = copied_df.query("end_time == -1")["Date"].max()

        self.result = (copied_df["min_start_time"] != copied_df["max_start_time"]) & (
            copied_df["min_end_time"] != copied_df["max_end_time"]
        )

    def check_bool(self) -> bool:
        if len(self.result[self.result == 1]) > 0:
            return True
        else:
            return False

    def check_detail(self) -> Dict:
        print("Verification results dict: ")
        output = {
            "Sample #": 1,
            "Verification Passed?": self.check_bool(),
        }
        print(output)
        return output

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass


class HeatPumpSupplementalHeatLockout(CheckLibBase):
    points = ["C_ref", "L_op", "P_supp_ht", "C_t_mod", "C_ff_mod", "L_defrost"]

    def heating_coil_verification(self, data):
        if data["P_supp_ht"] == 0:
            data["result"] = 1  # True
        else:
            if data["L_defrost"] > 0:
                data["result"] = 1
            else:
                if data["C_op"] > data["L_op"]:
                    data["result"] = 0  # False
                else:
                    data["result"] = 1
        return data

    def verify(self):
        self.df["C_op"] = self.df["C_ref"] * self.df["C_t_mod"] * self.df["C_ff_mod"]
        self.df["result"] = np.nan
        self.df = self.df.apply(lambda r: self.heating_coil_verification(r), axis=1)
        self.result = self.df["result"]

    def check_bool(self) -> bool:
        if len(self.result[self.result == 1] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == 1]),
            "Fail #": len(self.result[self.result == 0]),
            "Verification Passed?": self.check_bool(),
        }
        print(output)
        return output


class HeatRejectionFanVariableFlowControl(RuleCheckBase):
    points = ["P_ct_fan", "m_ct_fan_ratio", "P_ct_fan_dsgn", "m_ct_fan_dsgn"]

    def verify(self):
        self.df.loc[:, "m_ct_fan"] = (
            self.df.loc[:, "m_ct_fan_ratio"] * self.df.loc[:, "m_ct_fan_dsgn"]
        )
        self.df.loc[:, "normalized_m_ct_fan"] = (
            self.df.loc[:, "m_ct_fan"] / self.df.loc[:, "m_ct_fan_dsgn"]
        )
        self.df.loc[:, "normalized_P_ct_fan"] = (
            self.df.loc[:, "P_ct_fan"] / self.df.loc[:, "P_ct_fan_dsgn"]
        )

        self.df = self.df.loc[
            self.df["normalized_P_ct_fan"] > 0.0
        ]  # filter out 0 values
        self.df["normalized_m_ct_fan"] -= 1  # minus 1 to transform the data
        self.df["normalized_P_ct_fan"] -= 1

        # linear regression
        reg = LinearRegression(fit_intercept=False).fit(
            self.df["normalized_m_ct_fan"].values.reshape(-1, 1),
            self.df["normalized_P_ct_fan"],
        )  # fit_intercept=False is for set the intercept to 0

        if reg.coef_[0] >= 1.4:
            self.df["result"] = 1  # True
        else:
            self.df["result"] = 0  # False

        self.result = self.df["result"].copy(deep=True)

    def check_bool(self) -> bool:
        if len(self.result[self.result == 0] > 0):
            return False
        else:
            return True

    def check_detail(self) -> Dict:
        output = {
            "Sample #": 1,
            "Verification Passed?": self.check_bool(),
        }

        print("Verification results dict: ")
        print(output)
        return output

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass


class DemandControlVentilation(CheckLibBase):
    points = ["v_oa", "s_ahu", "s_eco", "no_of_occ_per1", "no_of_occ_per2", "no_of_occ_per3", "no_of_occ_per4", "no_of_occ_core"]

    def cluster(self, data):
        # Standardize the data to have a mean of 0 and standard deviation of 1 (feature scaling)
        # reason: the algorithm may consider the greater values in data because some feature values are greater and have higher variability because of unit difference.
        scaler = StandardScaler()
        scaled_df = scaler.fit_transform(data)

        kmeans_kwargs = {
            "init": "random",
            "n_init": 10,
            "max_iter": 300,
        }

        # evaluate the appropriate no. clusters,
        # use elbow method: run several K-means, increment k with each iteration and record the SSE
        # sweet spot is where the SSE curve starts to bend (a.k.a elbow point)
        # the silhouette coefficient isn't used because it requires to have at least 2 clusters. However, DCV data could have only 0 or 1 cluster
        SSE = []
        for k in range(1, 11):
            kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
            kmeans.fit(scaled_df)
            SSE.append(kmeans.inertia_)

            # if k == 4:
            #     print(kmeans.labels_)
            #     label = kmeans.labels_
            #     np.savetxt('label.csv', label, delimiter=",")

        no_of_cluster = KneeLocator(
            range(1, 11), SSE, curve="convex", direction="decreasing"
        ).elbow

        return no_of_cluster

    def verify(self):
        df_filtered = self.df.loc[
            (self.df["s_eco"] == 0.0) & (self.df["s_ahu"] != 0.0)
        ]  # filter out data when economizer isn't enabled
        # df_filtered.to_csv("filtered_df.csv")
        df_filtered["no_of_occ"] = df_filtered["no_of_occ_per1"] + df_filtered["no_of_occ_per2"] + df_filtered["no_of_occ_per3"] + df_filtered["no_of_occ_per4"] + df_filtered["no_of_occ_core"]
        # Pearson’s correlation
        corr, _ = pearsonr(df_filtered["no_of_occ"], df_filtered["v_oa"])

        # Linear regression
        reg = LinearRegression().fit(
            df_filtered["no_of_occ"].values.reshape(-1, 1), df_filtered["v_oa"]
        )

        # clustering
        no_of_clus = self.cluster(df_filtered)

        if (
            len(df_filtered["no_of_occ"].unique()) == 1
            or len(df_filtered["v_oa"].unique()) == 1
        ):
            self.df["DCV_type"] = 0  # NO DCV is observed
            self.dcv_msg = "NO DCV"
        elif no_of_clus == 2:
            self.df["DCV_type"] = 1  # DCV with binary control is observed
            self.dcv_msg = "DCV with binary control"
        elif corr > 0:
            self.df["DCV_type"] = 2  # DCV with occupant-counting based control
            self.dcv_msg = "DCV with occupant-counting based control"
        self.result = self.df["DCV_type"]

    def check_bool(self) -> bool:
        if len(self.result[self.result != 0] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": 1,
            "Verification Passed?": self.check_bool(),
            "Type of Demand Control Ventilation": self.dcv_msg,
        }
        print(output)
        return output

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass


class OptimumStart(CheckLibBase):
    points = ["T_oa_dry", "T_z_measure", "T_z_hea_set", "T_z_coo_set", "s_AHU", "occ"]

    def correlation(self, len_of_s_AHU, *cor_data): # cor_data: t_length, T_oa_dry, T_diff_heating, T_diff_cooling
        if len_of_s_AHU > 1:
            if pearsonr([cor_data[0] for _ in range(len(cor_data[1]))], cor_data[1])[0] > 0.5:
                return 1  # Optimum start is observed and confirmed
            elif pearsonr([cor_data[0] for _ in range(len(cor_data[2]))], cor_data[2])[0] > 0.5:
                return 1
            elif pearsonr([cor_data[0] for _ in range(len(cor_data[3]))], cor_data[3])[0] > 0.5:
                return 1
        else:
            return 0 # Optimum start is not correlated with outside temperature, zone temperature, etc. and may not work well

    def verify(self):
        result_repo = []
        year_info = 2000
        for idx, day in self.df.groupby(self.df.index.date):
            if day.index.month[0] == 2 and day.index.day[0] == 29:  # skip leap year, although E+ doesn't have leap year the date for loop assumes so because 24:00 time step so, it's intentionally skipped here
                pass
            elif year_info != day.index.year[0]:  # remove the Jan 1st of next year reason: the pandas date for loop iterates one more loop is hour is 24:00:00
                pass
            else:
                T_heat_diff = day[day["T_z_hea_set"].diff() >= 0.01]
                T_s_AHU_diff = day[day["s_AHU"].diff() >= 0.01]

                if len(T_heat_diff["T_z_hea_set"]) != 0:
                    t_length_s_hea = (T_heat_diff["T_z_hea_set"]).index[0]
                else:
                    t_length_s_hea = 0

                if len(T_s_AHU_diff["s_AHU"]) != 0:
                    t_length_s_AHU = (day[day["s_AHU"].diff() >= 0.01]["s_AHU"]).index[0]
                else:
                    t_length_s_AHU = 0

                t_length_s_hea = pd.to_datetime(t_length_s_hea)
                t_length_s_AHU = pd.to_datetime(t_length_s_AHU)
                t_length = (pd.Timedelta(t_length_s_AHU - t_length_s_hea).seconds)/3600 # divide by 3660 to obtain t_length in hour

                T_oa_dry = T_s_AHU_diff["T_oa_dry"]
                T_z_measured = T_s_AHU_diff["T_z_measure"]

                T_z_hea_set_occ = day.query('occ > 0')["T_z_hea_set"].max()
                T_z_hea_set_unocc = day.query('occ == 0')["T_z_hea_set"].max()

                T_z_coo_set_occ = day.query('occ > 0')["T_z_coo_set"].min()
                T_z_coo_set_unocc = day.query('occ == 0')["T_z_coo_set"].min()

                T_diff_heating = T_z_measured - T_z_hea_set_occ
                T_diff_cooling = T_z_measured - T_z_coo_set_occ

                if len(day["s_AHU"].unique()) == 1 and day["s_AHU"].unique() in [0, 1]:
                    if len(day["s_AHU"].unique()) == 0:
                        result_repo.append(0) # No optimum start
                    else:
                        result_repo.append(self.correlation(len(T_s_AHU_diff), T_oa_dry, T_diff_heating, T_diff_cooling))
                else:
                    if False: # len(t_length.unique()) == 1: # t_length is a constant @ all t # TODO ask Yan
                        result_repo.append(0) # No optimum start
                    else:
                        result_repo.append(self.correlation(len(T_s_AHU_diff), T_oa_dry, T_diff_heating, T_diff_cooling))
                year_info = day.index.year[0]
        self.result = result_repo

    def check_bool(self) -> bool:
        if len(self.result[self.result == 1] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == 1]),
            "Fail #": len(self.result[self.result == 0]),
            "Verification Passed?": self.check_bool(),
        }
        print(output)
        return output

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass


class GuestRoomControlTemp(CheckLibBase):
    points = ["T_z_hea_set", "T_z_coo_set", "O_sch", "tol_occ", "tol_temp"]

    def verify(self):
        result_repo = []
        tol_occ = self.df["tol_occ"][0]
        tol_temp = self.df["tol_temp"][0]
        year_info = 2000
        for idx, day in self.df.groupby(self.df.index.date):
            if day.index.month[0] == 2 and day.index.day[0] == 29: # skip leap year, although E+ doesn't have leap year the date for loop assumes so because 24:00 time step so, it's intentionally skipped here
                pass
            elif year_info != day.index.year[0]: # remove the Jan 1st of next year reason: the pandas date for loop iterates one more loop is hour is 24:00:00
                pass
            else:
                if day["O_sch"].all() <= tol_occ: # confirmed this room is rented out
                    if day["T_z_hea_set"].all() < 15.6 + tol_temp and day["T_z_coo_set"].all() > 26.7 - tol_temp:
                        result_repo += [1 for _ in range(24)] # pass, confirmed zone temperature setpoint reset during the unrented period
                    else:
                        result_repo += [0 for _ in range(24)] # fail, zone temperature setpoint was not reset correctly

                else: # room is  rented out
                    T_z_hea_occ_set = day.query('O_sch > 0.0')["T_z_hea_set"].max()
                    T_z_coo_occ_set = day.query('O_sch > 0.0')["T_z_coo_set"].min()

                    if day["T_z_hea_set"].all() < T_z_hea_occ_set - 2.22 + tol_temp or day[
                        "T_z_coo_set"].all() > T_z_coo_occ_set + 2.22 - tol_temp:
                        result_repo += [1 for _ in range(
                            24)]  # pass, confirm the HVAC setpoint control resets when guest room reset when occupants leave the room
                    else:
                        result_repo += [0 for _ in range(24)]  # fail, reset does not meet the standard or no reset was observed.

                year_info = day.index.year[0]

        self.result = pd.DataFrame(data=result_repo)
        print(f"shape of result is {self.result.shape}")
        palceholder = 1

    def check_bool(self) -> bool:
        if len(self.result[self.result == 1] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == 1]),
            "Fail #": len(self.result[self.result == 0]),
            "Verification Passed?": self.check_bool(),
        }
        print(output)
        return output


class GuestRoomControlVent(CheckLibBase):
    points = ["m_z_oa_set", "m_z_oa", "O_sch", "v_zone", "tol_occ", "tol_m"]

    def verify(self):
        result_repo = []
        tol_occ = self.df["tol_occ"][0]
        tol_m = self.df["tol_m"][0]
        zone_volume = self.df["v_zone"][0]
        year_info = 2000
        for idx, day in self.df.groupby(self.df.index.date):
            if day.index.month[0] == 2 and day.index.day[0] == 29:  # skip leap year, although E+ doesn't have leap year the date for loop assumes so because 24:00 time step so, it's intentionally skipped here
                pass
            elif year_info != day.index.year[0]:  # remove the Jan 1st of next year reason: the pandas date for loop iterates one more loop is hour is 24:00:00
                pass
            else:
                if day["O_sch"].all() <= tol_occ:  # check if this room is rented out
                    if day["m_z_oa"] == 0:
                        result_repo += [1 for _ in range(24)]  # pass,
                    else:
                        result_repo += [0 for _ in range(24)]  # fail,
                else:
                    if day["m_z_oa"] == 0:
                        if day["m_z_oa"] == day["m_z_oa_set"] or day["m_z_oa"] == zone_volume:
                            result_repo += [1 for _ in range(24)]  # pass,
                        else:
                            result_repo += [0 for _ in range(24)]  # fail,


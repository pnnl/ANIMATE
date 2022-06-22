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
    points = ["no_of_occ", "m_oa", "eco_onoff"]

    def verify(self):
        tol = 0.03
        self.result = ~(
            (self.df["no_of_occ"] < tol)
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
    points = ["p_set", "d_VAV_1", "d_VAV_2", "d_VAV_3", "d_VAV_4", "d_VAV_5"]

    def verify(self):
        tol = 1
        d_vav_points = ["d_VAV_1", "d_VAV_2", "d_VAV_3", "d_VAV_4", "d_VAV_5"]
        d_vav_df = self.df[d_vav_points].copy(deep=True)
        self.df["result"] = True
        self.df.at[
            0, "result"
        ] = True  # set first row True, reason: first row can't be determined

        for row_num, (index, row) in enumerate(self.df.iterrows()):
            if row_num != 0:
                if (
                    self.df.at[index, "p_set"] > self.df.at[prev_index, "p_set"] + tol
                    and (d_vav_df.iloc[row_num] < 0.9).all()
                ):
                    self.df.at[index, "result"] = False
            prev_index = index

        self.result = self.df["result"].copy(deep=True)

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
        self.df["ct_cells_op_theo"] = np.nan
        for index, row in self.df.iterrows():
            self.df.at[index, "ct_cells_op_theo"] = min(
                int(
                    (
                        self.df.loc[index, "m"]
                        / self.df.loc[index, "m_des"]
                        * self.df.loc[index, "min_flow_frac_per_cell"]
                        / self.df.loc[index, "ct_cells"]
                    )
                    + 0.9999
                ),
                self.df.loc[index, "ct_cells"],
            )
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
    points = ["p_fan_setpoint"]

    def verify(self):
        tol = 2.98  # 1 % of 298.608 Pa

        self.result = self.df["p_fan_setpoint"] < 298.608 + tol

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


class WLHPLoopHeatRejectionControl(CheckLibBase):
    points = ["T_max_heating_loop", "T_min_cooling_loop", "m_pump"]

    def verify(self):
        tol = 0.556
        self.df["T_max_heating_loop_max"] = (
            self.df.query("m_pump >0")["T_max_heating_loop"]
        ).max()
        self.df["T_min_cooling_loop_min"] = (
            self.df.query("m_pump >0")["T_min_cooling_loop"]
        ).min()

        self.result = (
            self.df["T_max_heating_loop_max"] - self.df["T_min_cooling_loop_min"]
        ) > 11.11 + tol

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
            "max(T_max_heating_loop0": self.df["T_max_heating_loop_max"][0],
            "min(T_min_cooling_loop)": self.df["T_min_cooling_loop_min"][0],
        }
        print(output)
        return


class AutomaticShutdown(CheckLibBase):
    points = ["hvac_set"]

    def verify(self):

        self.copied_df = self.df.copy(
            deep=True
        )  # copied not to store unnecessary intermediate variables in self.df dataframe
        # self.copied_df.to_csv("self.copied_df.csv")
        self.copied_df.reset_index(
            inplace=True
        )  # convert index column back to normal column
        self.copied_df = self.copied_df.rename(
            columns={"index": "Date"}
        )  # rename the index column to Date
        self.copied_df["hvac_set_diff"] = self.copied_df[
            "hvac_set"
        ].diff()  # calculate the difference between previous and current rows
        self.copied_df = self.copied_df.dropna(axis=0)  # drop NaN row
        self.copied_df = self.copied_df.loc[
            self.copied_df["hvac_set_diff"] != 0.0
        ]  # filter out 0.0 values
        self.copied_df["Date"] = pd.to_datetime(
            self.copied_df["Date"], format="%Y/%m/%d %H:%M:%S"
        )
        self.df2 = self.copied_df.groupby(
            pd.to_datetime(self.copied_df["Date"]).dt.date
        ).apply(
            lambda x: x.iloc[[0, -1]]
        )  # group by start/end time
        self.df["start_time"] = self.df2["hvac_set_diff"].iloc[::2]  # even number row
        self.df["end_time"] = self.df2["hvac_set_diff"].iloc[1::2]  # odd number row

        # self.df["min_start_time"] = min(
        #     self.df2["hvac_set_diff"].iloc[::2]
        # )  # even number row
        # self.df["max_start_time"] = max(self.df2["hvac_set_diff"].iloc[::2])
        # self.df["min_end_time"] = min(
        #     self.df2["hvac_set_diff"].iloc[1::2]
        # )  # odd number row
        # self.df["max_end_time"] = max(self.df2["hvac_set_diff"].iloc[1::2])

        self.result = (self.df["min_start_time"] != self.df["max_start_time"]) & (
            self.df["min_end_time"] != self.df["max_end_time"]
        )

    def check_bool(self) -> bool:
        if len(self.result[self.result == True] > 0):
            return True
        else:
            return False

    def check_detail(self) -> Dict:
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
            "min(start_time)": self.df["min_start_time"][0],
            "max(start_time)": self.df["max_start_time"][0],
            "min(end_time)": self.df["min_end_time"][0],
            "max(end_time)": self.df["max_end_time"][0],
        }
        print(output)
        return output


class HeatRejectionFanVariableFlowControl(CheckLibBase):
    points = ["m_ct_fan", "m_ct_fan_dsgn", "P_ct_fan", "P_ct_fan_dsgn"]

    def verify(self):
        self.result = 1 # TODO fix the logic

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


class HeatPumpSupplementalHeatLockout(CheckLibBase):
    points = ["hvac_set", "C_t_mod", "L_op", "P_supp_ht"]

    def verify(self):
        self.df["C_op"] = self.df["hvac_set"] * self.df["C_t_mod"]

        self.result = (self.df["C_op"] > self.df["L_op"]) & (
            self.df["P_supp_ht"] == 0
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


class DemandControlVentilation(CheckLibBase):
    points = ["v_oa", "s_ahu", "s_eco", "o_z_i"]

    def verify(self):
        self.df["C_op"] = self.df["hvac_set"] * self.df["C_t_mod"] # TODO check this line is executed correctly

        self.result = (self.df["C_op"] > self.df["L_op"]) & (
            self.df["P_supp_ht"] == 0
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
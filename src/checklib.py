# %% Supress future warning if needed
import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

# %% import packages
import datetime
from datetime import timedelta, date
from typing import List, Dict
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import seaborn as sns

# plt.style.use("ggplot")
import pandas as pd
from pandas.plotting import register_matplotlib_converters

# register_matplotlib_converters()


class CheckLibBase(ABC):
    """Abstract class defining interfaces for item-specific verification classes"""

    points = None

    def __init__(self, df: pd.DataFrame, params=None):
        full_df = df.copy(deep=True)
        if params is not None:
            for k, v in params.items():
                full_df[k] = v

        col_list = full_df.columns.values.tolist()
        if not set(self.points_list).issubset(set(col_list)):
            print(f"Dataset is not sufficient for running {self.__class__.__name__}")
            print(set(col_list))
        self.df = full_df[self.points_list]
        self.verify()

    @property
    def points_list(self) -> List[str]:
        return self.points

    @abstractmethod
    def check_bool(self) -> bool:
        """implementation of the checking boolean return"""
        pass

    @abstractmethod
    def check_detail(self) -> Dict:
        """implementaion of the checking detailed return in Dict"""
        pass

    @abstractmethod
    def verify(self):
        """checking logic implementation, not for user"""
        pass

    @property
    def get_checks(self):
        return self.check_bool(), self.check_detail()


class RuleCheckBase(CheckLibBase):
    def check_bool(self) -> bool:
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True

    def check_detail(self) -> Dict:
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
        }

        print("Verification results dict: ")
        print(output)

        ax1 = plt.subplot(311)
        sns.scatterplot(x=self.result.index, y=self.result, linewidth=0, s=1)
        plt.xlim([self.df.index[0], self.df.index[-1]])
        plt.ylim([-0.2, 1.2])
        plt.title(f"Pass / Fail flag plot - {self.__class__.__name__}")

        trueday = None
        truedaydf = None
        falseday = None
        falsedaydf = None
        mixday = None
        mixdaydf = None

        ratio = -0.5

        # Looking for day with most balanced pass/fail samples
        for one_day in self.daterange(date(2000, 1, 1), date(2001, 1, 1)):
            daystr = f"{str(one_day.year)}-{str(one_day.month)}-{str(one_day.day)}"
            daydf = self.df[daystr]
            day = self.result[daystr]
            if (trueday is None) and len(day[day == True]) > 0:
                trueday = day
                truedaydf = daydf
                # print("reach true")
                continue
            if (falseday is None) and len(day[day == False]) > 0:
                falseday = day
                falsedaydf = daydf
                # print("reach false")
                continue

            if len(day[day == False]) == 0 or len(day[day == True]) == 0:
                continue

            new_ratio = len(day[day == True]) / len(day) - 0.5
            # print(new_ratio)

            # print(f"newratio: {new_ratio}")

            if abs(new_ratio) < abs(ratio):
                ratio = new_ratio
                mixday = day
                mixdaydf = daydf
                # print(ratio)
        # print(f"Final plot ratio: {ratio}")

        if mixdaydf is None:
            plotdaydf = daydf
            plotday = day
        else:
            plotdaydf = mixdaydf
            plotday = mixday

        # below are for humidity demo
        ax2 = plt.subplot(312)
        plotdaydf.plot(ax=ax2)
        plt.title(f"Example day plot - {self.__class__.__name__}")

        ax3 = plt.subplot(313)
        sns.scatterplot(x=plotday.index, y=plotday)
        plt.xlim([plotday.index[0], plotday.index[-1]])
        plt.ylim([-0.2, 1.2])
        plt.title(f"Example day Pass / Fail flag - {self.__class__.__name__}")
        plt.show()

        # below are for non int economizer demo
        # plotdaydf[['Cool_sys_out']].plot()
        # plt.xlabel("Date/Time")
        # plt.ylabel("Variable value")
        # plt.tight_layout()
        # plt.savefig("1.png")
        # plt.show()
        # plotdaydf[['OA_min_sys', 'OA_timestep']].plot()
        # plt.xlabel("Date/Time")
        # plt.ylabel("Variable value")
        # plt.tight_layout()
        # plt.savefig("2.png")
        # plt.show()
        # # sns.scatterplot(x=plotday.index, y=plotday)
        # # plt.xlim([plotday.index[0], plotday.index[-1]])
        # # plotday = pd.DataFrame(plotday.astype(float))
        # plotday.astype(float).plot()
        # plt.title("Not ($OA_timestep > $OA_min_sys and $Cool_sys_out > 0)")
        # plt.xlabel("Date/Time")
        # plt.ylabel("Variable value")
        # plt.tight_layout()
        # plt.savefig("3.png")
        # plt.show()

        return output

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)


class EconomizerIntegrationCompliance(RuleCheckBase):
    points = ["OA_min_sys", "OA_timestep", "Cool_sys_out"]

    def verify(self):
        """Economizer Integration: Non-Integrated Economizer Operation

        "assertions_type": "fail",
        "assertion_level": "sample",
        "assertions": ["$OA_timestep > $OA_min_sys and $Cool_sys_out > 0"],
        """

        # Logical Operators in Pandas are &, | and ~, and parentheses (...) is important!
        self.result = ~(
            (self.df["OA_timestep"] > self.df["OA_min_sys"])
            & (self.df["Cool_sys_out"] > 0)
        )


class EconomizerHeatingCompliance(RuleCheckBase):
    points = ["OA_min_sys", "OA_timestep", "Heat_sys_out"]

    def verify(self):

        self.result = ~(
            (self.df["OA_timestep"] > self.df["OA_min_sys"])
            & (self.df["Heat_sys_out"] > 0)
        )


class HeatRecoveryCompliance(RuleCheckBase):
    points = ["OA_timestep", "Heat_rec", "Cool_rec", "OA_min_sys"]

    def verify(self):
        self.result = ~(
            (self.df["OA_timestep"] > self.df["OA_min_sys"])
            & ((self.df["Heat_rec"] > 0) | (self.df["Cool_rec"] > 0))
        )


class SimultaneousHeatingCoolingCompliance(RuleCheckBase):
    points = ["Cool_sys_out", "Heat_sys_out"]

    def verify(self):
        self.result = ~((self.df["Cool_sys_out"] > 0) & (self.df["Heat_sys_out"] > 0))

class HumidityWithinBoundaries(RuleCheckBase):
    points = ["Zone_hum", "Hum_up_bound", "Hum_low_bound"]

    def verify(self):
        self.result = ((self.df["Zone_hum"] >= self.df["Hum_up_bound"]) & (self.df["Zone_hum"] <= self.df["Hum_low_bound"]))

class ContinuousDimmingCompliance(CheckLibBase):
    points = ["Electric_light_power"]
    flat_min_threshold = 60

    def check_bool(self) -> bool:
        if self.max_up_period > 60 and self.max_down_period > 60:
            return True
        return False

    def check_detail(self) -> Dict:
        output = {
            "max_up_period": self.max_up_period,
            "max_down_period": self.max_down_period,
            "max_up_start": self.max_up_start,
            "max_up_end": self.max_up_end,
            "max_down_start": self.max_down_start,
            "max_down_end": self.max_down_end,
        }

        sns.scatterplot(x=self.df.index, y=self.df["Electric_light_power"])
        plt.axvspan(
            output["max_up_start"], output["max_up_end"], color="red", alpha=0.3
        )
        plt.axvspan(
            output["max_down_start"], output["max_down_end"], color="green", alpha=0.3
        )
        plt.xlim([self.df.index[0], self.df.index[-1]])
        plt.title(self.__class__.__name__)
        plt.show()
        return output

    def verify(self):
        max_up_period = 0
        max_down_period = 0
        trend_period = 0
        v_prev = None
        trend = None
        start_time_flat = None
        end_time_flat = None
        start_time = None
        end_time = None
        max_up_start = None
        max_up_end = None
        max_down_start = None
        max_down_end = None
        flat_flag = False

        for i, v in self.df["Electric_light_power"].iteritems():
            if v_prev is None:
                v_prev = v
                start_time = i
                end_time = i
                continue
            if v > v_prev:
                if trend == -1:
                    start_time = i
                trend = 1
                flat_flag = False
                end_time = i
            if v < v_prev:
                if trend == 1:
                    start_time = i
                trend = -1
                flat_flag = False
                end_time = i
            if v == v_prev:
                if flat_flag:
                    end_time_flat = i
                else:
                    start_time_flat = i
                    flat_flag = True
                    v_prev = v
                    continue
                if (
                    self.delta_minutes(start_time_flat, end_time_flat)
                    >= self.flat_min_threshold
                ):
                    trend_period = 0
                    v_prev = v
                    start_time = i
                    end_time = i
                    continue
            trend_period = self.delta_minutes(start_time, end_time)

            if trend == 1 and trend_period > max_up_period:
                max_up_period = trend_period
                max_up_start = start_time
                max_up_end = end_time
            if trend == -1 and trend_period > max_down_period:
                max_down_period = trend_period
                max_down_start = start_time
                max_down_end = end_time

            v_prev = v

        self.max_up_start = max_up_start
        self.max_up_end = max_up_end
        self.max_down_start = max_down_start
        self.max_down_end = max_down_end
        self.max_up_period = max_up_period
        self.max_down_period = max_down_period

    def delta_minutes(
        self, start_time_flat: datetime.datetime, end_time_flat: datetime.datetime
    ) -> float:
        return (end_time_flat - start_time_flat).total_seconds() / 60


def main():
    import json
    from tqdm import tqdm

    with open("../schema/simplified2items.json") as json_file:
        data = json.load(json_file)
    items = data["items"]

    from datetimeep import DateTimeEP

    # check dimming control example

    # df1 = DateTimeEP(
    #     pd.read_csv(
    #         "../resources/ASHRAE901_SchoolPrimary_STD2019_ElPaso/ASHRAE901_SchoolPrimary_STD2019_ElPaso.csv"
    #     )
    # ).transform()

    # dimming_item = items[0]
    # point_map = dimming_item["datapoints_source"]["output_variables"]
    # point_map_reverse = {value.strip(): key.strip() for key, value in point_map.items()}
    # new_df1 = df1.rename(str.strip, axis="columns")
    # new_df1 = new_df1.rename(columns=point_map_reverse)
    # cdc = ContinuousDimmingCompliance(new_df1["2000-07-21"]).get_checks
    # print(cdc)

    # check rule based examples
    df_rule = DateTimeEP(
        pd.read_csv(
            "../resources/ASHRAE901_Hospital_STD2016_Tampa/ASHRAE901_Hospital_STD2016_Tampa.csv" # hudmidity
            # "../resources/ASHRAE901_SchoolPrimary_STD2004_ElPaso_Injected/eplusout.csv" # non-int economizer
        )
    ).transform()

    # rule_items_id = [1] # non-int economizer
    rule_items_id = [-1] # humidity
    for item_id in rule_items_id:
        item = items[item_id]
        point_map = item["datapoints_source"]["output_variables"]
        point_map_reverse = {
            value.strip(): key.strip() for key, value in point_map.items()
        }
        new_df = df_rule.rename(str.strip, axis="columns")
        new_df = new_df.rename(columns=point_map_reverse)

        cls = globals()[item["verification_class"]]
        parameter = (
            item["datapoints_source"]["parameters"]
            if ("parameters" in item["datapoints_source"])
            else None
        )
        outcome = cls(new_df, item["datapoints_source"]["parameters"]).get_checks

        print(f"{item['verification_class']}:")
        print(outcome)


if __name__ == "__main__":
    main()

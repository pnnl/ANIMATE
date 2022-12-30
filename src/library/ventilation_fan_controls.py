from checklib import RuleCheckBase
from datetime import date


class VentilationFanControl(RuleCheckBase):
    points = ["Q_heat_req", "Q_cool_req", "fan_onoff", "P_fan"]

    def verify(self):
        self.result = ~(
            (self.df["Q_heat_req"] > 0)
            & (self.df["Q_heat_req"] > 0)
            & (self.df["fan_onoff"] == 0)
            & (self.df["P_fan"] != 0)
        )

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

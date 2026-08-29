from checklib import RuleCheckBase


class SWHRestroomOutletMaximumTemperatureControls(RuleCheckBase):
    points = ["T_wh_inlet", "tol_temp"]

    def verify(self):
        self.result = self.df["T_wh_inlet"] < 43.33 - self.df["tol_temp"]

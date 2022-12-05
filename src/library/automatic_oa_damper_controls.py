from checklib import RuleCheckBase


class AutomaticOADamperControl(RuleCheckBase):
    points = ["o", "m_oa", "eco_onoff", "tol"]

    def verify(self):
        self.result = ~(
            (self.df["o"] < self.df["tol"])
            & (self.df["m_oa"] > 0)
            & (self.df["eco_onoff"] == 0)
        )

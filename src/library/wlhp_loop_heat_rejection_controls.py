from checklib import RuleCheckBase


class WLHPLoopHeatRejectionControl(RuleCheckBase):
    points = ["T_loop", "m_pump", "tol"]

    def verify(self):
        self.df["T_max_loop"] = (
            self.df.query("m_pump >0")["T_loop"]
        ).max()
        self.df["T_min_min"] = (
            self.df.query("m_pump >0")["T_loop"]
        ).min()

        self.result = (
            self.df["T_max_loop"] - self.df["T_min_min"]
        ) > 11.11 - self.df["tol"]

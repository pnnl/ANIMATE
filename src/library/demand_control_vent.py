from checklib import CheckLibBase
from scipy.stats import pearsonr


class DemandControlVentilation(CheckLibBase):
    points = [
        "v_oa",
        "s_ahu",
        "s_eco",
        "no_of_occ_per1",
        "no_of_occ_per2",
        "no_of_occ_per3",
        "no_of_occ_per4",
        "no_of_occ_core",
    ]

    def verify(self):
        df_filtered = self.df.loc[
            (self.df["s_eco"] == 0.0) & (self.df["s_ahu"] != 0.0)
        ]  # filter out data when economizer isn't enabled

        df_filtered["no_of_occ"] = (
            df_filtered["no_of_occ_per1"]
            + df_filtered["no_of_occ_per2"]
            + df_filtered["no_of_occ_per3"]
            + df_filtered["no_of_occ_per4"]
            + df_filtered["no_of_occ_core"]
        )
        # Pearson’s correlation
        corr, p_value = pearsonr(df_filtered["no_of_occ"], df_filtered["v_oa"])

        if (
            len(df_filtered["no_of_occ"].unique()) == 1
            or len(df_filtered["v_oa"].unique()) == 1
        ):
            self.df["DCV_type"] = 0  # NO DCV is observed
            self.dcv_msg = "NO DCV"
        elif corr >= 0.3 and p_value <= 0.05:
            self.df["DCV_type"] = 1  # DCV is observed
            self.dcv_msg = "DCV is observed"
        elif corr < 0.3 and p_value > 0.05:
            self.df["DCV_type"] = 0  # NO DCV is observed
            self.dcv_msg = "No DCV"

        self.result = self.df["DCV_type"]

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == 1]),
            "Fail #": len(self.result[self.result == 0]),
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

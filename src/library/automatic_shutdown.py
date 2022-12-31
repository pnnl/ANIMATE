import pandas as pd

from checklib import RuleCheckBase
from functools import reduce


class AutomaticShutdown(RuleCheckBase):
    points = ["hvac_set"]

    def verify(self):
        grouped_df = (
            self.df.groupby(self.df.index.date)["hvac_set"].apply(list).tolist()
        )

        range_df = range(len(grouped_df))
        result = reduce(lambda x, y: x != y, [grouped_df[i] for i in range_df])
        self.result = pd.Series([result for _ in range_df])

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

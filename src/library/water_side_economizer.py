from checklib import RuleCheckBase

import numpy as np


class WaterSideEconomizer(RuleCheckBase):
    points = [
        "T_oa",
        "T_oa_wse_op",
        "P_mech_cool",
        "T_chw_s_sp",
        "T_chw_s",
        "T_chw_ret",
        "tol_sp",
    ]

    def water_side_economizer_check(self, data):
        tol = data["tol_sp"]
        temp_load = data["T_chw_ret"] - data["T_chw_s"]
        if data["P_mech_cool"] == 0:
            if (
                (data["T_chw_s_sp"] - tol < data["T_chw_s"] < data["T_chw_s_sp"] + tol)
                and data["T_oa"] < data["T_oa_wse_op"]
                and temp_load > 0
            ):
                # case 1: water-side economizer is running and meeting 100% of the load
                # - Mechanical cooling is off
                # - There is a load on the loop: CHW return fluid temperature is > CHW supply fluid temperature
                # - CHWS temperature setpoint is met
                # - OA temperature is below the WSE OA temperature threshold
                return True
            elif (
                data["T_chw_s"] > data["T_chw_s_sp"] + tol
                and data["T_oa"] < data["T_oa_wse_op"]
                and temp_load > 0
            ):
                # case 2: water-side economizer is running but not meeting 100% of the load
                # - Mechanical cooling is off
                # - There is a load on the loop: CHW return fluid temperature is > CHW supply fluid temperature
                # - CHWS temperature setpoint is met
                # - OA temperature is below the WSE OA temperature threshold
                return False
            elif temp_load <= 0:
                # case 3: no load, not observed
                return np.nan
            elif data["T_oa"] > data["T_oa_wse_op"]:
                # case 4: OA temp is above threshold
                return np.nan
            else:
                # case 5: Catch exception
                return np.nan
        elif data["P_mech_cool"] > 0:
            if data["T_oa"] < data["T_oa_wse_op"] and temp_load > 0:
                # case 6: water-side economizer should be running and meet 100% of the load
                # - Mechanical cooling is on
                # - There is a load on the loop: CHW return fluid temperature is > CHW supply fluid temperature
                # - OA temperature is below the WSE OA temperature threshold
                return False
            else:
                # case 7: not observed
                return np.nan
        else:
            # case 8: not observed
            return np.nan

    def verify(self):
        self.result = self.df.apply(
            lambda d: self.water_side_economizer_check(d), axis=1
        )

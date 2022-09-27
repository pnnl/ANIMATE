from enum import Enum


class FAILURE_SEVERITY_DENOMINATOR(Enum):
    """Class representing each unit's control setpoint denominator"""

    # magnitude of the denominator is discussed based on our empirical judgement (will be updated if needed)
    TEMPERATURE = 10.0
    PRESSURE = 100.0
    VOLUME_FLOW = 1.0
    ENTHALPY = 10000.0
    ELEC_POWER = 10.0
    NONE_DIMENSION = 1.0  # TO BE DISCUSSED


class PRIORITY_RANKING(Enum):
    """Class representing the control ranking from Rosenberg et al., 2017"""

    ZoneTempControl = 1
    EconomizerHighLimit = 2
    AutomaticOADamperControl = 3
    SupplyAirTempReset = 4
    DemandControlVentilation = 5
    FanStaticPressureResetControl = 6
    HeatPumpSupplementalHeatLockout = 7
    ServiceWaterHeatingSystemControl = 8
    HWReset = 9
    CHWReset = 9
    HeatRejectionFanVariableFlowControlsCells = 10
    WLHPLoopHeatRejectionControl = 11

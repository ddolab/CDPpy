from dataclasses import dataclass

# Experiment Information
@dataclass(frozen=True)
class ExpInfoNamespace:
    CELL_LINE = 'Cell Line'
    RUN_ID = 'ID'
    NAME = 'Name'
    INITIAL_VOLUME = 'Initial Volume (mL)'

# Experiment Data
@dataclass(frozen=True)
class ExpDataNamespace:
    SAMPLE = 'Sample #'
    DATE = 'Date (MM/DD/YY)'
    TIME = 'Time (HH:MM:SS AM/PM)'
    RUN_TIME_D = 'Run Time (day)'
    RUN_TIME_H = 'Run Time (hr)'
    SAMPLE_VOLUME = 'Sample Volume (mL)'
    FEED_MEDIA = 'Feed Media Added (mL)'
    BASE_ADDED = 'Base Added (mL)'
    VOLUME_BEFORE_SAMPLE = 'Volume Before Sampling (mL)'
    VOLUME_AFTER_SAMPLE = 'Volume After Sampling (mL)'
    VOLUME_AFTER_FEED = 'Volume After Feeding (mL)'

# Data about Cell
@dataclass(frozen=True)
class CellNameSpace:
    VIABLE = 'Viable Cell Concentration (10^6 cells/mL)'
    DEAD = 'Dead Cell Concentration (10^6 cells/mL)'
    TOTAL = 'Total Cell Concentration (10^6 cells/mL)'
    VIABILITY = 'Viability (%)'
    IVCC = 'Integral Viable Cell Concentration'
    IVCC_UNIT = '(10^6 cells hr/mL)'
    CUMULATIVE = 'Cumulative Cell Produced'
    CUMULATIVE_UNIT = '(10^6 cells)'
    SP_RATE = 'Specific Growth Rate'
    SP_RATE_UNIT = '(hr^-1)'

# Data about Oxygen
@dataclass(frozen=True)
class OxygenNameSpace:
    MEASURED_UPTAKE_RATE = 'OUR (mmol/L/hr)',
    MEASURED_SP_RATE = 'Specific Oxygen Consumption Rate (mmol/10^9 cells/hr)',
    MEASURED_CONSUMPTION = 'Oxygen Consumed (mmol/L)'

# Data about Product/IgG
@dataclass(frozen=True)
class ProductNameSpace:
    PRODUCTION = 'IgG (mg/L)'
    CUMULATIVE = 'Cumulative IgG Produced'
    CUMULATIVE_UNIT = '(mg)'
    SP_RATE = 'qProduct'
    SP_RATE_UNIT = '(mg/10^9 cells/hr)'

# Data about Metabolite
@dataclass(frozen=True)
class MetaboliteNameSpace:
    CONCE_UNIT = '(mM)'
    CUMULATIVE_UNIT = '(mmol)'
    SP_RATE_UNIT = '(mmol/10^9 cells/hr)'
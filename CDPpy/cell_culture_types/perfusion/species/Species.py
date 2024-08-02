import pandas as pd

from CDPpy.constants import RUN_TIME_DAY_COLUMN, RUN_TIME_HOUR_COLUMN, SPECIES_ABBR

class Species:
    '''
    '''
    def __init__(self, name, run_time_df, dillution_rate, viable_cell_conc) -> None:
        '''
        '''
        # Work with name
        name = name.capitalize() if name != 'IgG' else 'IgG'
        abbr = SPECIES_ABBR[name] if SPECIES_ABBR.get(name) else name.upper()

        # Store variables
        self._name = name
        self._abbr = abbr
        self._run_time = run_time_df
        self._run_time_day = run_time_df[RUN_TIME_DAY_COLUMN].values
        self._run_time_hour = run_time_df[RUN_TIME_HOUR_COLUMN].values
        self._samples = self._run_time_hour.size
        self._dillution_rate = dillution_rate
        self._viable_cell_conc = viable_cell_conc

    @property
    def name(self):
        return self._name
    
    @property
    def abbr(self):
        return self._abbr
    
    @property
    def run_time_day(self):
        return self._run_time_day
    
    @property
    def run_time(self):
        return self._run_time
    
    @property
    def run_time_hour(self):
        return self._run_time_hour
    
    @property
    def samples(self):
        return self._samples
    
    @property
    def dillution_rate(self):
        return self._dillution_rate
    
    @property
    def viable_cell_conc(self):
        return self._viable_cell_conc


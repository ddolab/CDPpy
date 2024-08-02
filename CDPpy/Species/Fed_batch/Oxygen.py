import numpy as np

from CDPpy.helper import get_measurement_indices
from .Species import Species

#from ...in_process.OxygenMixin import OxygenMixin
#from ...post_process.polynomial.OxygenMixin import OxygenMixin as Polynomial

class Oxygen(Species, 
             #OxygenMixin, 
             # Polynomial
             ):
    '''
    Oxygen class.

    Attribute
    ---------
        name : str
            name of species.
    '''
    # Constructor
    def __init__(self, name, samples, run_time_day, run_time_hour, 
                 volume_before_sampling, volume_after_sampling, feed_media_added,
                 viable_cell_conc,
                 measured_sp_rate, measured_uptake_rate, consumption):
        '''
        Parameters
        ---------
            name : str
                name of species.
            measured_data : python object
                MeasuredData object.
        '''
        # Constructor for Species Class
        super().__init__(name, samples, run_time_day, run_time_hour, 
                         volume_before_sampling, volume_after_sampling, feed_media_added, 
                         viable_cell_conc)

        # Work with parameters
        '''df = measured_data.param_df
        rate = df['sp_oxygen_consumption_rate_(mmol/10^9_cells/hr)']
        our = df['our_(mmol/L/hr)']
        consumption = df['oxygen_consumed_(mmol/L)']'''
        
        # Get indices of the measurements from the concentration
        conc = consumption['value']
        idx = get_measurement_indices(conc)

        # Members
        self._idx = idx
        self._measured_sp_rate = measured_sp_rate   # Measured oxygen consumption rate
        self._measured_uptake_rate = measured_uptake_rate                 # Measured oxygen Up Take Rate
        self._measured_consumption = consumption # Measured oxygen consumption
    
    @property
    def measurement_index(self):
        return self._idx
    @property
    def measured_uptake_rate(self):
        """Oxygen Uptake Rate in Measured Data (mmol/L/hr)"""
        return self._measured_uptake_rate
    @property
    def measured_sp_rate(self):
        """SP. Oxygen Consumption Rate in Measured Data (mmol/109cell/hr)"""
        return self._measured_sp_rate
    @property
    def measured_consumption(self):
        """Oxygen Consumption in Measured Data (mmol/L)"""
        return self._measured_consumption

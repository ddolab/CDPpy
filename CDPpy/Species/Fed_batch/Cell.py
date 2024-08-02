import pandas as pd
import numpy as np

from CDPpy.helper import get_measurement_indices
from CDPpy.in_process.Fed_batch.CellMixin import CellMixin as Inprocess
from .Species import Species

#from ...in_process.CellMixin import CellMixin
#from ...post_process.polynomial.CellMixin import CellMixin as Polynomial
#from ...post_process.rolling_window_polynomial.LogisticGrowthMixin import LogisticGrowthMixin

class Cell(Species, Inprocess,
           #Polynomial, 
           #LogisticGrowthMixin
           ):
    '''Cell class.

    Attributes
    ---------
        name : str
            name of species.
    '''
    # Constructor
    def __init__(self, name, samples, run_time_day, run_time_hour, 
                 volume_before_sampling, volume_after_sampling, feed_media_added,
                 viable_cell_conc, dead_cell_conc, total_cell_conc):
        '''
        Parameters
        ---------
            name : str
                name of species.
        '''
        # Constructor for Spcies Class
        super().__init__(name, samples, run_time_day, run_time_hour, 
                         volume_before_sampling, volume_after_sampling, feed_media_added, 
                         viable_cell_conc)
        
        # Calculate viability
        value = viable_cell_conc['value'].values / total_cell_conc['value'].values * 100
        viab = viable_cell_conc.copy()
        viab.index.name = 'Viability'
        viab['value'] = value
        viab['unit'] = '%'

        # Get indices of the measurement from the viable cell concentration
        xv = self._viable_cell_conc['value']
        idx = get_measurement_indices(xv)

        # Class Members
        self._idx = idx
        self._dead_cell_conc = dead_cell_conc
        self._total_cell_conc = total_cell_conc
        self._viability = viab

    @property
    def measurement_index(self):
        return self._idx
    @property
    def dead_cell_conc(self):
        return self._dead_cell_conc
    @property
    def total_cell_conc(self):
        return self._total_cell_conc
    @property
    def viability(self):
        return self._viability
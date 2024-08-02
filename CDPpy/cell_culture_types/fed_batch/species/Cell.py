import pandas as pd
import numpy as np

from CDPpy.helper import get_measurement_indices
from CDPpy.cell_culture_types.fed_batch.in_process import CellMixin as Inprocess
from CDPpy.cell_culture_types.fed_batch.post_process.polynomial import CellMixin as Polynomial
from CDPpy.cell_culture_types.fed_batch.post_process.rolling_window_polynomial import LogisticGrowthMixin as LogisticGrowoth
from CDPpy.cell_culture_types.fed_batch.post_process.rolling_window_polynomial import CellMixin as RollingPolynomial
from .Species import Species

class Cell(Species, Inprocess, Polynomial, RollingPolynomial):
    '''Cell class.
    Attributes
    ---------
    '''
    # Constructor
    def __init__(self, name, param_data):
        '''
        Parameters
        ---------
        '''
        # Constructor for Spcies Class
        super().__init__(name, param_data)

        viable_cell_conc = param_data['viable_cell']
        total_cell_conc = param_data['total_cell']
        dead_cell_conc = param_data['dead_cell']
        
        # Calculate viability
        value = viable_cell_conc['value'].values / total_cell_conc['value'].values * 100
        viab = viable_cell_conc.copy()
        viab.index.name = 'Viability'
        viab['value'] = value
        viab['unit'] = '%'

        # Class Members
        self._dead_cell_conc = dead_cell_conc
        self._total_cell_conc = total_cell_conc
        self._viability = viab

    @property
    def measurement_index(self):
        return self.vcc_index
    
    @property
    def dead_cell_conc(self):
        return self._dead_cell_conc
    
    @property
    def total_cell_conc(self):
        return self._total_cell_conc
    
    @property
    def viability(self):
        return self._viability
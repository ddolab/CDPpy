import pandas as pd
import numpy as np

from CDPpy.helper import get_measurement_indices
from CDPpy.cell_culture_types.fed_batch.in_process import MetaboliteMixin as Inprocess
from CDPpy.cell_culture_types.fed_batch.post_process.polynomial import MetaboliteMixin as Polynomial
from CDPpy.cell_culture_types.fed_batch.post_process.rolling_window_polynomial import MetaboliteMixin as RollingPolynomial
from .Species import Species

# from CCDPApy.in_process.Fed_batch.MetaboliteMixin import MetaboliteMixin as Inprocess

class Metabolite(Species, Inprocess, Polynomial, RollingPolynomial):
    '''
    Metabolite class.
    Attributes
    ---------
    '''             
    def __init__(self, name, 
                 param_data, 
                 separate_feed,
                 conc_before_feed, 
                 conc_after_feed, 
                 feed_conc, 
                 measured_cumulative_conc):
        '''
        Parameters
        ---------
        '''
        super().__init__(name, param_data=param_data)

        # Check measured cumulative concentration
        measured_cumulative_flag = False if measured_cumulative_conc is None else True
        
        # Get indices of the measurements from the concentration
        if measured_cumulative_flag:
            conc = measured_cumulative_conc['value']
        else:
            conc = conc_before_feed['value']
        idx = get_measurement_indices(conc)

        # Get the same index in both lists
        set1 = set(idx)
        set2 = set(self.vcc_index)
        common_idx = list(set1.intersection(set2))
        
        # Class Members
        self._idx = idx
        self._common_idx = common_idx
        self._separate_feed = separate_feed
        self._separate_feed_sum = param_data['feed_volume_sum']
        self._conc_before_feed = conc_before_feed
        self._conc_after_feed = conc_after_feed
        self._feed_conc = feed_conc
        self._measured_cumulative_conc = measured_cumulative_conc
        self._measured_cumulative_flag = False if measured_cumulative_conc is None else True
    
    @property
    def index(self):
        return self._idx
    
    @property
    def measurement_index(self):
        return self._common_idx
    
    @property
    def conc_before_feed(self):
        return self._conc_before_feed
    
    @property
    def conc_after_feed(self):
        return self._conc_after_feed
    
    @property
    def feed_conc(self):
        return self._feed_conc
    
    @property
    def measured_cumulative_conc(self):
        return self._measured_cumulative_conc
    
    @property
    def measured_cumulative_flag(self):
        return self._measured_cumulative_flag
    
    @property
    def separate_feed(self):
        return self._separate_feed
    
    @property
    def separate_feed_sum(self):
        return self._separate_feed_sum
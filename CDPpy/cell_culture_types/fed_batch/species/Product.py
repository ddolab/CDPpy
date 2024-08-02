import numpy as np

from CDPpy.helper import get_measurement_indices
from CDPpy.cell_culture_types.fed_batch.in_process import ProductMixin as Inprocess
from CDPpy.cell_culture_types.fed_batch.post_process.polynomial import ProductMixin as Polynomial
from CDPpy.cell_culture_types.fed_batch.post_process.rolling_window_polynomial import ProductMixin as RollingPolynomial
from .Species import Species

class Product(Species, Inprocess, Polynomial, RollingPolynomial):
    '''
    Product/IgG class.

    Attribute
    ---------
    '''
    # Constructor
    def __init__(self, name, param_data):
        '''
        Parameters
        ---------
        '''
        super().__init__(name, param_data)
        
        # Get indices of the measurements from the concentration
        production = param_data['production']
        conc = production['value']
        idx = get_measurement_indices(conc)

        # Get the same index in both lists
        set1 = set(idx)
        set2 = set(self.vcc_index)
        common_idx = list(set1.intersection(set2))

        # Class Members
        self._idx = idx
        self._common_idx = common_idx
        self._production = production

    @property
    def index(self):
        return self._idx
    
    @property
    def measurement_index(self):
        return self._common_idx
    
    @property
    def production(self):
        return self._production
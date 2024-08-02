import numpy as np

from CDPpy.helper import get_measurement_indices
from CDPpy.in_process.Fed_batch.ProductMixin import ProductMixin as Inprocess
from .Species import Species

#from ...post_process.polynomial.ProductMixin import ProductMixin as Polynomial
#from ...post_process.rolling_window_polynomial.ProductMixin import ProductMixin as Rolling

class Product(Species, Inprocess,
              #Polynomial, 
              #Rolling
              ):
    '''
    Product/IgG class.

    Attribute
    ---------
        name : str
            name of species.
        measured_data : python object
                MeasuredData object.
    '''
    # Constructor
    def __init__(self, name, samples, run_time_day, run_time_hour, 
                 volume_before_sampling, volume_after_sampling, feed_media_added,
                 viable_cell_conc, production):
        '''
        Parameters
        ---------
            name : str
                name of species.
        '''
        # Constructor for Species
        super().__init__(name, samples, run_time_day, run_time_hour, 
                         volume_before_sampling, volume_after_sampling, feed_media_added, 
                         viable_cell_conc)
        
        # Get indices of the measurements from the concentration
        conc = production['value']
        idx = get_measurement_indices(conc)

        # Work with parameters
        '''df = measured_data.param_df
        conc = df['IgG_(mg/L)']
        idx = conc[conc.notnull()].index  # Measurent Index
        t = df['run_time_(hrs)'].values[idx]    # original run time (hour)'''
        # Calculate Mid Time from Original Run time
        # time_mid = np.array([0.5 * (t[i] + t[i+1]) for i in range(len(t)-1)])

        # Class Members
        self._idx = idx
        self._production = production

    @property
    def measurement_index(self):
        return self._idx
    @property
    def production(self):
        return self._production
        


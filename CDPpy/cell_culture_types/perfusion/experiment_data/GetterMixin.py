class GetterMixin:
    '''
    '''    
    @property
    def cell_conc(self):
        return self._cell_conc
    
    def get_conc_data(self):
        '''get measured data for concentration.'''
        return self._conc_data

    def get_feed_conc(self):
        '''get feed concentration data.'''
        return self._feed_conc_data
    
    def get_polynomial_degree(self):
        '''get polynomial degreee data.'''
        return self._polynomial_degree_data
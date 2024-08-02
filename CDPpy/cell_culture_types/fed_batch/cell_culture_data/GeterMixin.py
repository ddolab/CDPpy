class GetterMixin:
    ''''''
    def get_pre_process_data(self):
        '''get dictionary for all dataset.'''
        return self._data_set
    
    def get_processed_data(self):
        ''''''
        return self._processed_data
    
    def get_cell_data(self):
        return self._cell_data
    
    def get_metabolite_data(self):
        return self._metabolite_data

    def get_measured_data(self):
        '''get measured data.'''
        return self._exp_data
    
    def get_conc_before_feed(self):
        '''get measured data for concentration before feeding.'''
        return self._conc_before_feed_data
    
    def get_conc_after_feed(self):
        '''get measured data for concentration before feeding.'''
        return self._conc_after_feed_data
    
    def get_measured_cumulative_conc(self):
        '''get measured data for calculated cumulative concentration.'''
        return self._measured_cumulative_data

    def get_feed_conc(self):
        '''get feed concentration data.'''
        return self._feed_conc_data
    
    def get_polynomial_degree(self):
        '''get polynomial degreee data.'''
        return self._polynomial_degree_data
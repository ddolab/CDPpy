class GetterMixin:
    def get_cell_line_handles(self, cell_line_name=None):
        ''''''
        if cell_line_name:
            return self._cell_line_handles[cell_line_name]
        else :
            return self._cell_line_handles
    
    def get_experiment_ids(self):
        ''''''
        id_list = []
        for cell_line_handler in self._cell_line_handles.values():
            id_list += list(cell_line_handler.get_experiment_handle())
        return id_list
    
    def get_all_data(self):
        '''get dictionary for all dataset.'''
        return self._data_set
    
    def get_cell_data(self):
        return self._cell_data
    
    def get_metabolite_data(self):
        return self._metabolite_data

    def get_measured_data(self):
        '''get measured data.'''
        return self._data
    
    def get_conc_data(self):
        '''get measured data for concentration.'''
        return self._conc_data
    
    def get_feed_conc(self):
        '''get feed concentration data.'''
        return self._feed_data
    
    def get_polynomial_degree(self):
        '''get polynomial degreee data.'''
        return self._polynomial_degree_data
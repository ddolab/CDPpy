class PerfusionParameters:
    '''Store key parameters for a fed-batch cell culture data processing.'''
    def __init__(self, 
                 cell_line_name:str,
                 regression_method=None, 
                 polynomial_degreee=None,
                 rolling_polynomial_degree=None, rolling_polynomial_window=None
                 ) -> None:
        '''
        Attributes
        ----------
            
        '''
        self._cell_line_name = cell_line_name

        if not isinstance(regression_method, list):
            regression_method = [regression_method]

        if 'polynomial' in regression_method:
            self._polynomial = True
        else:
            self._polynomial = False

        if 'rolling_window_polynomial' in regression_method:
            self._rolling_window_polynomial = True
            if rolling_polynomial_degree:
                self._rolling_polynomial_degree = rolling_polynomial_degree
            else:
                self._rolling_polynomial_degree = 3
            if rolling_polynomial_window:
                self._rolling_polynomial_window = rolling_polynomial_window
            else:
                self._rolling_polynomial_window = 6
        else:
            self._rolling_window_polynomial = False

    @property
    def cell_line_name(self):
        return self._cell_line_name
    
    @cell_line_name.setter
    def cell_line_name(self, cell_line_name):
        self._cell_line_name = cell_line_name

    @property
    def polynomial(self):
        return self._polynomial
    
    @polynomial.setter
    def polynomial(self, polynomial):
        self._polynomial = polynomial

    @property
    def rolling_window_polynomial(self):
        return self._rolling_window_polynomial
    
    @rolling_window_polynomial.setter
    def rolling_window_polynomial(self, rolling_window_polynomial):
        self._rolling_window_polynomial = rolling_window_polynomial
    
    @property
    def rolling_polynomial_degree(self):
        return self._rolling_polynomial_degree
    
    @rolling_polynomial_degree.setter
    def rolling_window_polynomial(self, degree):
        self._rolling_polynomial_degree = degree
    
    @property
    def rolling_polynomial_window(self):
        return self._rolling_polynomial_window
    
    @rolling_polynomial_window.setter
    def rolling_window_polynomial(self, window):
        self._rolling_polynomial_window = window

    def __repr__(self) -> str:
        return('\n'.join([f'Cell Line: {self._cell_line_name}',
                         f'Regression Methods',
                         f'     Polynomial: {self._polynomial}',
                         f'     Rolling window polynomial {self._rolling_window_polynomial}',
                         ]))
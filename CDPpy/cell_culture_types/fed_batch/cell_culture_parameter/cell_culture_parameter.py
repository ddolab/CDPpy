class FedBatchParameters:
    '''Store key parameters for a fed-batch cell culture data processing.'''
    def __init__(self, 
                 cell_line_name:str, 
                 use_feed_concentration:bool, 
                 use_concentration_after_feed:bool, 
                 regression_method=['polynomial', 'rolling_window_polynomial'], 
                 polynomial_degreee=None,
                 rolling_polynomial_degree=None, rolling_polynomial_window=None) -> None:
        '''
        Attributes
        ----------
            
        '''
        self._cell_line_name = cell_line_name
        self._use_feed_conc = use_feed_concentration
        self._use_conc_after_feed = use_concentration_after_feed

        if not isinstance(regression_method, list):
            regression_method = [regression_method]

        if 'polynomial' in regression_method:
            self._polynomial = True
        else:
            self._polynomial = False

        if 'rolling_window_polynomial' in regression_method:
            self._rolling_window_polynomial = True
            # if rolling_polynomial_degree:
            self._rolling_polynomial_degree = rolling_polynomial_degree
            # else:
            #     self._rolling_polynomial_degree = 3
            # if rolling_polynomial_window:
            self._rolling_polynomial_window = rolling_polynomial_window
            # else:
            #     self._rolling_polynomial_window = 6
        else:
            self._rolling_polynomial_degree = None
            self._rolling_polynomial_window = None
            self._rolling_window_polynomial = False
        

    @property
    def cell_line_name(self):
        return self._cell_line_name
    
    @cell_line_name.setter
    def cell_line_name(self, cell_line_name):
        self._cell_line_name = cell_line_name

    @property
    def use_feed_conc(self):
        return self._use_feed_conc
    
    @use_feed_conc.setter
    def use_feed_conc(self, use_feed_concentration):
        self._use_feed_conc = use_feed_concentration

    @property
    def use_conc_after_feed(self):
        return self._use_conc_after_feed

    @use_conc_after_feed.setter
    def use_conc_after_feed(self, use_concentration_after_feed):
        self._use_conc_after_feed = use_concentration_after_feed

    @property
    def polynomial(self):
        return self._polynomial
    
    @polynomial.setter
    def polynomial(self, poly):
        self._polynomial = poly
    
    @property
    def rolling_window_polynomial(self):
        return self._rolling_window_polynomial
    
    @rolling_window_polynomial.setter
    def rolling_window_polynomial(self, rolling_window_poly):
        self._rolling_window_polynomial = rolling_window_poly
    
    @property
    def rolling_polynomial_degree(self):
        return self._rolling_polynomial_degree
    
    @rolling_polynomial_degree.setter
    def rolling_polynomial_degree(self, degree):
        self._rolling_polynomial_degree = degree
    
    @property
    def rolling_polynomial_window(self):
        return self._rolling_polynomial_window
    
    @rolling_polynomial_window.setter
    def rolling_polynomial_window(self, window):
        self._rolling_polynomial_window = window

    def __repr__(self) -> str:
        return('\n'.join([f'Cell Line: {self._cell_line_name}',
                         f'Feed concentration will be used: {self._use_feed_conc}',
                         f'Concentration after feeding will be used: {self._use_conc_after_feed}',
                         f'Regression Methods',
                         f'     Polynomial: {self._polynomial}',
                         f'     Rolling window polynomial {self._rolling_window_polynomial}']))
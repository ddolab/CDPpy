
class GetterMixin:
    '''
    '''
    '''def get_sp_rate(self, method):
        """
        Get Get SP. Rate.

        Parameters
        ----------
            method : str
                The method used to calculate SP. rate.
                'towpt', 'polyreg', 'rollreg'.

        """
        if (method=='twopt'):
            return self._sp_rate
        elif (method=='polyreg'):
            return self._polyreg_sp_rate
        elif (method=='rollreg'):
            return self._rollpolyreg_sp_rate
        else:
            print('wrong method parameter.')
            return None

    def get_rollreg_order(self):
        return  self._rollpolyreg_order
    
    def get_rollreg_window(self):
        return  self._rollpolyreg_window

    def get_polyorder(self):
        return self._polyorder

    def get_polyfit_cumulative(self):
        return self._polyfit

    def get_polyreg_cumulative(self):
        return self._polyreg_cumulative'''



class SetterMixin:
    '''
    '''
    def set_method_flag(self, method, flag):
        '''
        Set a flag for the regression method True.

        Parameters
        ----------
            method : str
                Pass 'cumulative', 'twopt', 'polyreg', 'rollreg'.
        '''
        if method=='cumulative':
            self._in_process_flag = flag
        elif method=='twopt':
            self._twopt_flag = flag
        elif method=='polyreg':
            self._polyreg_flag = flag
        elif method=='rollreg':
            self._rollreg_flag = flag
        else:
            pass

    def set_sp_rate(self, sp_rate):
        '''
        Set the SP. rate.

        Parameters
        ----------
            sp_rate : pd.Series
        '''
        self._sp_rate = sp_rate
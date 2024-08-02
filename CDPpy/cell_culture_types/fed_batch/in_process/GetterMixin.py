import pandas as pd

class GetterMixin:
    '''Getter Mixin Class for In-Process
    '''
    @property
    def cumulative_conc(self):
        return self._cumulative_conc

    @cumulative_conc.setter
    def cumulative_conc(self, cumulative_conc_df):
        self._cumulative_conc = cumulative_conc_df

    @property
    def sp_rate(self):
        return self._sp_rate
    
    @sp_rate.setter
    def sp_rate(self, sp_rate_data):
        self._sp_rate = sp_rate_data
    
    @property
    def conc(self):
        return self._conc

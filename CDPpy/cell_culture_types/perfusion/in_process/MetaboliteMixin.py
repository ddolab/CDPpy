import numpy as np
import pandas as pd

from CDPpy.constants import SPECIES_STATE

from .GetterMixin import GetterMixin
from .Equation import production

class MetaboliteMixin(GetterMixin):
    '''
    '''
    def in_process(self):
        '''
        '''
        # Get run time dataframe
        run_time = self.run_time

        # Cumulative production/consumption
        s = self.cumulative_calc()
        self._cumulative_conc = pd.concat([run_time, s], axis=1)

        # SP. rate
        self._sp_rate = pd.DataFrame()
        
    def cumulative_calc(self) -> pd.DataFrame:
        '''Calculate cumulative consumption or production of a metabolite.
        Parameters
        ---------
            t : numpy array
                Time (hr)
            c : numpy array
                Concentration (mg/mL) or (mmol/L).
            d : numpy array
                Dillution rate at (hr^1).
                Flow rate (L/hr) / Culture volume (L)
            f : numpy array
                Feed concentration (mg/mL) or (mmol/L).
        Returns
            s : pandas DataFrame
                cumulative consumption or production (mg/mL) or (mmol/L).
        '''
        t = self.run_time_hour
        c = self.conc['value'].values
        d = self.dillution_rate['value'].values
        f = self.feed_conc['value'].values
        unit = self.conc['unit'].iat[0]

        # Check if there is feed concentration
        if np.isnan(f).all():
            f = np.zeros_like(f)

        s = np.zeros_like(t)
        for i in range(1, t.size):
            s_i = production(c[i-1], c[i], t[i-1], t[i], d[i], f[i])
            s[i] = s[i-1] + s_i

        # check if species is consumed or produced
        if SPECIES_STATE[self.name]=='Consumed':
            s *= -1

        s = pd.DataFrame(data=s, columns=['value'])
        s['unit'] = unit
        s['state'] = SPECIES_STATE[self.name]
        s['method'] = 'twoPoint'
        return s
        
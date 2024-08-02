import numpy as np
import pandas as pd

from .GetterMixin import GetterMixin
from .Equation import production, death_rate, growth_rate

class CellMixin(GetterMixin):
    '''
    '''
    def in_process(self):
        ''''''
        # Get run time dataframe
        run_time = self.run_time

        # Cumulative production
        s = self.cumulative_calc()
        self._cumulative_conc = pd.concat([run_time, s], axis=1)

        # Growth rate and death rate
        g_rate, d_rate = self.sp_rate_calc()
        self._sp_rate = pd.concat([run_time, g_rate], axis=1)
        self._sp_death_rate = pd.concat([run_time, d_rate], axis=1)
        
    def cumulative_calc(self) -> pd.DataFrame:
        '''Calculate cumulative production of the cell.
        Parameters
        ---------
            t : numpy array
                Time (hr)
            c : numpy array
                Viable cell concentration (10^6 cells/mL).
            d : numpy array
                Dillution rate at (hr^1).
                Flow rate (L/hr) / Culture volume (L)
        Returns
            s : pandas DataFrame
                cumulative consumption or production (10^6 cells/mL).
        '''
        t = self.run_time_hour
        c = self.viable_cell_conc['value'].values
        d = self.dillution_rate['value'].values
        unit = self.viable_cell_conc['unit'].iat[0]

        s = np.zeros_like(t)
        for i in range(1, t.size):
            s_i = production(c[i-1], c[i], t[i-1], t[i], d[i], 0)
            s[i] = s[i-1] + s_i
        
        s = pd.DataFrame(data=s, columns=['value'])
        s['unit'] = unit
        s['method'] = 'twoPonint'
        s.index.name = 'Cumulatve Production'
        return s
    
    def sp_rate_calc(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        '''Calculate the specific growth rate and death rate of the cell.
        Parameters
        ---------
            t : numpy array
                Time (hr)
            xd : numpy array
                Dead cell concentration (10^6 cells/mL).
            xv : numpy array
                Viable cell concentration (10^6 cells/mL).
            d : numpy array
                Dillution rate at (hr^1).
                Flow rate (L/hr) / Culture volume (L)
        Returns
            g_rate, d_rate : tupple of pandas DataFrames
                Specific growth rate (hr^1) and death rate (hr^1).
        '''
        t = self.run_time_hour
        b = self._bleeding_ratio
        xd = self.dead_cell_conc['value'].values
        xv = self.viable_cell_conc['value'].values
        d = self.dillution_rate['value'].values

        dr, gr = np.zeros_like(t), np.zeros_like(t)
        dr.fill(np.nan)
        gr.fill(np.nan)
        for i in range(1, t.size):
            dr[i] = death_rate(b[i-1], xd[i-1], xd[i], xv[i-1], xv[i], t[i-1], t[i], d[i-1], d[i])
            gr[i] = growth_rate(b[i-1], xv[i-1], xv[i], t[i-1], t[i], d[i-1], d[i], dr[i])
        
        d_rate = pd.DataFrame(data=dr, columns=['value'])
        d_rate['unit'] = '(hr^-1)'
        d_rate['method'] = 'twoPoint'
        d_rate.index.name = 'Specific death rate'

        g_rate = pd.DataFrame(data=gr, columns=['value'])
        g_rate['unit'] = '(hr^-1)'
        g_rate['method'] = 'twoPoint'
        g_rate.index.name = 'Specific growth rate'
        return g_rate, d_rate
    
    @property
    def growth_rate(self):
        return self._sp_rate
    
    @property
    def death_rate(self):
        return self._sp_death_rate
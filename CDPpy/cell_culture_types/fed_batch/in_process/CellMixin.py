import pandas as pd
import numpy as np

from .GetterMixin import GetterMixin

from .equation import integral_viable_cell, cell_production, growth_rate

from CDPpy.constants import CellNameSpace
from CDPpy.constants import RUN_TIME_HOUR_COLUMN

CONSTANTS = CellNameSpace()

class CellMixin(GetterMixin):
    '''
    '''
    # Call methods
    def in_process(self):
        '''Caluculate in-process data for cell.
        '''
        # Get run time dataframe
        run_time = self.run_time

        # IVCC
        ivcc = self.integral_viable_cell_calc()
        self._ivcc = pd.concat([run_time, ivcc], axis=1)

        # Cumulative Consumption/Production
        s = self.cumulative_calc()
        self._cumulative_conc = pd.concat([run_time, s], axis=1)

        # Specific rate
        r = self.sp_rate_calc()
        self._sp_rate = pd.concat([run_time, r], axis=1)

        # Viable, Total concentrations and Viability
        viable = pd.concat([run_time, self._viable_cell_conc], axis=1)
        viable['state'] = 'Viable'
        total = pd.concat([run_time, self._total_cell_conc], axis=1)
        total['state'] = 'Total'
        viab = pd.concat([run_time, self._viability], axis=1)
        viab['state'] = 'Viability'
        self._conc = pd.concat([viable, total, viab], axis=0).reset_index(drop=True)


    def integral_viable_cell_calc(self) -> pd.DataFrame:
        '''Calculate Integral of Viable Cell
        Parameters
        ---------
            idx : numpy array
                Indices of measurements.
            c : numpy array
                Viable cell concentration (10^6 cells/mL).
            t : numpy array
                Time (hr)
        Returns
            s : pandas DataFrame
                Integral of viable cell concentration (10^6 cells hr/mL).
        '''
        idx = self.measurement_index
        c = self.viable_cell_conc['value'].values[idx]
        t = self.run_time_hour[idx]

        # Initialize
        s = np.zeros(self.samples)
        for i in range(1, len(t)):
            s_i = integral_viable_cell(c[i-1], c[i], t[i-1], t[i])
            s[idx[i]] = s[idx[i-1]] + s_i

        s = pd.DataFrame(data=s, columns=['value'])
        s['unit'] = CONSTANTS.IVCC_UNIT
        s.index.name = CONSTANTS.IVCC
        return s
        
    def cumulative_calc(self):
        '''Calculate cumulative production of the cell.
        Parameters
        ---------
            idx : numpy array
                Indices of measurements.
            c : numpy array
                Viable cell concentration (10^6 cells/mL).
            v1 : numpy array
                Culture volume before sampling (mL).
            v2 : numpy array
                Culture volume after sampling (mL).
        Returns
            s : pandas DataFrame
                Cumulative production (10^6 cells).
        '''
        idx = self.measurement_index
        c = self.viable_cell_conc['value'].values[idx]
        v1 = self.volume_before_sampling[idx]
        v2 = self.volume_after_sampling[idx]

        # Initialize
        s = np.zeros(self.samples)
        s.fill(np.nan)
        s[0] = 0.0

        for i in range(1, len(idx)):
            s_i = cell_production(c[i-1], c[i], v1[i], v2[i-1])
            s[idx[i]] = s_i + s[idx[i-1]]
        
        s = pd.DataFrame(data=s, columns=['value'])
        s['unit'] = CONSTANTS.CUMULATIVE_UNIT
        s['method'] = 'twoPoint'
        s.index.name = CONSTANTS.CUMULATIVE
        return s

    def sp_rate_calc(self):
        '''Calculates Specific growth rate.
        Parameters
        ---------
            idx : numpy array
                Indices of measurements.
            s : numpy array
                Cumulative cell concentration (10^6 cells).
            t : numpy array
                Time (hr).
            v1 : numpy array
                Culture volume before sampling (mL).
            v2 : numpy array
                Culture volume after sampling (mL).
        Returns
            r : pandas DataFrame
                Specific growth rate (hr^1).
        '''
        idx = self.measurement_index
        t = self.run_time_hour[idx]
        xv = self.viable_cell_conc['value'].values[idx]                   # vialbe cell concentration (10e6 cells/ml)
        s = self.cumulative_conc['value'].values[idx]            # Cumulative Cell Concentraion (10e6 cells/mL)
        v1 = self.volume_before_sampling[idx]
        v2 = self.volume_after_sampling[idx]

        # Initialize
        r = np.zeros(self.samples)
        r.fill(np.nan)
        for i in range(1, len(t)):
            r[idx[i]] = growth_rate(s[i-1], s[i], xv[i-1], xv[i], v1[i], v2[i-1], t[i-1], t[i])
        r = pd.DataFrame(data=r, columns=['value'])
        r['unit'] = CONSTANTS.SP_RATE_UNIT
        r['method'] = 'twoPoint'
        r.index.name = CONSTANTS.SP_RATE
        return r

    @property
    def integral_viable_cell_conc(self):
        return self._ivcc
    
    @integral_viable_cell_conc.setter
    def integral_viable_cell_conc(self, ivcc):
        self._ivcc = ivcc
    
    @property
    def growth_rate(self):
        return self._sp_rate
    
    @growth_rate.setter
    def growth_rate(self, growth_rate):
        self._sp_rate = growth_rate
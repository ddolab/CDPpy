import pandas as pd
import numpy as np

from .GetterMixin import GetterMixin
from CDPpy.constants import ProductNameSpace

CONSTANTS = ProductNameSpace()

class ProductMixin(GetterMixin):
    def in_process(self):
        ''''''
        run_time = self.run_time
        c = self.production
        self._conc = pd.concat([run_time, c], axis=1)
        s = self.cumulative_calc()
        self._cumulative_conc = pd.concat([run_time, s], axis=1)
        r = self.sp_rate_calc()
        self._sp_rate = pd.concat([run_time, r], axis=1)
    
    def cumulative_calc(self) -> pd.DataFrame:
        ''' Calculate cumulative Product/IgG produced.
        IgG produced = xv(t) * v(t) - xv(t-1) * v(t-1)
        '''
        idx = self.measurement_index
        c = self.production['value'].values[idx]# IgG concentration (10e6 cells/ml)
        v1 = self.volume_before_sampling[idx]# Culture Volume Bfore sampling (ml)
        v2 = self.volume_after_sampling[idx]# Culture Volume After feeding (ml)
        
        # Initialize
        s = np.zeros(self.samples)
        s.fill(np.nan)
        s[idx[0]] = 0

        for i in range(1, len(idx)):
            s_i = (c[i] * v1[i] - c[i-1] * v2[i-1]) / 1000
            s[idx[i]] = s[idx[i-1]] + s_i

        s = pd.DataFrame(data=s, columns=['value'])
        s['unit'] = CONSTANTS.CUMULATIVE_UNIT
        s['state'] = 'Produced'
        s['method'] = 'twoPoint'
        s.index.name = CONSTANTS.CUMULATIVE
        return s

    def sp_rate_calc(self) -> pd.DataFrame:
        '''Calculate specific rate of Product/IgG.
        '''
        idx = self.measurement_index
        s = self.cumulative_conc['value'].values[idx]           # Substrate Concentration (mM)
        t = self.run_time_hour[idx]        # Run Time (hrs)
        v1 = self.volume_before_sampling[idx]   # Culture Volume Before Sampling (mL)
        v2 = self.volume_after_sampling[idx]    # Culture Volume Before sampling (mL)
        xv = self.viable_cell_conc['value'].values[idx]                  # Viable Cell Concentration (10e6 cells/mL)

        r = np.zeros(self.samples)
        r.fill(np.nan)

        for i in range(1, len(idx)):
            x = (s[i] - s[i-1]) * 1000
            y = xv[i] * v1[i] + xv[i-1] * v2[i-1]
            r[idx[i]] = x / (y * 0.5 * (t[i] - t[i-1]))
        r = pd.DataFrame(data=r, columns=['value'])
        r['unit'] = CONSTANTS.SP_RATE_UNIT
        r['method'] = 'twoPoint'
        r.index.name = CONSTANTS.SP_RATE
        return r

    @property
    def conc(self):
        return self._conc
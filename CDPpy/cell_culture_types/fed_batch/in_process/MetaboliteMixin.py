import pandas as pd
import numpy as np

from .GetterMixin import GetterMixin
from CDPpy.constants import MetaboliteNameSpace, ExpDataNamespace
from CDPpy.constants import SPECIES_STATE, RUN_TIME_HOUR_COLUMN

CONSTANTS = MetaboliteNameSpace()
KEY = ExpDataNamespace()

class MetaboliteMixin(GetterMixin):
    '''
    '''
    # Call Initialize Method
    def in_process(self, use_feed_conc, use_conc_after_feed):
        ''' Calculate In-Proccess for metabolites.
        '''
        self._use_feed_conc = use_feed_conc
        self._use_conc_after_feed = use_conc_after_feed

        # Calculate concentration after feeding
        if not use_conc_after_feed:
            self._conc_after_feed = self.conc_after_feeding_calc()

        # If measured data already has the calculated cumulative consumption/production
        if (self.measured_cumulative_flag):
            s = self.measured_cumulative_conc
            s['state'] = SPECIES_STATE[self.name]
        else:
            # IF Experiments measure the feed Concentrations
            if (use_feed_conc):
                s = self.cumulative_calc_by_feed()
            # IF Experiments measure the concentraions after feeding
            elif (use_conc_after_feed):
                s = self.cumulative_calc_by_conc_after_feed()
            else:
                s = self.cumulative_calc_without_feed()

        run_time = self.run_time
            
        # Cumulative Consumption/Production
        self._cumulative_conc = pd.concat([run_time, s], axis=1)

        # Specific rate
        r = self.sp_rate_calc()
        self._sp_rate = pd.concat([run_time, r], axis=1)

        # Concat concentrations before and after feeding
        c1 = pd.concat([run_time, self.conc_before_feed], axis=1)
        c2 = pd.concat([run_time, self.conc_after_feed], axis=1)
        conc = pd.concat([c1, c2], axis=0)
        self._conc = conc.sort_values(by=[RUN_TIME_HOUR_COLUMN], kind='stable', ignore_index=True)

    def conc_after_feeding_calc(self) -> pd.DataFrame:
        ''' Calculate concentration after feeding.
        '''
        idx = self.measurement_index
        s = self.conc_before_feed['value'].values[idx]# Substrate Concentration (mM)
        f_media = self.feed_media_added[idx]# Feed Flowrate (ml/hr)
        v = self.volume_after_sampling[idx]# Culture Volume After Sampling (ml)
        f = self.separate_feed[idx]
        separate_f_added = self.separate_feed_sum[idx] # Separate Feed Sum Added (E.g. glutamine, glucose, etc.)

        # Initialize
        c = np.zeros(self.samples)
        c.fill(np.nan)

        if self.use_feed_conc:
                sf = self.feed_conc
        else:
            sf = 0

        # calculate concentration After Feeding
        for i in range(1, len(idx)):
                c[idx[i]] = ((s[i] * v[i] + sf * f[i]) / (v[i] + f_media[i] + separate_f_added[i]))
    
        c = pd.DataFrame(data=c,columns=['value'])
        c['unit'] = CONSTANTS.CONCE_UNIT
        return c

    def cumulative_calc_by_feed(self) -> pd.DataFrame:
        ''' Calculate cumulative consumption using the feed concentration.
        '''
        idx = self.measurement_index
        s = self.conc_before_feed['value'].values[idx]     # Substrate Concentration (mM)
        sf = self.feed_conc
        v1 = self.volume_before_sampling[idx]   # Culture Volume Before Sampling (ml)
        v2 = self.volume_after_sampling[idx]    # Culture Volume After Sampling (ml)
        f = self.separate_feed[idx]

        # Initialize
        c = np.zeros(self.samples)
        c.fill(np.nan)
        c[idx[0]] = 0

        # Consumed Substrate = sf*f + s[i-1]*v[i-1] - s[i]*v[i]
        for i in range(1, len(idx)):
            c_i = (sf * f[i-1] - s[i] * v1[i] + s[i-1] * v2[i-1]) / 1000
            c[idx[i]] = c[idx[i-1]] + c_i
        if SPECIES_STATE[self.name] == 'Produced':
            c *= -1
        c = pd.DataFrame(data=c, columns=['value'])
        c['unit'] = CONSTANTS.CUMULATIVE_UNIT
        c['state'] = SPECIES_STATE[self.name]
        c['method'] = 'twoPoint'
        return c

    def cumulative_calc_by_conc_after_feed(self) -> pd.DataFrame:
        ''' Calculate cumulative consumption using the concentration after feeding
        '''
        idx = self.measurement_index
        s1 = self.conc_before_feed['value'].values[idx]    # Substrate Concentration Before Feeding (mM)
        s2 = self.conc_after_feed['value'].values[idx]     # Substrate Concentration After Feeding (mM)
        v = self.volume_before_sampling[idx]    # Culture Volume After Feeding (ml)

        # Initialize
        c = np.zeros(self.samples)
        c.fill(np.nan)
        c[idx[0]] = 0

        for i in range(1, len(idx)):
            c_i = (s2[i-1] * v[i] - s1[i] * v[i]) / 1000
            c[idx[i]] = c[idx[i-1]] + c_i
        if SPECIES_STATE[self.name] == 'Produced':
            c *= -1
        c = pd.DataFrame(data=c, columns=['value'])
        c['unit'] = CONSTANTS.CUMULATIVE_UNIT
        c['state'] = SPECIES_STATE[self.name]
        c['method'] = 'twoPoint'
        return c

    def cumulative_calc_without_feed(self) -> pd.DataFrame:
        ''' Calculate cumulative consumption without the concentration after feeding.
        '''
        idx = self.measurement_index
        s = self.conc_before_feed['value'].values[idx]     # Substrate Concentration (mM)
        v1 = self.volume_before_sampling[idx]   # Culture Volume Before Sampling (ml)
        v2 = self.volume_after_sampling[idx]    # Culture Volume After Sampling (ml)

        # Initialize
        c = np.zeros(self.samples)
        c.fill(np.nan)
        c[idx[0]] = 0

        # Consumed Substrate = sf*f + s[i-1]*v[i-1] - s[i]*v[i]
        for i in range(1, len(idx)):
            c_i = (- s[i] * v1[i] + s[i-1] * v2[i-1]) / 1000
            c[idx[i]] = c[idx[i-1]] + c_i
        if SPECIES_STATE[self.name] == 'Produced':
            c *= -1
        c = pd.DataFrame(data=c, columns=['value'])
        c['unit'] = CONSTANTS.CUMULATIVE_UNIT
        c['state'] = SPECIES_STATE[self.name]
        c['method'] = 'twoPoint'
        return c
    
    # Calculate Specific Rate
    def sp_rate_calc(self) -> pd.DataFrame:
        ''' Calculate specific rate.
        '''
        idx = self.measurement_index
        s = self.cumulative_conc['value'].values[idx]           # Cumulative Concentration (mM)
        t = self.run_time_hour[idx]        # Run Time (hrs)
        v1 = self.volume_before_sampling[idx]   # Culture Volume Before Sampling (mL)
        v2 = self.volume_after_sampling[idx]    # Culture Volume Before sampling (mL)
        xv = self.viable_cell_conc['value'].values[idx]  # Viable Cell Concentration (10e6 cells/mL)
        
        # Initialize
        r = np.zeros(self.samples)
        r.fill(np.nan)
        
        # If there is the measurements of the cumulative concentration.
        if (self.measured_cumulative_flag):
            for i in range(1, len(idx)):                
                c_diff = (s[i] - s[i-1])            # concentration difference
                xv_avg = 0.5 * (xv[i] + xv[i-1])    # average vcc
                r[idx[i]] = c_diff / (t[i] - t[i-1]) / xv_avg
        else:
            for i in range(1, len(idx)):                
                c_diff = (s[i] - s[i-1]) * 1000 # concentration difference
                # With the concentration after feed
                if (self.use_conc_after_feed and not self.use_feed_conc):
                    xv_avg = 0.5 * (xv[i] * v1[i] + xv[i-1] * v1[i]) # Average
                # With the feed concentration OR without both
                else:
                    xv_avg = 0.5 * (xv[i] * v1[i] + xv[i-1] * v2[i-1]) # Average
                r[idx[i]] = c_diff / (t[i]-t[i-1]) / xv_avg
        r = pd.DataFrame(data=r, columns=['value'])
        r['unit'] = CONSTANTS.SP_RATE_UNIT
        r['method'] = 'twoPoint'
        r.index.name = f'q{self.name}'
        return r

    @property
    def use_feed_conc(self):
        return self._use_feed_conc
    
    @property
    def use_conc_after_feed(self):
        return self._use_conc_after_feed

        

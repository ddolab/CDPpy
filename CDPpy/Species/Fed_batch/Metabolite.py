import pandas as pd
import numpy as np

from CDPpy.helper import get_measurement_indices
from .Species import Species

from CDPpy.in_process.Fed_batch.MetaboliteMixin import MetaboliteMixin as Inprocess
#from ...in_process.MetaboliteMixin import MetaboliteMixin
#from ...post_process.polynomial.MetaboliteMixin import MetaboliteMixin as Polynomial
#from ...post_process.rolling_window_polynomial.Metabolite import MetaboliteMixin as Rolling
#from ...plotting.PlotMixin import PlotMixin

class Metabolite(Species, Inprocess,
                 # Polynomial, 
                 # Rolling, 
                 # PlotMixin
                 ):
    '''
    Metabolite class.

    Attributes
    ---------
        name : str
                name of species.
    '''             
    def __init__(self, name, samples, run_time_day, run_time_hour, 
                 volume_before_sampling, volume_after_sampling, feed_media_added,
                 viable_cell_conc, separate_feed, separate_feed_sum,
                 conc_before_feed, conc_after_feed, feed_conc, measured_cumulative_conc):
        '''
        Parameters
        ---------
            name : str
                name of species.
        '''
        # Constructor for MeasuredDate Class
        super().__init__(name, samples, run_time_day, run_time_hour, 
                         volume_before_sampling, volume_after_sampling, feed_media_added, 
                         viable_cell_conc)
        
        # Get indices of the measurements from the concentration
        conc = conc_before_feed['value']
        idx = get_measurement_indices(conc)
        
        # Class Members
        self._idx = idx
        self._separate_feed = separate_feed
        self._separate_feed_sum = separate_feed_sum
        self._conc_before_feed = conc_before_feed
        self._conc_after_feed = conc_after_feed
        self._feed_conc = feed_conc
        self._measured_cumulative_conc = measured_cumulative_conc
        value = measured_cumulative_conc['value']
        self._measured_cumulative_flag = True if value.notnull().any() else False # True if there is the measurement of cumulative concentration.
    
    @property
    def measurement_index(self):
        return self._idx
    @property
    def conc_before_feed(self):
        return self._conc_before_feed
    @property
    def conc_after_feed(self):
        return self._conc_after_feed
    @property
    def feed_conc(self):
        return self._feed_conc
    @property
    def measured_cumulative_conc(self):
        return self._measured_cumulative_conc
    @property
    def measured_cumulative_flag(self):
        return self._measured_cumulative_flag
    @property
    def separate_feed(self):
        return self._separate_feed
    @property
    def separate_feed_sum(self):
        return self._separate_feed_sum
    
    '''def get_info_df(self, t):
        n = len(t)
        id = pd.Series(data=[self._exp_id] * n, name='Experiment ID')
        cl = pd.Series(data=[self._cell_line_name] * n, name='Cell Line')
        return pd.concat([cl, id, t], axis=1)


    def get_inpro_df(self):
        return pd.concat([self.get_info_df(self._run_time_hour),
                          self._conc_before_feed,
                          self._feed_conc,
                          self._conc_after_feed,
                          self._cumulative,
                          ], axis=1)

    def get_conc_df(self):
        t = self.get_info_df(self._run_time_hour)
        conc = self._conc_before_feed
        conc_before = pd.concat([t, conc.rename('CONC.')], axis=1)
        
        conc = self._conc_after_feed
        conc_after = pd.concat([t, conc.rename('CONC.')], axis=1)
        conc = pd.concat([conc_before, conc_after]).reset_index(drop=True)
        conc['Species'] = self._name.upper()
        conc['Species_label'] = f'{self._name.capitalize()} (mM)'

        return conc.sort_values(by=['RUN TIME (HOURS)'], kind='stable').reset_index(drop=True)
        
    def get_cumulative_df(self):
        t = self._run_time_hour
        # Two-pt calc.
        cum = self.get_info_df(t)
        cum['Cumulative'] = self.get_cumulative()
        cum['Method'] = f'Two-Pt. Calc.'
        cum['Cell_Line_Label'] = cum['Cell Line'].apply(lambda x: x+', Two-Pt. Calc.')
        cum['Experiment_ID_Label'] = cum['Experiment ID'].apply(lambda x: x+', Two-Pt. Calc.')

        # Poly. Reg.
        x = np.linspace(t.iat[0], t.iat[-1], 100)
        x = pd.Series(data=x, name=t.name)
        cum_poly = self.get_info_df(x)
        # cum[f'CUM {self._name} (mmol)'] = pd.Series(data=self._polyfit(x))
        cum_poly[f'Cumulative'] = pd.Series(data=self._polyfit(x))
        cum_poly['Method'] = f'Poly. Reg.'
        cum_poly['Order'] = self._polyorder
        cum_poly['Cell_Line_Label'] = cum_poly['Cell Line'].apply(lambda x: x+', Poly. Reg.')
        cum_poly['Experiment_ID_Label'] = cum_poly['Experiment ID'].apply(lambda x: x+', Poly. Reg.')

        # concat
        cum = pd.concat([cum, cum_poly], axis=0).reset_index(drop=True)
        if  self._production:
            name = f'{self._name.capitalize()} Production (mmol)'
        else:
            name = f'{self._name.capitalize()} Consumption (mmol)'
        cum['Species'] = self._name.upper()
        cum['Species_label'] = name
        return cum.sort_values(by=['RUN TIME (HOURS)'], kind='stable').reset_index(drop=True)

    def get_sp_rate_df(self, twopt=False, polyreg=False, rollreg=False):
        q1 = pd.DataFrame()
        q2 = pd.DataFrame()
        q3 = pd.DataFrame()

        if (twopt):
            q1 = self.get_twopt_sp_rate_df()
        if (polyreg):
            q2 = self.get_polyreg_sp_rate_df()
        if (rollreg):
            q3 = self.get_rollreg_sp_rate_df()
        df = pd.concat([q1, q2, q3], axis=0).reset_index(drop=True)
        df['Species'] = self._name.upper()
        df['Species_label'] = f'q{self._name.capitalize()} (mmol/10^9 cell/hr)'
        return df

    def get_twopt_sp_rate_df(self):
        info_df = self.get_info_df(self._run_time_hour)
        # name = f'q{self._name} (mmol/109 cell/hr)'
        name = f'Sp. rate'
        q = self._sp_rate.rename(name)
        q = pd.concat([info_df, q], axis=1)
        q['Method'] = 'Two-Pt. Calc.'
        return q
    
    def get_polyreg_sp_rate_df(self):
        info_df = self.get_info_df(self._run_time_hour)
        # name = f'q{self._name} (mmol/109 cell/hr)'
        name = f'Sp. rate'
        q = self._polyreg_sp_rate.rename(name)
        q = pd.concat([info_df, q], axis=1)
        q['Method'] = f'Poly. Reg.'
        q['Order'] = self._polyorder
        return q

    def get_rollreg_sp_rate_df(self):
        info_df = self.get_info_df(self._run_time_mid.rename('RUN TIME (HOURS)'))
        # name = f'q{self._name} (mmol/109 cell/hr)'
        name = f'Sp. rate'
        q = self._rollpolyreg_sp_rate.rename(name)
        q = pd.concat([info_df, q], axis=1)
        q['Method'] = f'Roll. Reg.'
        q['Order'] = self._rollpolyreg_order
        q['Window'] = self._rollpolyreg_window
        return q'''
        

###########################################################################
# Metabolite Class for Nitrogen, and AA Carbon
###########################################################################
class Metabolite2(Species, 
                  #Polynomial, 
                  # Rolling
                  ):
    '''
    Store information for Nitrogen and AA carbon.

    Attributes
    ---------
        name : str
            name of species.
        measured_data : python object
                MeasuredData object.
        cumulative : pandas.DataFrame
            calculated cumulative consumption/production.
    '''
    def __init__(self, name, measured_data, cumulative):
        '''
        Parameters
        ----------
            name : str
                name of species.
            measured_data : python object
                MeasuredData object.
            cumulative : pandas.DataFrame
                calculated cumulative consumption/production.
        '''
        # Constructor for MeasuredDate Class
        super().__init__(name=name, measured_data=measured_data)

        self._cumulative = cumulative
        self._sp_rate = pd.DataFrame()
        self._idx = self._cumulative[self._cumulative.notnull()].index
        self._run_time_mid = self.__mid_calc_runtime()


    #*** Praivete Methods ***#
    def __mid_calc_runtime(self):
        idx = self._idx                 # Measurement index
        t = self._run_time_hour[idx]         # run time hour

        t_mid = pd.Series(data=[np.nan] * (len(idx)-1),
                            name='RUN TIME MID (HOURS)', dtype='float')

        for i in range(len(idx)-1):
            t_mid.iat[i] = (t.iat[i]+t.iat[i+1])/2

        return t_mid
        
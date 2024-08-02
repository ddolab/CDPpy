import pandas as pd

class GetterMixin:
    def get_conc_before_feed(self):
        '''get measured data for concentration before feeding.'''
        return self._conc_before_feed_data
    
    def get_conc_after_feed(self):
        '''get measured data for concentration before feeding.'''
        return self._conc_after_feed_data
    
    def get_measured_cumulative_conc(self):
        '''get measured data for calculated cumulative concentration.'''
        return self._measured_cumulative_conc_data

    def get_feed_conc(self):
        '''get feed concentration data.'''
        return self._feed_data

    def get_separate_feed_conc(self):
        '''get separate feed concentration data.'''
        return self._separate_feed_data
    
    def get_polynomial_degree(self):
        '''get polynomial degreee data.'''
        return self._polynomial_degree_data
    
    def get_processed_data(self):
        ''''''
        exp_handles = self._exp_handles

        df_list = []
        for i, exp_handler in enumerate(exp_handles.values()):
            if i==0:
                df_list.append(exp_handler.get_processed_data())
            else:
                df = exp_handler.get_processed_data().copy()
                df_list.append(df.drop(df.index[0]))

        return pd.concat(df_list, axis=0, ignore_index=True)
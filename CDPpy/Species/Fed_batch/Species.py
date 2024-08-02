# Python Libraries
import pandas as pd
import numpy as np

# My Libraries
from CDPpy.Constants import SPECIES_ABBR

class Species():
    '''
    Species class.

    Attribute
    ---------
        name : str
            name of species.
        measured_data : python object
            MeasuredData object.
    '''
    # Constructor
    def __init__(self, name, samples, run_time_day, run_time_hour, 
                 volume_before_sampling, volume_after_sampling, 
                 feed_media_added, viable_cell_conc) -> None:
        '''
        Parameters
        ---------
            name : str
                name of species.
        '''
        # Class Members
        name = name.capitalize() if name != 'IgG' else 'IgG'
        abbr = SPECIES_ABBR[name] if SPECIES_ABBR.get(name) else name.upper()
        run_time = pd.DataFrame(data={run_time_day.index.name: run_time_day['value'].values,
                                      run_time_hour.index.name: run_time_hour['value'].values})

        # Store data
        self._name = name
        self._abbr = abbr
        self._samples = samples
        self._run_time = run_time
        self._run_time_day = run_time_day
        self._run_time_hour = run_time_hour
        self._volume_before_sampling = volume_before_sampling
        self._volume_after_sampling = volume_after_sampling
        self._feed_media_added = feed_media_added
        self._viable_cell_conc = viable_cell_conc

    @property
    def name(self):
        return self._name
    @property
    def abbr(self):
        return self._abbr
    @property
    def run_time_day(self):
        return self._run_time_day
    @property
    def run_time_hour(self):
        return self._run_time_hour
    @property
    def samples(self):
        return self._samples
    @property
    def volume_before_sampling(self):
        return self._volume_before_sampling
    @property
    def volume_after_sampling(self):
        return self._volume_after_sampling
    @property
    def feed_media_added(self):
        return self._feed_media_added
    @property
    def viable_cell_conc(self):
        return self._viable_cell_conc
    @property
    def run_time(self):
        return self._run_time
        
    
    def get_profile_data(self, data_list, profile_list, kind_list, method_list):
        '''Return cumulative concentration data.
        '''
        df_lst = []
        for d, p, k, m in zip(data_list, profile_list, kind_list, method_list):
            df = self._run_time_hour.to_frame(name='runTime')
            df['value'] = d
            df['profile'] = p
            df['kind'] = k
            df['method'] = m
            df_lst.append(df)
        data = pd.concat(df_lst, axis=0)
        data = data.sort_values(by=['runTime'], kind='stable').reset_index(drop=True)
        return data
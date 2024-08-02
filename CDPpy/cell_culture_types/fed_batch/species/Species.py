from CDPpy.constants import SPECIES_ABBR, RUN_TIME_DAY_COLUMN, RUN_TIME_HOUR_COLUMN
from CDPpy.helper import get_measurement_indices

class Species():
    '''
    Species class.

    Attribute
    ---------
    '''
    # Constructor
    def __init__(self, name, param_data) -> None:
        '''
        Parameters
        ---------
        '''
        name = name.capitalize() if name != 'IgG' else 'IgG'
        abbr = SPECIES_ABBR[name] if SPECIES_ABBR.get(name) else name.upper()

        # Get indices of the measurement from the viable cell concentration
        xv = param_data['viable_cell']['value']
        idx = get_measurement_indices(xv)

        # Store data
        self._name = name
        self._abbr = abbr
        self._run_time = param_data['time']
        self._run_time_day = self._run_time[RUN_TIME_DAY_COLUMN].values
        self._run_time_hour = self._run_time[RUN_TIME_HOUR_COLUMN].values
        self._samples = self._run_time_hour.size
        self._volume_before_sampling = param_data['v_before_sample']
        self._volume_after_sampling = param_data['v_after_sample']
        self._feed_media_added = param_data['feed_media']
        self._viable_cell_conc = param_data['viable_cell']
        self._vcc_idx = idx

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
    def run_time(self):
        return self._run_time
    
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
    def vcc_index(self):
        return self._vcc_idx

    
    
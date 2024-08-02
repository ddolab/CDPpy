import pandas as pd

from .Variables import metabolite_dict

class Species:
    '''
    '''
    def __init__(self, name, run_time, culture_volume, flow_rate, viable_cell_conc) -> None:
        '''
        '''
        # Work with name
        name = name.capitalize()
        abbr = metabolite_dict[name] if metabolite_dict.get(name) else name

        # Calculate the dillution rate (hr^-1): flow rate (ml/hr) / culture volume (ml)
        dillution_rate = flow_rate['value'].values / culture_volume['value'].values
        df = pd.DataFrame(data=dillution_rate, columns=['value'])
        df['unit'] = '(hr^-1)'
        df.index.name = 'dillution_rate'

        # Store variables
        self._name = name
        self._abbr = abbr
        self._run_time = run_time
        self._culture_volume = culture_volume
        self._flow_rate = flow_rate
        self._dillution_rate = df
        self._viable_cell_conc = viable_cell_conc

    @property
    def get_name(self):
        return self._name
    
    @property
    def get_abbr(self):
        return self._abbr
    
    @property
    def get_run_time(self):
        return self._run_time
    
    @property
    def get_culture_volume(self):
        return self._culture_volume
    
    @property
    def get_flow_rate(self):
        return self._flow_rate
    
    @property
    def get_dillution_rate(self):
        return self._dillution_rate
    
    @property
    def get_viable_cell_conc(self):
        return self._viable_cell_conc


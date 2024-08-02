from .Species import Species
from ...in_process.Perfusion.CellMixin import CellMixin as InProcess
import pandas as pd

class Cell(Species, InProcess):
    '''
    '''
    def __init__(self, run_time, culture_volume, flow_rate, viable_cell_conc, dead_cell_conc, total_cell_conc) -> None:
        '''
        '''
        super().__init__('cell', run_time, culture_volume, flow_rate, viable_cell_conc)

        # Calculate viability
        viab = viable_cell_conc['value'].values / total_cell_conc['value'].values * 100
        df = pd.DataFrame(data=viab, columns=['value'])
        df['unit'] = '(%)'
        df.index.name = 'viability'

        # Store variables
        self._dead_cell_conc = dead_cell_conc
        self._total_cell_conc = total_cell_conc
        self._viability = df
    
    @property
    def get_dead_cell_conc(self):
        return self._dead_cell_conc
    
    @property
    def get_total_cell_conc(self):
        return self._total_cell_conc
    
    @property
    def viability(self):
        ''''''
        t = self._run_time['value'].values.copy()
        v = self._viability.copy()
        v['time'] = t
        v = v[['time', 'value', 'unit']]
        return v
    
    @property
    def concentration(self):
        t = self._run_time['value'].values.copy()
        xv = self._viable_cell_conc.copy()
        xv['time'] = t
        xv['state'] = 'viable'
        xd = self._dead_cell_conc.copy()
        xd['time'] = t
        xd['state'] = 'death'
        xt = self._total_cell_conc.copy()
        xt['time'] = t
        xt['state'] = 'total'
        data = pd.concat([xv, xd, xt], axis=0).reset_index(drop=True)
        data = data[['time', 'value', 'unit', 'state']]
        return data
    
    
    

        
from .Species import Species
import pandas as pd

from CDPpy.cell_culture_types.perfusion.in_process import CellMixin as Inprocess
from CDPpy.cell_culture_types.perfusion.post_process.polynomial import CellMixin as Polynomial

class Cell(Species, Inprocess, Polynomial):
    '''
    '''
    def __init__(self, run_time_df, bleeding_ratio, dillution_rate, viable_cell_conc, dead_cell_conc, total_cell_conc) -> None:
        '''
        '''
        super().__init__('cell', run_time_df, dillution_rate, viable_cell_conc)

        # Calculate viability
        viab = viable_cell_conc['value'].values / total_cell_conc['value'].values * 100
        df = pd.DataFrame(data=viab, columns=['value'])
        df['unit'] = '(%)'
        df.index.name = 'viability'

        # Store variables
        self._bleeding_ratio = bleeding_ratio
        self._dead_cell_conc = dead_cell_conc
        self._total_cell_conc = total_cell_conc
        self._viability = df
    
    @property
    def dead_cell_conc(self):
        return self._dead_cell_conc
    
    @property
    def total_cell_conc(self):
        return self._total_cell_conc
    
    @property
    def viability(self):
        return self._viability
    

        
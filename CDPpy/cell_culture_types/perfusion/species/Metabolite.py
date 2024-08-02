from CDPpy.cell_culture_types.perfusion.in_process import MetaboliteMixin as Inprocess
from CDPpy.cell_culture_types.perfusion.post_process.polynomial import MetaboliteMixin as Plynomial
from CDPpy.cell_culture_types.perfusion.post_process.rolling_window_polynomial import MetaboliteMixin as RollingPolynomial
from .Species import Species

class Metabolite(Species, Inprocess, Plynomial, RollingPolynomial):
    '''
    '''
    def __init__(self, name, run_time_df, dillution_rate, conc, feed_conc, viable_cell_conc) -> None:
        '''
        '''
        super().__init__(name, run_time_df, dillution_rate, viable_cell_conc)

        # Store variables
        self._conc = conc
        self._feed_conc = feed_conc

    @property
    def conc(self):
        ''''''
        return self._conc
    
    @property
    def feed_conc(self):
        ''''''
        return self._feed_conc
    

    
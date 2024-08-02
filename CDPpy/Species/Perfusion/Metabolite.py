from .Species import Species
from ...in_process.Perfusion.MetaboliteMixin import MetaboliteMixin as InProcess
from CDPpy.post_process.Perfusion.polynomial.MetaboliteMixin import MetaboliteMixin as Polynomial
class Metabolite(Species, InProcess, Polynomial):
    '''
    '''
    def __init__(self, name, run_time, culture_volume, flow_rate, conc, feed_conc, viable_cell_conc) -> None:
        '''
        '''
        super().__init__(name, run_time, culture_volume, flow_rate, viable_cell_conc)

        # Store variables
        self._conc = conc
        self._feed_conc = feed_conc
    
    @property
    def concentration(self):
        t = self._run_time['value'].values.copy()
        c = self._conc.copy()
        c['time'] = t
        c = c[['time', 'value', 'unit']]
        return c
    
    @property
    def feed_concentration(self):
        t = self._run_time['value'].values.copy()
        f = self._feed_conc.copy()
        f['time'] = t
        f = f[['time', 'value', 'unit']]
        return f
    
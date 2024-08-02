import pandas as pd

from CDPpy.cell_line_data import CellLineDataHandler

from CDPpy.constants import CELL_LINE_COLUMN

from .GetterMixin import GetterMixin

class PerfusionCellLineDataHandler(CellLineDataHandler, GetterMixin):
    '''
    '''
    def __init__(self, cell_line_name, data, parameter) -> None:
        self._parameter = parameter

        super().__init__(cell_line_name, data=data, cell_culture_type='perfusion')

        conc_data = data['conc'].copy()
        feed_conc_data = data['feed_conc'].copy()
        feed_mask = feed_conc_data[CELL_LINE_COLUMN]==cell_line_name

        polynomial_degree_data = data['polynomial_degree_data'].copy()
        polynomial_degree_mask = polynomial_degree_data[CELL_LINE_COLUMN]==cell_line_name

        self._polynomial_degree_data = polynomial_degree_data[polynomial_degree_mask]
        self._conc_before_feed_data = conc_data[self._mask].copy()
        self._feed_data  = feed_conc_data[feed_mask].copy()

        # Store all data in dict
        data = {'measured_data': self._measured_data,
                'conc': self._conc_before_feed_data,
                'feed_conc': self._feed_data,
                'polynomial_degree_data': self._polynomial_degree_data}
        self._data_set = data

        # calss members to store processed data
        self._cell_data = {'conc': None,
                           'cumulative': None,
                           'death_rate': None,
                           'growth_rate': None}
        
        self._metabolite_data = {'conc': None,
                                 'cumulative': None,
                                 'sp_rate': None}
        
        # class member to store experiment handlers
        self._exp_handles = {}

    def get_all_data(self):
        '''get all data set'''
        return self._data_set
    
    def get_cell_data(self):
        '''get processed data for the cell.'''
        return self._cell_data
    
    def get_metabolite_data(self):
        '''get processed data for the metabolite.'''
        return self._metabolite_data
    
    def get_experiment_handle(self, experiment_id=None):
        '''get the experiment handl(s).'''
        exp_handles = self._exp_handles
        if experiment_id:
            return exp_handles[experiment_id]
        else:
            return exp_handles

    def in_process(self):
        '''in-processing the data for the same cell line name.'''
        cell_line_name = self.cell_line_name
        experiment_ids = self.get_experiment_names()
        data = self.get_all_data()

        exp_handles = self._exp_handles
        for id in experiment_ids:
            # call experiment handler
            exp_handler = self._experiment_handler(cell_line_name=cell_line_name,
                                                   cell_line_id=id,
                                                   data=data)
            # in-processing
            exp_handler.in_process()

            # store the handle with a key of id
            exp_handles[id] = exp_handler
        
        # store handlers    
        self._exp_handles = exp_handles
        # store data 
        self.store_data()

    def polynomial(self):
        '''post-processing for polynomial regression.
        '''
        exp_handles = self._exp_handles

        for exp_handler in exp_handles.values():
            # polynomial regression
            exp_handler.polynomial()

        self.store_data()

    def store_data(self):
        '''store data for the cell and metabolite from experiment handlers.'''
        exp_handles = self._exp_handles
        cell_conc, cell_cumulative, cell_death_rate, cell_growth_rate = [], [], [], []
        conc, cumulative, sp_rate = [], [], []
        for exp_handler in exp_handles.values():
            # cell data
            cell_conc.append(exp_handler.cell_conc)
            cell_cumulative.append(exp_handler.cumulative_cell_production)
            cell_death_rate.append(exp_handler.death_rate)
            cell_growth_rate.append(exp_handler.growth_rate)

            # metabolite data
            conc.append(exp_handler.conc)
            cumulative.append(exp_handler.cumulative_conc)
            sp_rate.append(exp_handler.sp_rate)

        # concat
        cell_conc =  pd.concat(cell_conc, axis=0)
        cell_cumulative = pd.concat(cell_cumulative, axis=0)
        cell_death_rate = pd.concat(cell_death_rate, axis=0)
        cell_growth_rate = pd.concat(cell_growth_rate, axis=0)
        conc = pd.concat(conc, axis=0)
        cumulative = pd.concat(cumulative, axis=0)
        sp_rate = pd.concat(sp_rate, axis=0)
            
        cell_conc['Cell Line'] = self.cell_line_name
        cell_cumulative['Cell Line'] = self.cell_line_name
        cell_death_rate['Cell Line'] = self.cell_line_name
        cell_growth_rate['Cell Line'] = self.cell_line_name
        conc['Cell Line'] = self.cell_line_name
        cumulative['Cell Line'] = self.cell_line_name
        sp_rate['Cell Line'] = self.cell_line_name

        # store data
        self._cell_data['conc'] =  cell_conc
        self._cell_data['cumulative'] = cell_cumulative
        self._cell_data['death_rate'] = cell_death_rate
        self._cell_data['growth_rate'] = cell_growth_rate
        self._metabolite_data['conc'] = conc
        self._metabolite_data['cumulative'] = cumulative
        self._metabolite_data['sp_rate'] = sp_rate
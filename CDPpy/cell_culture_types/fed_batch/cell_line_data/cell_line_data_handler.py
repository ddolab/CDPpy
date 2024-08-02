import pandas as pd

from CDPpy.cell_line_data import CellLineDataHandler
from CDPpy.cell_culture_types.fed_batch.experiment_data import FedBatchExperimentHandler
from CDPpy.constants.fed_batch.column_name import CELL_LINE_COLUMN
from CDPpy.constants.fed_batch.dict_key import SPC_CONC_BEFORE_FEED_KEY, SPC_CONC_AFTER_FEED_KEY, SPC_FEED_CONC_KEY, SPC_MEASURED_CUM_CONC_KEY
from CDPpy.constants.fed_batch.dict_key import EXP_DATA_KEY, FEED_VOLUME_KEY, CONC_BEFORE_FEED_KEY, CONC_AFTER_FEED_KEY, MEASURED_CUM_CONC_KEY, FEED_CONC_KEY, POLY_DEG_KEY

from .GetterMixin import GetterMixin

class FedBatchCellLineDataHandler(CellLineDataHandler, GetterMixin):
    '''
    '''
    def __init__(self, cell_line_name, data) -> None:
        super().__init__(cell_line_name, data=data, cell_culture_type='fed-batch')

        conc_before_feed_data = data[CONC_BEFORE_FEED_KEY].copy()
        conc_after_feed_data = data[CONC_AFTER_FEED_KEY].copy()
        measured_cumulative_conc_data = data[MEASURED_CUM_CONC_KEY].copy()
        feed_conc_data = data[FEED_CONC_KEY].copy()
        feed_volume_data = data[FEED_VOLUME_KEY].copy()
        feed_mask = feed_conc_data[CELL_LINE_COLUMN]==cell_line_name

        polynomial_degree_data = data[POLY_DEG_KEY].copy()
        polynomial_degree_mask = polynomial_degree_data[CELL_LINE_COLUMN]==cell_line_name

        self._polynomial_degree_data = polynomial_degree_data[polynomial_degree_mask]
        self._conc_before_feed_data = conc_before_feed_data[self._mask].copy()
        self._conc_after_feed_data  = conc_after_feed_data[self._mask].copy()
        self._measured_cumulative_conc_data = measured_cumulative_conc_data[self._mask].copy()
        self._feed_data  = feed_conc_data[feed_mask].copy()
        self._feed_volume_data  = feed_volume_data[self._mask].copy()

        # Store
        # self._use_feed_conc = use_feed_conc
        # self._use_conc_after_feed = use_conc_after_feed
        data = {SPC_CONC_BEFORE_FEED_KEY: list(self._conc_before_feed_data.columns),
                SPC_CONC_AFTER_FEED_KEY: list(self._conc_after_feed_data.columns),
                SPC_FEED_CONC_KEY: list(self._feed_data.columns[3:]),
                SPC_MEASURED_CUM_CONC_KEY: list(self._measured_cumulative_conc_data.columns),
                EXP_DATA_KEY: self._measured_data,
                CONC_BEFORE_FEED_KEY: self._conc_before_feed_data,
                CONC_AFTER_FEED_KEY: self._conc_after_feed_data,
                MEASURED_CUM_CONC_KEY: self._measured_cumulative_conc_data,
                FEED_CONC_KEY: self._feed_data,
                FEED_VOLUME_KEY: self._feed_volume_data,
                POLY_DEG_KEY: self._polynomial_degree_data}
        self._data_set = data

        # calss members to store processed data
        self._cell_data = {'conc': None,
                           'cumulative': None,
                           'integral': None,
                           'growth_rate': None}
        
        self._metabolite_data = {'conc': None,
                                 'cumulative': None,
                                 'sp_rate': None}

    def get_pre_process_data(self):
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

    def in_process(self, use_feed_conc, use_conc_after_feed):
        '''in-processing the data for the same cell line name.'''
        self._check_species_name(use_feed_conc=use_feed_conc, use_conc_after_feed=use_conc_after_feed)
        cell_line_name = self.cell_line_name
        experiment_ids = self.get_experiment_names()
        data = self.get_pre_process_data()

        exp_handles = {}
        for id in experiment_ids:
            # call experiment handler
            exp_handler = FedBatchExperimentHandler(cell_line_name=cell_line_name,
                                                    cell_line_id=id,
                                                    data=data,
                                                    use_feed_conc=use_feed_conc,
                                                    use_conc_after_feed=use_conc_after_feed)
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

    def rolling_window_polynomial(self, deg, window):
        '''post-processing for rolling window polynomial regression.
        '''
        exp_handles = self._exp_handles

        for exp_handler in exp_handles.values():
            # rolling window polynomial regression
            exp_handler.rolling_window_polynomial(degree=deg, window=window)

        self.store_data()

    def store_data(self):
        '''store data for the cell and metabolite from experiment handlers.'''
        exp_handles = self._exp_handles
        cell_conc, cell_cumulative, cell_integral, cell_growth_rate = [], [], [], []
        conc, cumulative, sp_rate = [], [], []
        for exp_handler in exp_handles.values():
            # cell data
            cell_conc.append(exp_handler.cell_conc)
            cell_cumulative.append(exp_handler.cumulative_cell_production)
            cell_integral.append(exp_handler.integral_viable_cell_conc)
            cell_growth_rate.append(exp_handler.growth_rate)

            # metabolite data
            conc.append(exp_handler.conc)
            cumulative.append(exp_handler.cumulative_conc)
            sp_rate.append(exp_handler.sp_rate)

        # concat
        cell_conc =  pd.concat(cell_conc, axis=0)
        cell_cumulative = pd.concat(cell_cumulative, axis=0)
        cell_integral = pd.concat(cell_integral, axis=0)
        cell_growth_rate = pd.concat(cell_growth_rate, axis=0)
        conc = pd.concat(conc, axis=0)
        cumulative = pd.concat(cumulative, axis=0)
        sp_rate = pd.concat(sp_rate, axis=0)

        cell_conc['Cell Line'] = self.cell_line_name
        cell_cumulative['Cell Line'] = self.cell_line_name
        cell_integral['Cell Line'] = self.cell_line_name
        cell_growth_rate['Cell Line'] = self.cell_line_name
        conc['Cell Line'] = self.cell_line_name
        cumulative['Cell Line'] = self.cell_line_name
        sp_rate['Cell Line'] = self.cell_line_name

        # store data
        self._cell_data['conc'] =  cell_conc
        self._cell_data['cumulative'] = cell_cumulative
        self._cell_data['integral'] = cell_integral
        self._cell_data['growth_rate'] = cell_growth_rate
        self._metabolite_data['conc'] = conc
        self._metabolite_data['cumulative'] = cumulative
        self._metabolite_data['sp_rate'] = sp_rate

    def _check_species_name(self, use_feed_conc, use_conc_after_feed):
        '''Check species name in the measured data file'''
        # Check species name for each data
        if use_feed_conc:
            for spc in self._spc_feed:
                assert spc in self._spc_conc_before, f"{spc} is not included in 'Feed Concentration beore Feeding' data."
            for spc in self._spc_conc_before:
                assert spc in self._spc_feed, f"{spc} is not included in 'Feed Concentration' data."
        
        elif use_conc_after_feed:
            for spc in self._spc_conc_after:
                assert spc in self._spc_conc_before, f"{spc} is not included in 'Feed Concentration beore Feeding' data."
            for spc in self._spc_conc_before:
                assert spc in self._spc_conc_after, f"{spc} is not included in 'Feed Concentration after Feeding' data."




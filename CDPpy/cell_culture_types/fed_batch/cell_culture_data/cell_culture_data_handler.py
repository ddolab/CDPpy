import pandas as pd
import numpy as np

from CDPpy.plotting.InteractivePlot import InteractivePlotMixin
from CDPpy.cell_culture_data_base.cell_culture_data_handler import CellCultureDataHandler
from CDPpy.cell_culture_types.fed_batch.cell_line_data import FedBatchCellLineDataHandler
from CDPpy.cell_culture_types.fed_batch.export_data.export_data import ExportMixin
from CDPpy.cell_culture_types.fed_batch.import_data.import_data import ImportMixin

from CDPpy.constants.fed_batch.sheet_name import DATA_SHEET, FEED_SHEET, POLYNOMIAL_SHEET
from CDPpy.constants.fed_batch.column_name import EXPERIMENT_DATA_COLUMN, FEED_VOLUME_COLUMN, CONC_BEFOROE_FEED_COLUMN, CONC_AFTER_FEED_COLUMN, MEASURED_CUMULATIVE_COLUMN
from CDPpy.constants.fed_batch.column_name import CELL_LINE_COLUMN, ID_COLUMN
from CDPpy.constants.fed_batch.dict_key import SPC_CONC_BEFORE_FEED_KEY, SPC_CONC_AFTER_FEED_KEY, SPC_FEED_CONC_KEY, SPC_MEASURED_CUM_CONC_KEY
from CDPpy.constants.fed_batch.dict_key import EXP_DATA_KEY, FEED_VOLUME_KEY, CONC_BEFORE_FEED_KEY, CONC_AFTER_FEED_KEY, MEASURED_CUM_CONC_KEY, FEED_CONC_KEY, POLY_DEG_KEY

from CDPpy.helper import split_df, compile_df

from .GeterMixin import GetterMixin

class FedBatchCellCultureDataHandler(CellCultureDataHandler, GetterMixin, InteractivePlotMixin, ExportMixin, ImportMixin):
    ''''''
    def __init__(self) -> None:
        super().__init__(cell_culture_type='fed-batch')

        # Fed-batch cell line data handler
        self._cell_line_handler = FedBatchCellLineDataHandler

        # calss members to store processed data
        self._processed_data = pd.DataFrame()

        self._cell_data = {'conc': None,
                           'cumulative': None,
                           'integral': None,
                           'growth_rate': None}
        
        self._metabolite_data = {'conc': None,
                                 'cumulative': None,
                                 'sp_rate': None}


    def load_data(self, file):
        '''load an excel file.'''
        sheet_name=[DATA_SHEET, FEED_SHEET, POLYNOMIAL_SHEET]
        sheets_dict = super().load_data(file=file)

        measured_data = sheets_dict[sheet_name[0]]
        feed_conc = compile_df(sheets_dict[sheet_name[1]])
        polynomial_degree = compile_df(sheets_dict[sheet_name[2]])
        
        # change dtype of "Cell Line" and "ID" columns
        cols = [CELL_LINE_COLUMN, ID_COLUMN]
        feed_conc[cols] = feed_conc[cols].astype('string')
        polynomial_degree[cols] = polynomial_degree[cols].astype('string')
        
        # store data
        self._exp_data = measured_data
        self._feed_conc_data = feed_conc
        self._polynomial_degree_data = polynomial_degree
        
        # pre-process
        self.preprocess_data()

    def preprocess_data(self):
        '''format loaded data.'''
        taerget_columns=[EXPERIMENT_DATA_COLUMN, 
                         FEED_VOLUME_COLUMN, 
                         CONC_BEFOROE_FEED_COLUMN, 
                         CONC_AFTER_FEED_COLUMN, 
                         MEASURED_CUMULATIVE_COLUMN]
        data_list = split_df(self._exp_data, taerget_columns)
        taerget_column_indices = dict(zip(taerget_columns, np.arange(len(taerget_columns))))
        
        data = data_list[taerget_column_indices[EXPERIMENT_DATA_COLUMN]]
        data[[CELL_LINE_COLUMN, ID_COLUMN]] = data[[CELL_LINE_COLUMN, ID_COLUMN]].astype('string')
        
        self._exp_data = data
        self._feed_volume = data_list[taerget_column_indices[FEED_VOLUME_COLUMN]]
        self._conc_before_feed_data = data_list[taerget_column_indices[CONC_BEFOROE_FEED_COLUMN]]
        self._conc_after_feed_data = data_list[taerget_column_indices[CONC_AFTER_FEED_COLUMN]]
        self._measured_cumulative_data = data_list[taerget_column_indices[MEASURED_CUMULATIVE_COLUMN]].astype('float64')
        self._cell_line_names = list(self._exp_data[CELL_LINE_COLUMN].unique())

        # Store all data in dict
        data = {SPC_CONC_BEFORE_FEED_KEY: list(self._conc_before_feed_data.columns),
                SPC_CONC_AFTER_FEED_KEY: list(self._conc_after_feed_data.columns),
                SPC_FEED_CONC_KEY: list(self._feed_conc_data.columns[3:]),
                SPC_MEASURED_CUM_CONC_KEY: list(self._measured_cumulative_data.columns),
                EXP_DATA_KEY: self._exp_data,
                FEED_VOLUME_KEY: self._feed_volume,
                CONC_BEFORE_FEED_KEY: self._conc_before_feed_data,
                CONC_AFTER_FEED_KEY: self._conc_after_feed_data,
                MEASURED_CUM_CONC_KEY: self._measured_cumulative_data,
                FEED_CONC_KEY: self._feed_conc_data,
                POLY_DEG_KEY: self._polynomial_degree_data}
        self._data_set = data

    def perform_data_process(self, parameters):
        '''in-prcessing data for all cell lines.'''
        # Cell culture parameters
        param_dict = {}
        if isinstance(parameters, list):
            for param in parameters:
                param_dict[param.cell_line_name] = param
        else:
            param_dict[parameters.cell_line_name] = parameters
        self._param = param_dict
        
        cell_line_names = self.get_cell_line_names()
        data_set = self.get_pre_process_data()

        cell_lines = [name for name in cell_line_names if name in self._param.keys()]

        cell_line_handles = {}
        df_list = []
        for i, cell_line in enumerate(cell_lines):
            param = self._param[cell_line]
            # call cell line data handler
            cell_line_data_handler = self._cell_line_handler(
                cell_line_name=cell_line,
                data=data_set)
            
            # in-processing
            cell_line_data_handler.in_process(use_feed_conc=param.use_feed_conc,
                                              use_conc_after_feed=param.use_conc_after_feed)

            # post-porcessing-polynomial regression
            if param.polynomial:
                cell_line_data_handler.polynomial()
            # post-processing-rolling window polynomial regression
            if param.rolling_window_polynomial:
                deg = param.rolling_polynomial_degree
                window = param.rolling_polynomial_window
                cell_line_data_handler.rolling_window_polynomial(deg=deg, window=window)

            # store handlers
            cell_line_handles[cell_line] = cell_line_data_handler

            # get all processed data for each cell line
            if i==0:
                df_list.append(cell_line_data_handler.get_processed_data())
            else:
                # df_list.append(cell_line_data_handler.get_processed_data())
                df = cell_line_data_handler.get_processed_data().copy()
                df_list.append(df.drop(df.index[0]).reset_index(drop=True))

        self._cell_line_handles = cell_line_handles

        # store processed cell line name and id
        processed_info = {}
        for cell_line, cl_handler in cell_line_handles.items():
            processed_info[cell_line] = list(cl_handler.get_experiment_handle().keys())
        self._processed_cell_lines = processed_info

        # store data
        self.store_data()

        if self._processed_data.size==0:
            self._processed_data = pd.concat(df_list, axis=0, ignore_index=True)
        else:
            df = self._processed_data.iloc[2:]
            df_list.append(df)
            self._processed_data = pd.concat(df_list, axis=0, ignore_index=True)

    def store_data(self):
        '''store data for the cell and metabolite from cell line data handlers.'''
        cell_line_handles = self._cell_line_handles

        cell_conc, cell_cumulative, cell_integral, cell_growth_rate = [], [], [], []
        conc, cumulative, sp_rate = [], [], []
        for cell_line_handler in cell_line_handles.values():
            # cell data
            cell_data = cell_line_handler.get_cell_data()
            cell_conc.append(cell_data['conc'])
            cell_cumulative.append(cell_data['cumulative'])
            cell_integral.append(cell_data['integral'])
            cell_growth_rate.append(cell_data['growth_rate'])

            # metabolite data
            metabolite_data = cell_line_handler.get_metabolite_data()
            conc.append(metabolite_data['conc'])
            cumulative.append(metabolite_data['cumulative'])
            sp_rate.append(metabolite_data['sp_rate'])

        # concat
        cell_conc =  pd.concat(cell_conc, axis=0)
        cell_cumulative = pd.concat(cell_cumulative, axis=0)
        cell_integral = pd.concat(cell_integral, axis=0)
        cell_growth_rate = pd.concat(cell_growth_rate, axis=0)
        conc = pd.concat(conc, axis=0)
        cumulative = pd.concat(cumulative, axis=0)
        sp_rate = pd.concat(sp_rate, axis=0)

        # store data
        self._cell_data['conc'] =  cell_conc
        self._cell_data['cumulative'] = cell_cumulative
        self._cell_data['integral'] = cell_integral
        self._cell_data['growth_rate'] = cell_growth_rate
        self._metabolite_data['conc'] = conc
        self._metabolite_data['cumulative'] = cumulative
        self._metabolite_data['sp_rate'] = sp_rate

    def get_cell_line_handles(self, cell_line_name=None):
        ''''''
        if cell_line_name:
            return self._cell_line_handles[cell_line_name]
        else :
            return self._cell_line_handles
    
    def get_experiment_ids(self):
        ''''''
        id_list = []
        for cell_line_handler in self._cell_line_handles.values():
            id_list += list(cell_line_handler.get_experiment_handle())
        return id_list
    
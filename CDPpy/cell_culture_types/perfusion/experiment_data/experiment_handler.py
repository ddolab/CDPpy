import numpy as np
import pandas as pd

from .GetterMixin import GetterMixin

from CDPpy.experiment_data import ExperimentDataHandler
from CDPpy.cell_culture_types.perfusion.species import Cell, Metabolite
from CDPpy.cell_culture_types.perfusion.in_process import InProcessMixin as Inprocess
from CDPpy.cell_culture_types.perfusion.post_process.polynomial import PolynomialMixin as Polynomial
from CDPpy.cell_culture_types.perfusion.post_process.rolling_window_polynomial import RollingWindowPolynomialMixin as RollingPolynomial
from CDPpy.helper import create_value_unit_df, split_name_unit, create_col_indices
from CDPpy.constants import CELL_LINE_COLUMN, ID_COLUMN
from CDPpy.constants.perfusion.constants import CULTURE_VOLUME_COLUMN, BLEEDING_RATIO_COLUMN, FLOWRATE_COLUMN, VIABLE_CELL_COLUMN, DEAD_CELL_COLUMN, TOTAL_CELL_COLUMN

COLUMNS_TO_DROP = [CELL_LINE_COLUMN, ID_COLUMN]

class PerfusionExperimentHandler(ExperimentDataHandler, GetterMixin, Inprocess, Polynomial, RollingPolynomial):
    '''
    '''
    def __init__(self, cell_line_name, cell_line_id, data) -> None:
        super().__init__(cell_line_name, cell_line_id, data=data, cell_culture_type='perfusion')

        conc_data = data['conc'].copy()
        feed_conc_data = data['feed_conc'].copy()
        feed_mask = (feed_conc_data[CELL_LINE_COLUMN]==cell_line_name) & (feed_conc_data[ID_COLUMN]==cell_line_id)
        
        polynomial_degree_data = data['polynomial_degree_data'].copy()
        polynomial_degree_mask = (polynomial_degree_data[CELL_LINE_COLUMN]==cell_line_name) & (polynomial_degree_data[ID_COLUMN]==cell_line_id)
        
        self._conc_data = conc_data[self._mask].copy().reset_index(drop=True)
        self._feed_conc_data = feed_conc_data[feed_mask].copy().reset_index(drop=True)
        self._feed_conc_data.drop(COLUMNS_TO_DROP, axis=1, inplace=True)
        self._polynomial_degree_data = polynomial_degree_data[polynomial_degree_mask]
        
        df = self._measured_data
        # calculate the dillution rate (hr^-1): 
        #       flow rate (ml/hr) / culture volume (ml)
        culture_volume = df[CULTURE_VOLUME_COLUMN].iat[0]
        beta = df[BLEEDING_RATIO_COLUMN].values
        flow_rate = df[FLOWRATE_COLUMN].values
        rate = flow_rate / culture_volume
        dillution_rate = pd.DataFrame(data=rate, columns=['value'])
        dillution_rate['unit'] = '(hr^-1)'
        dillution_rate.index.name = 'dillution_rate'
        
        self._bleeding_ratio = beta
        self._dillution_rate = dillution_rate
        self._viable_cell_conc = create_value_unit_df(df[VIABLE_CELL_COLUMN])
        self._dead_cell_conc = create_value_unit_df(df[DEAD_CELL_COLUMN])
        self._total_cell_conc = create_value_unit_df(df[TOTAL_CELL_COLUMN])

        # pre-processing
        self._preprocess()

        # work with species object
        self._create_species()

        # work with cell concentration
        run_time = self._run_time
        cell = self.get_species('cell')
        vcd = cell.viable_cell_conc
        vcd['state'] = 'VCD'
        vcd = pd.concat([run_time, vcd], axis=1)

        tcd = cell.total_cell_conc
        tcd['state'] = 'TCD'
        tcd = pd.concat([run_time, tcd], axis=1)

        dcd = cell.dead_cell_conc
        dcd['state'] = 'DCD'
        dcd = pd.concat([run_time, dcd], axis=1)

        viab = cell.viability
        viab['state'] = 'Viability'
        viab = pd.concat([run_time, viab], axis=1)

        cell_conc = pd.concat([vcd, tcd, dcd, viab], axis=0).reset_index(drop=True)
        cell_conc['ID'] = self.cell_line_id
        self._cell_conc = cell_conc

    def _create_species(self):
        '''crate specise object to analyze.'''
        spc_dict = {}
        run_time = self._run_time
        bleeding_ratio = self._bleeding_ratio
        dillution_rate = self._dillution_rate
        viable_cell = self._viable_cell_conc
        dead_cell = self._dead_cell_conc
        total_cell = self._total_cell_conc
        conc_df = self._conc_data
        feed_conc_df = self._feed_conc_data

        # Get indices
        conc_indices = create_col_indices(conc_df)
        feed_conc_indices = create_col_indices(feed_conc_df)

        cell = Cell(run_time_df=run_time, 
                    bleeding_ratio=bleeding_ratio,
                    dillution_rate=dillution_rate,
                     viable_cell_conc=viable_cell, 
                    dead_cell_conc=dead_cell, 
                    total_cell_conc=total_cell)
        spc_dict['cell'] = cell

        for name in conc_indices.keys():
            # Conc. before feeding
            index = conc_indices[name]['index']
            data = conc_df.iloc[:, index]
            conc = create_value_unit_df(data)
            
            # Feeed conc.
            index = feed_conc_indices[name]['index']
            data = feed_conc_df.iloc[:, index]
            feed_conc = create_value_unit_df(data)

            metabolite = Metabolite(name=name, 
                                    run_time_df=run_time,
                                    dillution_rate=dillution_rate,
                                    conc=conc,
                                    feed_conc=feed_conc,
                                    viable_cell_conc=viable_cell)
            spc_dict[name.lower()] = metabolite
            self._spc_dict = spc_dict

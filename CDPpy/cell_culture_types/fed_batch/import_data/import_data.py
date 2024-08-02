import pandas as pd
import numpy as np

from CDPpy.helper import input_path, split_df, create_value_unit_df, remove_units
from CDPpy.constants.fed_batch.column_name import EXPERIMENT_DATA_COLUMN, CONC_BEFOROE_FEED_COLUMN, CONC_AFTER_FEED_COLUMN, CUMULATIVE_CONC_COLUMN, SP_RATE_COLUMN, SP_RATE_POLY_COLUMN, SP_RATE_ROLLING_COLUMN
from CDPpy.constants.fed_batch.column_name import RUN_TIME_DAY_COLUMN, RUN_TIME_HOUR_COLUMN, RUN_TIME_DAY_MID_COLUMN, RUN_TIME_HOUR_MID_COLUMN, CELL_LINE_COLUMN, ID_COLUMN, VIABLE_CELL_COLUMN, DEAD_CELL_COLUMN, TOTAL_CELL_COLUMN, PRODUCT_COLUMN, VIABILITY_COLUMN
from CDPpy.constants import SPECIES_STATE

TARGET_COLUMNS = [EXPERIMENT_DATA_COLUMN, 
                  CONC_BEFOROE_FEED_COLUMN, 
                  CONC_AFTER_FEED_COLUMN,
                  CUMULATIVE_CONC_COLUMN,
                  SP_RATE_COLUMN]

class ImportMixin:
    '''import processed data file.'''

    def import_data(self, file_name, sheet_name='Processed Data'):
        ''''''
        if not '.xlsx' in file_name:
            print('Invalid extension. Use .xlsx')
            return
        path = input_path(file_name=file_name)
        imported_data = pd.read_excel(io=path, sheet_name=sheet_name)

        # Rename columns
        new_columns = [col if 'Unnamed' not in col else '' for col in imported_data.columns]
        imported_data.columns = new_columns

        # store imported processed data for plotting
        if SP_RATE_POLY_COLUMN in imported_data.columns:
            TARGET_COLUMNS.append(SP_RATE_POLY_COLUMN)

        if SP_RATE_ROLLING_COLUMN in imported_data.columns:
            TARGET_COLUMNS.append(SP_RATE_ROLLING_COLUMN)
        
        # Split data
        data_list = split_df(imported_data, TARGET_COLUMNS)
        taerget_column_indices = dict(zip(TARGET_COLUMNS, np.arange(len(TARGET_COLUMNS))))

        exp_data = data_list[taerget_column_indices[EXPERIMENT_DATA_COLUMN]]
        conc_before_data = data_list[taerget_column_indices[CONC_BEFOROE_FEED_COLUMN]]
        conc_after_data = data_list[taerget_column_indices[CONC_AFTER_FEED_COLUMN]]
        cumulative_data = data_list[taerget_column_indices[CUMULATIVE_CONC_COLUMN]]
        sp_rate_data = data_list[taerget_column_indices[SP_RATE_COLUMN]]
        
        if SP_RATE_POLY_COLUMN in imported_data.columns:
            print(taerget_column_indices[SP_RATE_POLY_COLUMN])
            sp_rate_poly_data = data_list[taerget_column_indices[SP_RATE_POLY_COLUMN]]
        else:
            sp_rate_poly_data = None

        if SP_RATE_ROLLING_COLUMN in imported_data.columns:
            sp_rate_rolling_data = data_list[taerget_column_indices[SP_RATE_ROLLING_COLUMN]]
        else:
            sp_rate_rolling_data = None
        
        self._imported_data_list = data_list

        cell_line_id = exp_data[[ID_COLUMN, CELL_LINE_COLUMN]]
        run_time = exp_data[[RUN_TIME_DAY_COLUMN, RUN_TIME_HOUR_COLUMN]]

        processed_info = {}
        for cell_line in cell_line_id['Cell Line'].unique():
            processed_info[cell_line] = list(cell_line_id[cell_line_id['Cell Line']==cell_line]['ID'].unique())
        self._processed_cell_lines.update(processed_info)

        self._get_processed_cell_data(cell_line_id, run_time, exp_data, cumulative_data, sp_rate_data, sp_rate_poly_data, sp_rate_rolling_data)
        self._get_processed_metabolite_data(cell_line_id, run_time, exp_data, conc_before_data, conc_after_data, cumulative_data, sp_rate_data, sp_rate_poly_data, sp_rate_rolling_data)

        # Concat all processed data
        if self._processed_data.size==0:
            self._processed_data = imported_data
        else:
            df = self._processed_data.iloc[2:]
            self._processed_data = pd.concat([df, imported_data], axis=0)

    def _get_processed_cell_data(self, cell_line_id, run_time, exp_data, cumulative, sp_rate, sp_rate_poly, sp_rate_rolling):
        ''''''
        # Create Concentration data
        vcc = create_value_unit_df(exp_data[VIABLE_CELL_COLUMN])
        dcc = create_value_unit_df(exp_data[DEAD_CELL_COLUMN])
        tcc = create_value_unit_df(exp_data[TOTAL_CELL_COLUMN])
        viab = create_value_unit_df(exp_data[VIABILITY_COLUMN])

        vcc['state'] = 'VCD'
        dcc['state'] = 'DCD'
        tcc['state'] = 'TCD'
        viab['state'] = 'Viability'

        conc_df_list = [pd.concat([run_time, data, cell_line_id], axis=1) for data in [vcc, tcc, dcc, viab]]
        conc_df = pd.concat(conc_df_list, axis=0, ignore_index=True)

        # Create Cumulative production and IVCC data
        cumu = create_value_unit_df(cumulative['Cell (10^6 cells)'])
        cumu['method'] = 'twoPoint'
        ivcc = create_value_unit_df(cumulative['IVCC (10^6 cells hr/mL)'])

        cumu_df = pd.concat([run_time, cumu, cell_line_id], axis=1)
        ivcc_df = pd.concat([run_time, ivcc, cell_line_id], axis=1)

        # Create SP. rate data
        growth_rate = create_value_unit_df(sp_rate['Cell (hr^-1)'])
        growth_rate['method'] = 'twoPoint'
        growth_rate_df = pd.concat([run_time, growth_rate, cell_line_id], axis=1)

        if not sp_rate_poly is None:
            growth_rate_poly = create_value_unit_df(sp_rate_poly['Cell (hr^-1)'])
            growth_rate_poly['method'] = 'polynomial'
            growth_rate_poly_df = pd.concat([run_time, growth_rate_poly, cell_line_id], axis=1)
            growth_rate_df = pd.concat([growth_rate_df, growth_rate_poly_df], axis=0, ignore_index=True)

        if not sp_rate_rolling is None:
            # run_time_mid = sp_rate_rolling[[RUN_TIME_DAY_MID_COLUMN, RUN_TIME_HOUR_MID_COLUMN]]
            # run_time_mid = run_time_mid.rename(columns={RUN_TIME_DAY_MID_COLUMN: RUN_TIME_DAY_COLUMN,
            #                                             RUN_TIME_HOUR_MID_COLUMN: RUN_TIME_HOUR_COLUMN})
            growth_rate_roll = create_value_unit_df(sp_rate_rolling['Cell (hr^-1)'])
            growth_rate_roll['method'] = 'rollingWindowPolynomial'
            growth_rate_roll_df = pd.concat([run_time, growth_rate_roll, cell_line_id], axis=1)
            growth_rate_df = pd.concat([growth_rate_df, growth_rate_roll_df], axis=0, ignore_index=True)

        # store
        data = {}
        data['conc'] = conc_df
        data['cumulative'] = cumu_df
        data['integral'] = ivcc_df
        data['growth_rate'] = growth_rate_df

        self._cell_data
        self._cell_data['conc'] = pd.concat([self._cell_data['conc'], conc_df])
        self._cell_data['integral'] = pd.concat([self._cell_data['integral'], ivcc_df])
        self._cell_data['cumulative'] = pd.concat([self._cell_data['cumulative'], cumu_df])
        self._cell_data['growth_rate'] = pd.concat([self._cell_data['growth_rate'], growth_rate_df])

        self._imported_cell_data = data

    def _get_processed_metabolite_data(self, cell_line_id, run_time, exp_data, conc_before, conc_after, cumulative, sp_rate, sp_rate_poly, sp_rate_rolling):
        ''''''
        # Delete Cell and IVCC
        del cumulative['Cell (10^6 cells)']
        del cumulative['IVCC (10^6 cells hr/mL)']
        del sp_rate['Cell (hr^-1)']

        # IgG concentration 
        conc_df_list = []
        product = create_value_unit_df(exp_data['IgG (mg/L)'])
        product['species'] = 'IgG'
        product_df = pd.concat([run_time, product, cell_line_id], axis=1)
        conc_df_list.append(product_df)

        # Concentration
        for col1, col2 in zip(conc_before.columns, conc_after.columns):
            temp1 = create_value_unit_df(conc_before[col1])
            temp1['species'] = remove_units(col1).capitalize()
            temp2 = create_value_unit_df(conc_after[col2])
            temp2['species'] = remove_units(col2).capitalize()
            temp1_df = pd.concat([run_time, temp1, cell_line_id], axis=1)
            temp2_df = pd.concat([run_time, temp2, cell_line_id], axis=1)

            temp = pd.concat([temp1_df, temp2_df], axis=0)
            temp = temp.sort_values(by=[RUN_TIME_HOUR_COLUMN], kind='stable', ignore_index=True)
            conc_df_list.append(temp)
        conc_df = pd.concat(conc_df_list, axis=0)

        # Create Cumulative production/consumption
        cumu_df_list = []
        for col in cumulative.columns:
            name = remove_units(col)
            name = name.capitalize() if name != 'IgG' else 'IgG'
            temp = create_value_unit_df(cumulative[col])
            temp['state'] = SPECIES_STATE[name]
            temp['method'] = 'twoPoint'
            temp['species'] = name
            temp_df = pd.concat([run_time, temp, cell_line_id], axis=1)
            cumu_df_list.append(temp_df)
        cumu_df = pd.concat(cumu_df_list, axis=0)
            
        # Create SP. rate data
        sp_rate_df_list = []
        for col in sp_rate.columns:
            name = remove_units(col)
            name = name.capitalize() if name != 'IgG' else 'IgG'

            temp = create_value_unit_df(sp_rate[col])
            temp['method'] = 'twoPoint'
            temp['species'] = name
            temp_df = pd.concat([run_time, temp, cell_line_id], axis=1)
            sp_rate_df_list.append(temp_df)
        sp_rate_df = pd.concat(sp_rate_df_list, axis=0)
        
        if not sp_rate_poly is None:
            del sp_rate_poly['Cell (hr^-1)']

            sp_rate_poly_df_list = []
            for col in sp_rate_poly.columns:
                name = remove_units(col)
                name = name.capitalize() if name != 'IgG' else 'IgG'

                temp = create_value_unit_df(sp_rate_poly[col])
                temp['method'] = 'polynomial'
                temp['species'] = name
                temp_df = pd.concat([run_time, temp, cell_line_id], axis=1)
                sp_rate_poly_df_list.append(temp_df)
            sp_rate_poly_df = pd.concat(sp_rate_poly_df_list, axis=0)
            sp_rate_df = pd.concat([sp_rate_df, sp_rate_poly_df], axis=0, ignore_index=True)

        if not sp_rate_rolling is None:
            del sp_rate_rolling['Cell (hr^-1)']
            # run_time_mid = sp_rate_rolling[[RUN_TIME_DAY_MID_COLUMN, RUN_TIME_HOUR_MID_COLUMN]]
            # run_time_mid = run_time_mid.rename(columns={RUN_TIME_DAY_MID_COLUMN: RUN_TIME_DAY_COLUMN,
            #                                             RUN_TIME_HOUR_MID_COLUMN: RUN_TIME_HOUR_COLUMN})
            
            sp_rate_roll_df_list = []
            for col in sp_rate_rolling.columns:
                name = remove_units(col)
                name = name.capitalize() if name != 'IgG' else 'IgG'

                temp = create_value_unit_df(sp_rate_rolling[col])
                temp['method'] = 'rollingWindowPolynomial'
                temp['species'] = name
                temp_df = pd.concat([run_time, temp, cell_line_id], axis=1)
                sp_rate_roll_df_list.append(temp_df)
            sp_rate_rolling_df = pd.concat(sp_rate_roll_df_list, axis=0)
            sp_rate_df = pd.concat([sp_rate_df, sp_rate_rolling_df], axis=0, ignore_index=True)

        # store
        data = {}
        data['conc'] = conc_df
        data['cumulative'] = cumu_df
        data['sp_rate'] = sp_rate_df

        self._metabolite_data['conc'] = pd.concat([self._metabolite_data['conc'], conc_df])
        self._metabolite_data['cumulative'] = pd.concat([self._metabolite_data['cumulative'], cumu_df])
        self._metabolite_data['sp_rate'] = pd.concat([self._metabolite_data['sp_rate'], sp_rate_df])

        self._imported_metabolite_data = data
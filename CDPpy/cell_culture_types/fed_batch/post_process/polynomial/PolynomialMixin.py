import pandas as pd

from CDPpy.helper import add_descriptive_column
from CDPpy.constants import CELL_LINE_COLUMN, ID_COLUMN
from CDPpy.constants.fed_batch.column_name import SP_RATE_POLY_COLUMN

COLUMNS_TO_DROP = [CELL_LINE_COLUMN, ID_COLUMN]

class PolynomialMixin:
    '''
    Polynomial Mixin class for polynomial regression.
    Methods
    -------
    '''
    def polynomial(self):
        '''
        Calculate cumulative consumptions/productions and sp. rate for species using polynomial regression.
        '''
        species = self.get_species('all')
        species_list = list(species.keys())

        polynomial_degree = self.get_polynomial_degree().copy()
        polynomial_degree.drop(COLUMNS_TO_DROP, axis=1, inplace=True)
        polynomial_degree.columns = [s.lower() for s in polynomial_degree.columns]

        # initialize df for logging
        sp_rate_dataframe = pd.DataFrame()

        # initialize list to store data for plottng
        cumulative_conc_df_list = []
        sp_rate_df_list = []
        
        if 'cell' in species_list:
            name = 'cell'
            species_list.remove(name)
            cell = species[name]
            if polynomial_degree.get(name, None) is None or polynomial_degree.get(name, None).empty:
                deg = 3
            else:
                deg = polynomial_degree[name].iat[0]

            cell.polynomial(deg)

            cumulative_conc = cell.cumulative_conc.copy()
            cumulative_conc_poly = cell.cumulative_conc_poly.copy()
            cumulative_conc_data = pd.concat([cumulative_conc, cumulative_conc_poly], axis=0).reset_index(drop=True)
            cumulative_conc_data['ID'] = self.cell_line_id
            cell.cumulative_conc = cumulative_conc_data

            sp_rate = cell.growth_rate.copy()
            sp_rate_poly = cell.sp_rate_poly.copy()
            sp_rate_data = pd.concat([sp_rate, sp_rate_poly], axis=0).reset_index(drop=True)
            sp_rate_data['ID'] = self.cell_line_id
            cell.growth_rate = sp_rate_data

            sp_rate_dataframe[f"Cell {sp_rate_poly['unit'].iat[0]}"] = sp_rate_poly['value']

        if 'IgG' in species_list:
            name = 'IgG'
            species_list.remove(name)
            prod = species[name]
            if polynomial_degree.get('igg', None) is not None:
                deg = polynomial_degree['igg'].iat[0]
            elif polynomial_degree.get(name, None) is not None:
                deg = polynomial_degree[name].iat[0]
            else:
                deg = 3
            prod.polynomial(deg)

            cumulative_data = prod.cumulative_conc_poly.copy()
            cumulative_data['species'] = prod.name
            cumulative_conc_df_list.append(cumulative_data)

            sp_rate_data = prod.sp_rate_poly.copy()
            sp_rate_data['species'] = prod.name
            sp_rate_df_list.append(sp_rate_data)

            sp_rate_dataframe[f"{prod.name} {sp_rate_data['unit'].iat[0]}"] = sp_rate_data['value']

        if 'oxygen' in species_list:
            species_list.remove('oxygen')
            prod = species['oxygen']
            prod.in_process()

        for name in species_list:
            spc = species[name]
            if polynomial_degree.get(name, None) is None or polynomial_degree.get(name, None).empty:
                deg = 3
            else:
                deg = polynomial_degree[name].iat[0]

            spc.polynomial(deg)

            cumulative_data = spc.cumulative_conc_poly.copy()
            cumulative_data['species'] = name.capitalize()
            cumulative_conc_df_list.append(cumulative_data)

            sp_rate_data = spc.sp_rate_poly.copy()
            sp_rate_data['species'] = name.capitalize()
            sp_rate_df_list.append(sp_rate_data)

            sp_rate_dataframe[f"{name.capitalize()} {sp_rate_data['unit'].iat[0]}"] = sp_rate_data['value']
        
        cumulative_conc_poly_df = pd.concat(cumulative_conc_df_list, axis=0, ignore_index=True)
        sp_rate_poly_df = pd.concat(sp_rate_df_list, axis=0, ignore_index=True)

        cumulative_conc = self.cumulative_conc
        sp_rate = self.sp_rate

        cumulative_conc_data = pd.concat([cumulative_conc, cumulative_conc_poly_df], axis=0, ignore_index=True)
        cumulative_conc_data['ID'] = self.cell_line_id
        sp_rate_data = pd.concat([sp_rate, sp_rate_poly_df], axis=0, ignore_index=True)
        sp_rate_data['ID'] = self.cell_line_id
        
        self.cumulative_conc = cumulative_conc_data
        self.sp_rate = sp_rate_data

        self._sp_rate_data_poly = sp_rate_dataframe

        # concat all processed data
        processed_data = self._processed_data
        sp_rate = add_descriptive_column(sp_rate_dataframe, SP_RATE_POLY_COLUMN)
        self._processed_data = pd.concat([processed_data, sp_rate], axis=1)
        
        # Cumulative for Nitrogen, and AA Carbon
        # self.__cumulative_others()

        # Set in process flag True
        # self.set_process_flag(process='inpro', flag=True)

    def get_sp_rate_poly(self):
        return self._sp_rate_data_poly

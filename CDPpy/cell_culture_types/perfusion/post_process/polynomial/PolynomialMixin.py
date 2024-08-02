import pandas as pd

from CDPpy.constants import CELL_LINE_COLUMN, ID_COLUMN

COLUMNS_TO_DROP = [CELL_LINE_COLUMN, ID_COLUMN]

class PolynomialMixin:
    '''
    '''
    def polynomial(self):
        '''
        '''
        # Get species dictionary
        species = self.get_species()
        species_list = list(species.keys())

        polynomial_degree = self.get_polynomial_degree().copy()
        polynomial_degree.drop(COLUMNS_TO_DROP, axis=1, inplace=True)
        polynomial_degree.columns = [s.lower() for s in polynomial_degree.columns]

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
            self._cumulative_cell_production = cumulative_conc_data

        # Metabolite
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

        cumulative_conc_poly_df = pd.concat(cumulative_conc_df_list, axis=0, ignore_index=True)
        sp_rate_poly_df = pd.concat(sp_rate_df_list, axis=0, ignore_index=True)

        cumulative_conc = self.cumulative_conc
        sp_rate = self.sp_rate

        cumulative_conc_data = pd.concat([cumulative_conc, cumulative_conc_poly_df], axis=0, ignore_index=True)
        cumulative_conc_data['ID'] = self.cell_line_id
        sp_rate_data = pd.concat([sp_rate, sp_rate_poly_df], axis=0, ignore_index=True)
        
        self.cumulative_conc = cumulative_conc_data
        self.sp_rate = sp_rate_data
    
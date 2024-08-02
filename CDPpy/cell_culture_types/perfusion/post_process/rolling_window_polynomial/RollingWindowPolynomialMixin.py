import pandas as pd

from CDPpy.constants import CELL_LINE_COLUMN, ID_COLUMN

class RollingWindowPolynomialMixin:
    ''''''
    def rolling_window_polynomial(self, degree=3, window=6):
        # Get species dictionary
        species = self.get_species()
        species_list = list(species.keys())

        sp_rate_df_list = []

        # remove cell
        species_list.remove('cell')

        # Metabolite
        for name in species_list:
            spc = species[name]
            spc.rolling_window_polynomial(degree, window)

            sp_rate_data = spc.sp_rate_rolling.copy()
            sp_rate_data['species'] = name.capitalize()
            sp_rate_df_list.append(sp_rate_data)

        # concat sp. rate for rolling polynomial
        sp_rate_rolling_df = pd.concat(sp_rate_df_list, axis=0, ignore_index=True)
        # stored sp. rate
        sp_rate = self.sp_rate

        # concat 
        sp_rate_data = pd.concat([sp_rate, sp_rate_rolling_df], axis=0, ignore_index=True)
        sp_rate_data['ID'] = self.cell_line_id
        
        # save
        self.sp_rate = sp_rate_data
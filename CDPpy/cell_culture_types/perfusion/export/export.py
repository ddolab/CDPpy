import pandas as pd

from CDPpy.helper import output_path

class ExportMixin:
    '''Export Mixin class to save processed data.'''
    def save_excel(self, file_name):
        '''
        '''
        if not '.xlsx' in file_name:
            print('Invalid extension. Use .xlsx')
            return
        cell_data = self.get_cell_data().copy()
        data = self.get_metabolite_data().copy()

        # Renaming keys
        cell_data['Cell Concentration'] = cell_data['conc']
        cell_data['Cumulative Cell Production'] = cell_data['cumulative']
        cell_data['Cell Death Rate'] = cell_data['death_rate']
        cell_data['Cell Growth Rate'] = cell_data['growth_rate']

        data['Concentration'] = data['conc']
        data['Cumulative Concentration'] = data['cumulative']
        data['SP Rate'] = data['sp_rate']

        # Delete old keys
        del cell_data['conc']
        del cell_data['cumulative']
        del cell_data['death_rate']
        del cell_data['growth_rate']
        del data['conc']
        del data['cumulative']
        del data['sp_rate']

        # Export data as Excel file
        path = output_path(file_name=file_name)
        with pd.ExcelWriter(path) as writer:  
            for sheet_name, df_sheet in cell_data.items():
                df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

            for sheet_name, df_sheet in data.items():
                df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
        print(file_name, ' saved.')
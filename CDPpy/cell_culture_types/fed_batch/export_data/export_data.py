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
        
        data = {'Processed Data': self.get_processed_data()}

        # Export data as Excel file
        path = output_path(file_name=file_name)
        with pd.ExcelWriter(path) as writer:  
            for sheet_name, df_sheet in data.items():
                df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
        print(file_name, ' saved.')
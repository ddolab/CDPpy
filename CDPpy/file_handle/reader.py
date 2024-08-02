import pandas as pd

from CDPpy.helper import input_path


class _DefaultReader:
    def read(self, file):
        file_path = input_path(file)
        sheets_dict = pd.read_excel(file_path, sheet_name=None)
        return sheets_dict
    
DEFAULT_READER = _DefaultReader()
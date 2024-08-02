from CDPpy.file_handle import FileHandler
# from CCDPApy.cell_culture_types.fed_batch.cell_line_data import FedBatchCellLineDataHandler
# from CCDPApy.cell_culture_types.perfusion.cell_line_data.cell_line_data_handler import PerfusionCellLineDataHandler

class CellCultureDataHandler:
    '''
    '''
    def __init__(self, cell_culture_type) -> None:
        self._cell_culture_type = cell_culture_type
        # Define cell line and experiment data handler
        '''
        if cell_culture_type=='fed-batch':
            self._cell_line_handler = FedBatchCellLineDataHandler
            
        elif cell_culture_type=='perfusion':
            self._cell_line_handler = PerfusionCellLineDataHandler
        '''

        # file handler
        self._file_handler = FileHandler

        # Processed Cell line name and ID
        self._processed_cell_lines = {}

    def load_data(self, file):
        '''load an excel file and return the dictionary.'''
        file_handler = self._file_handler(file=file)
        return file_handler.read()

    def get_cell_line_names(self):
        '''get cell line names.'''
        return self._cell_line_names
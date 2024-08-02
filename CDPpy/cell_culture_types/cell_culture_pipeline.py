from CDPpy.cell_culture_types.fed_batch.cell_culture_data.cell_culture_data_handler import FedBatchCellCultureDataHandler
from CDPpy.cell_culture_types.perfusion.cell_culture_data.cell_culture_data_handler import PerfusionCellCultureDataHandler
from CDPpy.helper import input_path

def cell_culture_pipeline(cell_culture_type, file=None):
    ''''''

    if cell_culture_type=='perfusion':
        cell_culture_data_handler = PerfusionCellCultureDataHandler
    elif cell_culture_type=='fed-batch':
        cell_culture_data_handler = FedBatchCellCultureDataHandler
    else:
        print('Wrong cell culture type. Please pass "perfusion" or "fed-batch".')
        return
    
    # call cell culture data handler
    cell_culture = cell_culture_data_handler()

    # load data file
    if file:
        file_path = input_path(file_name=file)
        cell_culture.load_data(file=file_path)

    return cell_culture

class CellCulturePipeline:
    def __init__(self, cell_culture_type, file) -> None:
        if cell_culture_type=='perfusion':
            cell_culture_data_handler = PerfusionCellCultureDataHandler
        elif cell_culture_type=='fed-batch':
            cell_culture_data_handler = FedBatchCellCultureDataHandler
        else:
            print('Wrong cell culture type. Please pass "perfusion" or "fed-batch".')
            return
    
        # call cell culture data handler
        cell_culture = cell_culture_data_handler()

        # load data file
        file_path = input_path(file_name=file)
        cell_culture.load_data(file=file_path)

        # store
        self._cell_culture = cell_culture

    def perform_data_process(self, parametes):
        '''Perform data-processing.'''
        self._cell_culture.perform_data_process(parameters=parametes)

    def import_data(self, file):
        '''Importing processed data.'''
        self._cell_culture.import_data(file_name=file)



from CDPpy.constants import CELL_LINE_COLUMN, ID_COLUMN
from CDPpy.constants.fed_batch.dict_key import EXP_DATA_KEY, SPC_CONC_BEFORE_FEED_KEY, SPC_CONC_AFTER_FEED_KEY, SPC_FEED_CONC_KEY

from CDPpy.cell_culture_types.fed_batch.experiment_data import FedBatchExperimentHandler
from CDPpy.cell_culture_types.perfusion.experiment_data.experiment_handler import PerfusionExperimentHandler
class CellLineDataHandler:
    '''
    '''
    def __init__(self, cell_line_name, data, cell_culture_type=None) -> None:
        '''
        '''
        # Define cell line and experiment data handler
        if cell_culture_type=='fed-batch':
            self._experiment_handler = FedBatchExperimentHandler
            
        elif cell_culture_type=='perfusion':
            self._experiment_handler = PerfusionExperimentHandler

        df = data[EXP_DATA_KEY].copy()

        # Check Cell Line name
        assert df[CELL_LINE_COLUMN].isin([cell_line_name]).any(), f"Cell Line '{cell_line_name}' is not in data file."
        mask = df[CELL_LINE_COLUMN]==cell_line_name
        data_masked = df[mask].copy()

        self._cell_line_name = cell_line_name
        self._mask = mask
        self._measured_data = data_masked
        self._experiment_names = list(data_masked[ID_COLUMN].unique())
        self._spc_conc_before = data[SPC_CONC_BEFORE_FEED_KEY]
        self._spc_conc_after = data[SPC_CONC_AFTER_FEED_KEY]
        self._spc_feed = data[SPC_FEED_CONC_KEY]
    
    def get_experiment_names(self):
        '''get experiment names in the cell culture.'''
        return self._experiment_names
    
    def get_measured_data(self):
        '''get measured data.'''
        return self._measured_data
    
    @property
    def cell_line_name(self):
        return self._cell_line_name
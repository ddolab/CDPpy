from math import ceil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..helper_func.helper_func import output_path

###########################################################################
class SRatioMixin:
    '''Plot stoicheometric ratios.
    '''

    def plot_s_ratio(self, spc_list, x_spc=None, file_name=None):
        '''
        Plot stoichiometric ratios.

        Parameters:
        ----------
            spc_list : str, list of str
                species name to plot
            x_spc : str, default=None, optional
                species name to be plotted on x axis.
            file_name: str, default=None, optional
                file name to save a plot.
        '''

        # Make spcies names upper case
        if type(spc_list)==str:
            spc_list = [spc_list.upper()]
        elif type(spc_list)==list:
            spc_list = [s.upper() for s in spc_list]
        print(spc_list)

        # Config
        col = 3 if len(spc_list) > 2 else len(spc_list)
        row = ceil(len(spc_list) / col)
        # Cleate fig and axes
        fig, axes = plt.subplots(row, col, figsize=(8*col, 6*row), tight_layout=True, squeeze=False)

        # x: Glucose cumulative
        x_spc = 'GLUCOSE' if not x_spc else x_spc.upper()
        x = self._spc_dict[x_spc].get_cumulative()

        # Start index
        row_idx = 0
        col_idx = 0

        # Plotting
        for spc in spc_list:
            # y: cumulative consumption for species
            y = self._spc_dict[spc].get_cumulative()
            # Scatter plot
            axes[row_idx, col_idx].scatter(x, y)
            # Plot setting
            axes[row_idx, col_idx].set_title('Stoichiometric Ratio', loc='left')
            axes[row_idx, col_idx].set_xlabel(f'{x_spc.lower()} (mmol)')
            axes[row_idx, col_idx].set_ylabel(f'{spc.lower()} (mmol)')
            axes[row_idx, col_idx].grid(color = 'gray', linestyle = '--', linewidth = 0.5)
            col_idx += 1
            
            if (col_idx > 2):
                col_idx = 0
                row_idx += 1

        # Saving a plot as an image.
        if file_name:
            self.__save_plot(file_name=file_name)

        return fig

    def __save_plot(self, file_name):
        # Saving
        if (file_name):
            if '.png' not in file_name:
                file_name += '.png'
            # Get output file path
            file_path = output_path(file_name=file_name)

            plt.savefig(file_path)
            print(f'{file_name} Saved')
        

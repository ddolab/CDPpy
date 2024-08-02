import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from CDPpy.helper import output_path

class PlotMixin:
    '''
    Plot Function for Cell Line Class
    '''
    # Plotting different experiments in a cell line on the same figure.
    def plot_exps(self, cell_line, spc_list, method='all',
                  exp_list=None, legend=True, file_name=None):
        '''
        Plot different experiments in a cell line on the same figure.

        Parameters
        ----------
            cell_line : str
                Cell line name to plot experiments.
            spc_list :  llist of str
                Spcies name list to plot the profiles.
            method :default='all', optional
                Method to plot specific rates for species.
                'all' for all methods, 
                'towpt' for two-point calcuations, 
                'polyreg' for polynomial regression,
                'rollreg' for rolling polynomial regression.
            exp_list : default=None, optional
                List Experience ID to plot. 
            legend : default=True, optional
                When True, legends are plotted on the figure.
            file_name : default=None, optional
                File name to save the plot.
        '''
        # Initialize methods as True
        twopt = False
        polyreg = False
        rollreg = False

        # Check Methods
        if 'all' in method:
            twopt = True
            polyreg = True
            rollreg = True
        if 'twopt' in method:
            twopt = True
        if 'polyreg' in method:
            polyreg = True
        if 'rollreg' in method:
            rollreg = True
 
        # Bioprocess dictionary
        bp_dict = self._cell_line_dict[cell_line]

        # Check Experiment List
        if (not exp_list):
            exp_list = [exp_id for exp_id in bp_dict.keys()]

        # Check legend
        if (legend):
            legend = 'auto'

        # Create figure and the adjusments
        fig, ax = plt.subplots(len(spc_list), 3, figsize=(24, 8*len(spc_list)))
        fig.tight_layout(rect=[0,0,1,0.96])
        plt.subplots_adjust(wspace=0.2, hspace=0.3)
        fig.suptitle(f'Profiles for {exp_list}')

        print(f'Makeing a plot for {exp_list}')
        for i, s in enumerate(spc_list):
            inpro_df_lst = []   # In process list for different experiments
            conc_df_lst = []    # Concentration list for different experiments
            cumulative_lst = [] # Cumulative list for different experiments
            sp_rate_df_lst = [] # SP. rate list for different experiments
            for exp in exp_list:
                spc = bp_dict[exp].get_spc_dict()[s.upper()] # spc object
                inpro_df = spc.get_inpro_df()   # inpro df
                conc_df = spc.get_conc_df() # concenration df for spceis
                cumulative_df = spc.get_cumulative_df() # cumulative df for species
                sp_rate_df = spc.get_sp_rate_df(twopt=twopt,
                                                polyreg=polyreg,
                                                rollreg=rollreg) # sp. rate df for species
                
                # Append each df to each list
                inpro_df_lst.append(inpro_df)
                conc_df_lst.append(conc_df)
                cumulative_lst.append(cumulative_df)
                sp_rate_df_lst.append(sp_rate_df)

            # Concatnating each df list to make a df for different experiments
            inpro = pd.concat(inpro_df_lst, axis=0, ignore_index=True)
            conc = pd.concat(conc_df_lst, axis=0, ignore_index=True)#.sort_values('RUN TIME (HOURS)')
            cumulative = pd.concat(cumulative_lst, axis=0, ignore_index=True)#.sort_values('RUN TIME (HOURS)')
            sp_rate = pd.concat(sp_rate_df_lst, axis=0, ignore_index=True)#.sort_values('RUN TIME (HOURS)')

            # Plot Conentration
            set_ax = ax[i, 0] if len(spc_list) != 1 else ax[0]
            sns.lineplot(ax=set_ax, data=conc, x='RUN TIME (HOURS)', y=f'CONC.',
                         hue="Experiment ID", hue_order=exp_list,
                         legend=legend,
                         estimator=None)
            set_ax.set_title(f'{s.upper()} Concentration Profile', loc='center')
            set_ax.set_ylabel('Concentration (mM)')
            set_ax.grid(color = 'gray', linestyle = '--', linewidth = 0.5)

            # Plot Cumulative Consumption/Production
            set_ax = ax[i, 1] if len(spc_list) != 1 else ax[1]
            sns.scatterplot(ax=set_ax, data=inpro, x='RUN TIME (HOURS)', y=f'CUM {s.upper()} (mmol)',
                            hue="Experiment ID", hue_order=exp_list,
                            style="Experiment ID",
                            legend=legend)
            sns.lineplot(ax=set_ax, data=cumulative, x='RUN TIME (HOURS)', y=f'CUM {s.upper()} (mmol)',
                            hue="Experiment ID", hue_order=exp_list,
                            style='Method',
                            legend=legend)
            set_ax.set_title(f'{s.upper()} Cumulative Profile', loc='center')
            set_ax.set_ylabel('Cumulative (mmol)')
            set_ax.grid(color = 'gray', linestyle = '--', linewidth = 0.5)

            # Plot Sp. Rate.
            set_ax = ax[i, 2] if len(spc_list) != 1 else ax[2]
            sns.lineplot(ax=set_ax, data=sp_rate, x='RUN TIME (HOURS)', y=f'q{s.upper()} (mmol/109 cell/hr)',
                            hue="Experiment ID", hue_order=exp_list,
                            style='Method',
                            legend=legend)
            sns.set_theme(style="whitegrid")
            set_ax.set_title(f'{s.upper()} Specific-Rate Profile', loc='center')
            set_ax.set_ylabel('SP. rate (mmol/109 cell/hr)')
            set_ax.grid(color = 'gray', linestyle = '--', linewidth = 0.5)

        # Saving
        if (file_name):
            if '.png' not in file_name:
                file_name += '.png'
            # Get output file path
            file_path = output_path(file_name=file_name)

            plt.savefig(file_path)
            print(f'{file_name} Saved')

        return fig



    # Plotting different cell lines and experiments on the same figure.
    def plot_cell_lines(self, spc_list, compare_cell_line, method='all',
                        cell_line_list=None, estimator=None,
                        file_name=None, legend=True):
        '''
        Plot different cell lines and experiments on the same figure.

        Parameters
        ----------
            spc_list :  llist of str
                Spcies name list to plot the profiles.
            compare_cell_line : bool
                When True, experiments of the same cell line are colored in the same color.
            method : list of str default='all', optional
                Method to plot specific rates for species.
                'all' for all methods, 
                'towpt' for two-point calcuations, 
                'polyreg' for polynomial regression,
                'rollreg' for rolling polynomial regression.
            cell_line_list : list of str, default=None, optional
            estimator : str default=None, optional
            legend : default=True, optional
                When True, legends are plotted on the figure.
            file_name : default=None, optional
                File name to save the plot.
        '''

        # Initialize methods as false
        twopt=False
        polyreg=False
        rollreg=False

        # Check methods
        if 'all' in method:
            twopt=True
            polyreg=True
            rollreg=True

        if 'twopt' in method:
            twopt=True
        if 'polyreg' in method:
            polyreg=True
        if 'rollreg' in method:
            rollreg=True

        # Check cell line list
        if not cell_line_list:
            cell_line_list = self.get_cell_line_list()
        print(cell_line_list)

        # Create figure and ax, and the adjust them
        fig, ax = plt.subplots(len(spc_list), 3, figsize=(24, 8*len(spc_list)))
        fig.tight_layout(rect=[0,0,1,0.96])
        plt.subplots_adjust(wspace=0.2, hspace=0.3)

        cl_list = []    # Cell line list to store bioprocess obj
        exp_list = []   # experiment list
        bp_dict = {}    # bioprocess object

        for cell_line, bio_process_dict in self._cell_line_dict.items():
            if cell_line in cell_line_list:
                cl_list.append(cell_line)
                for exp_id, bp in bio_process_dict.items():
                    bp_dict[exp_id] = bp
                    exp_list.append(exp_id)

        hue = 'Cell Line'
        style = 'Experiment ID'

        for i, s in enumerate(spc_list):
            inpro_df_lst = []   # In process list for different experiments
            conc_df_lst = []
            cumulative_lst = []
            sp_rate_df_lst = []
            for exp in exp_list:
                aa = bp_dict[exp].get_spc_dict()[s.upper()]
                inpro_df = aa.get_inpro_df()   # inpro df
                conc_df = aa.get_conc_df()
                cumulative_df = aa.get_cumulative_df()
                sp_rate_df = aa.get_sp_rate_df(twopt, polyreg, rollreg)

                inpro_df_lst.append(inpro_df)
                conc_df_lst.append(conc_df)
                cumulative_lst.append(cumulative_df)
                sp_rate_df_lst.append(sp_rate_df)

            inpro = pd.concat(inpro_df_lst, axis=0, ignore_index=True)
            conc = pd.concat(conc_df_lst, axis=0, ignore_index=True)
            cumulative = pd.concat(cumulative_lst, axis=0, ignore_index=True)
            sp_rate = pd.concat(sp_rate_df_lst, axis=0, ignore_index=True)

            # Conentration
            set_ax = ax[i, 0] if len(spc_list) != 1 else ax[0]
            sns.lineplot(ax=set_ax, data=conc, x='RUN TIME (HOURS)', y=f'CONC.',
                         hue=hue, hue_order=cl_list,
                         style=style,
                         legend=legend,
                         estimator=None)
            set_ax.set_title(f'{s.upper()} Concentration Profile', loc='center')
            set_ax.set_ylabel('Concentration (mM)')
            set_ax.grid(color = 'gray', linestyle = '--', linewidth = 0.5)

            # Cumulative Consumption/Production
            set_ax = ax[i, 1] if len(spc_list) != 1 else ax[1]
            sns.scatterplot(ax=set_ax, data=inpro, x='RUN TIME (HOURS)', y=f'CUM {s.upper()} (mmol)',
                            hue=hue, hue_order=cl_list,
                            style=style,
                            legend=False
                            )
            sns.lineplot(ax=set_ax, data=cumulative, x='RUN TIME (HOURS)', y=f'CUM {s.upper()} (mmol)',
                            hue=hue, hue_order=cl_list,
                            style=style,
                            legend=legend)
            set_ax.set_title(f'{s.upper()} Cumulative Profile', loc='center')
            set_ax.set_ylabel('Cumulative (mmol)')
            set_ax.grid(color = 'gray', linestyle = '--', linewidth = 0.5)

            # Sp. Rate.
            set_ax = ax[i, 2] if len(spc_list) != 1 else ax[2]
            sns.lineplot(ax=set_ax, data=sp_rate, x='RUN TIME (HOURS)', y=f'q{s.upper()} (mmol/109 cell/hr)',
                            hue=hue if (compare_cell_line) else 'Experiment ID',
                            hue_order=cl_list if (compare_cell_line) else exp_list,
                            style=style if (compare_cell_line) else 'Method',
                            estimator=estimator,
                            legend=legend)
            sns.set_theme(style="whitegrid")
            set_ax.set_title(f'{s.upper()} Specific-Rate Profile', loc='center')
            set_ax.set_ylabel('SP. rate (mmol/109 cell/hr)')
            set_ax.grid(color = 'gray', linestyle = '--', linewidth = 0.5)

        if (file_name):
            if '.png' not in file_name:
                file_name += '.png'
            file_path = output_path(file_name=file_name)

            print(f'{file_name} Saving......')
            plt.savefig(file_path)
            print(f'{file_name} Saved')

        return fig



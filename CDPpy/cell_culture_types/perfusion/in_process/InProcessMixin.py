import pandas as pd

from .GetterMixin import GetterMixin

class InProcessMixin(GetterMixin):
    '''
    Mixin class for BioProcess class to do in-processing.
    Methods
    -------

    '''
    def in_process(self):
        '''
        Calculate cumulative consumptions/productions for species.
        '''
        # Species dict
        species = self.get_species()
        species_list = list(species.keys())

        conc_df_list = []
        cumulative_conc_df_list = []

        if 'cell' in species_list:
            species_list.remove('cell')
            cell = species['cell']
            cell.in_process()
            s = cell.cumulative_conc.copy()
            g_r = cell.growth_rate.copy()
            d_r = cell.death_rate.copy()

            s['ID'] = self.cell_line_id
            g_r['ID'] = self.cell_line_id
            d_r['ID'] = self.cell_line_id

            self._cumulative_cell_production = s
            self._cell_growth_rate = g_r
            self._cell_death_rate = d_r

        # Metabolite
        for name in species_list:
            spc = species[name] # Species object
            spc.in_process()
            conc_data = spc.conc.copy()
            conc_data['species'] = name.capitalize()
            conc_df_list.append(conc_data)

            cumulative_data = spc.cumulative_conc.copy()
            cumulative_data['species'] = name.capitalize()
            cumulative_conc_df_list.append(cumulative_data)

            '''sp_rate_data = spc.sp_rate.copy()
            sp_rate_data['species'] = name.capitalize()
            sp_rate_data.append(sp_rate_data)'''
        
        # concat and add "ID"
        conc_df = pd.concat(conc_df_list, axis=0, ignore_index=True)
        cumulative_conc_df = pd.concat(cumulative_conc_df_list, axis=0, ignore_index=True)
        conc_df['ID'] = self.cell_line_id
        cumulative_conc_df['ID'] = self.cell_line_id

        # save
        self._conc_df = conc_df
        self._cumulative_conc_df = cumulative_conc_df
        self._sp_rate = pd.DataFrame()

    @property
    def conc(self):
        return self._conc_df
    
    @property
    def cumulative_conc(self):
        return self._cumulative_conc_df
    
    @cumulative_conc.setter
    def cumulative_conc(self, cumulative_conc_data):
        self._cumulative_conc_df = cumulative_conc_data

    @property
    def cumulative_cell_production(self):
        return self._cumulative_cell_production
    
    @property
    def sp_rate(self):
        return self._sp_rate
    
    @sp_rate.setter
    def sp_rate(self, sp_rate):
        self._sp_rate = sp_rate

    @property
    def growth_rate(self):
        return self._cell_growth_rate
    
    @property
    def death_rate(self):
        return self._cell_death_rate
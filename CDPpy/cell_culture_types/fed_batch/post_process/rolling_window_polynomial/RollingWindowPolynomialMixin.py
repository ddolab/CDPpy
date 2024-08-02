import pandas as pd
import numpy as np

from CDPpy.helper import add_descriptive_column
from CDPpy.constants.fed_batch.column_name import SP_RATE_ROLLING_COLUMN
from CDPpy.constants.constants import RUN_TIME_HOUR_COLUMN, RUN_TIME_DAY_COLUMN, RUN_TIME_DAY_MID_COLUMN, RUN_TIME_HOUR_MID_COLUMN

class RollingWindowPolynomialMixin():
    ''''''
    def rolling_window_polynomial(self, degree=None, window=None):
        '''
        '''
        species = self.get_species('all')
        species_list = list(species.keys())

        # initialize list to store data for plottng
        sp_rate_df_list = []

        # get middle points of run time
        run_time = self.run_time
        t_day = run_time[RUN_TIME_DAY_COLUMN].values
        t_hour = run_time[RUN_TIME_HOUR_COLUMN].values
        t_day_mid = np.zeros((len(t_day)-1))
        t_hour_mid = np.zeros((len(t_hour)-1))

        for i in range(t_day.size-1):
            t_day_mid[i] = 0.5 * (t_day[i] + t_day[i+1])
            t_hour_mid[i] = 0.5 * (t_hour[i] + t_hour[i+1])

        run_time = pd.DataFrame(data={RUN_TIME_DAY_COLUMN: t_day,
                                                RUN_TIME_HOUR_COLUMN: t_hour})
        
        if window == None:
            window = round(t_day.size/3.0)
            if window < 6:
                window = 6
        if degree == None:
            degree = 3

        # initialize df for logging
        sp_rate_dataframe = run_time.copy()


        # Product/IgG and Metabolite
        for name in species_list:
            spc = species[name]
            spc_name = name.capitalize() if name != "IgG" else name

            # calculate sp. rate.
            spc.rolling_window_polynomial(degree=degree, windows=window)

            sp_rate_data = spc.sp_rate_rolling.copy()
            sp_rate_data['species'] = spc_name
            sp_rate_df_list.append(sp_rate_data)

            sp_rate_dataframe[f"{spc_name} {sp_rate_data['unit'].iat[0]}"] = sp_rate_data['value']
        
        # concat sp. rate for rolling polynomial
        sp_rate_rolling_df = pd.concat(sp_rate_df_list, axis=0, ignore_index=True)
        # stored sp. rate
        sp_rate = self.sp_rate

        # concat 
        sp_rate_data = pd.concat([sp_rate, sp_rate_rolling_df], axis=0, ignore_index=True)
        sp_rate_data['ID'] = self.cell_line_id
        
        # save
        self.sp_rate = sp_rate_data
        self._sp_rate_data_rolling = sp_rate_dataframe

        # concat all processd data
        processed_data = self._processed_data
        sp_rate = add_descriptive_column(sp_rate_dataframe, SP_RATE_ROLLING_COLUMN)
        self._processed_data = pd.concat([processed_data, sp_rate], axis=1)


    def get_sp_rate_rolling(self):
        return self._sp_rate_data_rolling
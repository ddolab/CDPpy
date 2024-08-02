import numpy as np
import pandas as pd

from CDPpy.Species.Perfusion.Variables import molar_mass_dict
from CDPpy.constants import RUN_TIME_DAY_COLUMN, RUN_TIME_HOUR_COLUMN

from .mid_point_calc import mid_point_conc

class MetaboliteMixin:
    '''
    '''
    def rolling_window_polynomial(self, degree, windows):
        '''
        '''
        s = self.cumulative_conc['value'].values
        c = self.conc['value'].values
        t_day = self.run_time_day
        t_hour = self.run_time_hour
        vcc = self.viable_cell_conc['value'].values
        conc_unit = self.conc['unit'].iat[0]
        unit = self.cumulative_conc['unit'].iat[0]
        state = self.cumulative_conc['state'].iat[0]

        t_day_mid, t_hour_mid, c_mid = mid_point_conc(t_day, t_hour, c)

        q = np.zeros(len(t_hour)-1)
        q.fill(np.nan)

        # Calculate SP. rate
        x = t_hour
        x_mid = t_hour_mid
        y = s
        for i in range(0, len(x_mid)):
            if (i + 1) < (windows / 2):
                x_roll = x[0: windows]
                y_roll = y[0: windows]
                # Polynomial Regression for Cumulative Consumption/Production
                fit = np.polyfit(x_roll, y_roll, degree)  # Fitting data to polynomial Regression (Get slopes)
                p = np.poly1d(fit)  # Get polynomial curve for Cumulative Consumption/Production

                dp1 = p.deriv()      # first derivetive of polynomial fit

                dy = dp1(x_mid[i])      # derivetive values corresponding to x
                
                q[i] = dy / vcc[i]

            elif (i + windows / 2) > len(x):
                x_roll = x[int(len(x)-windows/2-1):len(x)]
                y_roll = y[int(len(x)-windows/2-1):len(x)]
                # Polynomial Regression for Cumulative Consumption/Production
                fit = np.polyfit(x_roll, y_roll, degree)  # Fitting data to polynomial Regression (Get slopes)
                p = np.poly1d(fit)  # Get polynomial curve for Cumulative Consumption/Production

                dp1 = p.deriv()      # first derivetive of polynomial fit

                dy = dp1(x_mid[i])      # derivetive values corresponding to x
                
                q[i] = dy / vcc[i]
                
            else:
                x_roll = x[int(i-windows/2+1):int(i+windows/2+1)]
                y_roll = y[int(i-windows/2+1):int(i+windows/2+1)]
                # Polynomial Regression for Cumulative Consumption/Production
                fit = np.polyfit(x_roll, y_roll, degree)  # Fitting data to polynomial Regression (Get slopes)
                p = np.poly1d(fit)  # Get polynomial curve for Cumulative Consumption/Production

                dp1 = p.deriv()      # first derivetive of polynomial fit

                dy = dp1(x_mid[i])      # derivetive values corresponding to x
                
                q[i] = dy / vcc[i]

        if unit==('(mg/ml)'): # Match the unit
            molar_mass = molar_mass_dict[self._name.capitalize()]
            q = q / molar_mass * 1000
        
        #Concentration middle points.
        conc_mid = pd.DataFrame(data={'Run Time Mid (day)': t_day_mid,
                                      'Run Time Mid (hr)': t_hour_mid,
                                      'value': c_mid})
        conc_mid['unit'] = conc_unit

        # Sp. rate by rolling window polynomial
        r_roll_poly = pd.DataFrame(data={RUN_TIME_DAY_COLUMN: t_day_mid,
                                         RUN_TIME_HOUR_COLUMN: t_hour_mid,
                                         'value': q})
        
        r_roll_poly['unit'] = '(mmol/10^9_cells/hr)'
        r_roll_poly['method'] = 'rollingWindowPolynomial'
        r_roll_poly['degree'] = degree
        r_roll_poly['window'] = windows

        # store values
        self._roll_polyorder = degree
        self._roll_polywindow = windows
        self._conc_mid = conc_mid
        self._sp_rate_rolling = r_roll_poly

    @property
    def conc_mid(self):
        ''''''
        return self._conc_mid
    
    @property
    def sp_rate_rolling(self):
        ''''''
        return self._sp_rate_rolling
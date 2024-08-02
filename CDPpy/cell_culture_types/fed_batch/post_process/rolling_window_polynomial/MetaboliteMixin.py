import pandas as pd
import numpy as np
from CDPpy.constants import MetaboliteNameSpace
from CDPpy.constants import RUN_TIME_DAY_COLUMN, RUN_TIME_HOUR_COLUMN

from .GetterMixin import GetterMixin

CONSTANTS = MetaboliteNameSpace()

class MetaboliteMixin(GetterMixin):
    '''Rolling window polynomial regression Mixin Class for metabolites.
    '''
    def rolling_window_polynomial(self, degree, windows):
        '''Calculate Specific Rate from Derivetive of Polynomial Regression on Cumularive Consumption/Production.
        '''
        idx = self.measurement_index
        x = self.run_time_hour[idx]
        x_day = self.run_time_day[idx]
        v = self.volume_before_sampling[idx]
        y = self.cumulative_conc['value'].values[idx]
        vcc = self.viable_cell_conc['value'].values[idx]
        
        q = np.zeros(len(x))
        q.fill(np.nan)

        # Calculate SP. rate
        for i in range(0, len(x)):
            if (i + 1) < (windows / 2):
                x_roll = x[0: windows]
                y_roll = y[0: windows]
                # Polynomial Regression for Cumulative Consumption/Production
                fit = np.polyfit(x_roll, y_roll, degree)  # Fitting data to polynomial Regression (Get slopes)
                p = np.poly1d(fit)  # Get polynomial curve for Cumulative Consumption/Production

                dp1 = p.deriv()      # first derivetive of polynomial fit

                dy = dp1(x[i])      # derivetive values corresponding to x
                if(self._measured_cumulative_flag):
                    q[i] = dy / vcc[i]
                else:
                    q[i] = dy / (vcc[i] * v[i]) * 1000

            elif (i + windows / 2) > len(x):
                x_roll = x[int(len(x)-windows):len(x)]
                y_roll = y[int(len(x)-windows):len(x)]
                # Polynomial Regression for Cumulative Consumption/Production
                fit = np.polyfit(x_roll, y_roll, degree)  # Fitting data to polynomial Regression (Get slopes)
                p = np.poly1d(fit)  # Get polynomial curve for Cumulative Consumption/Production

                dp1 = p.deriv()      # first derivetive of polynomial fit

                dy = dp1(x[i])      # derivetive values corresponding to x
                if(self._measured_cumulative_flag):
                    q[i] = dy / vcc[i]* 2
                else:
                    q[i] = dy / (vcc[i] * v[i]) * 1000
                
            else:
                x_roll = x[int(i-windows/2+1):int(i+windows/2+1)]
                y_roll = y[int(i-windows/2+1):int(i+windows/2+1)]
                # Polynomial Regression for Cumulative Consumption/Production
                fit = np.polyfit(x_roll, y_roll, degree)  # Fitting data to polynomial Regression (Get slopes)
                p = np.poly1d(fit)  # Get polynomial curve for Cumulative Consumption/Production

                dp1 = p.deriv()      # first derivetive of polynomial fit

                dy = dp1(x[i])      # derivetive values corresponding to x
                if(self._measured_cumulative_flag):
                    q[i] = dy / vcc[i] * 2
                else:
                    q[i] = dy / (vcc[i] * v[i] )* 1000



        # Sp. rate by rolling window polynomial
        r_roll_poly = pd.DataFrame(data={RUN_TIME_DAY_COLUMN: x_day,
                                         RUN_TIME_HOUR_COLUMN: x,
                                         'value': q})
        r_roll_poly['unit'] = CONSTANTS.SP_RATE_UNIT
        r_roll_poly['method'] = 'rollingWindowPolynomial'
        r_roll_poly['degree'] = degree
        r_roll_poly['window'] = windows

        # store values
        self._roll_polyorder = degree
        self._roll_polywindow = windows
        self._sp_rate_rolling = r_roll_poly
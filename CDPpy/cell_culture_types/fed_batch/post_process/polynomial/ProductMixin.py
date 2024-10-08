import numpy as np
import pandas as pd

from CDPpy.constants import RUN_TIME_DAY_COLUMN, RUN_TIME_HOUR_COLUMN
from CDPpy.constants import ProductNameSpace
from .GetterMixin import GetterMixin

Constants = ProductNameSpace()

class ProductMixin(GetterMixin):
    '''Product/IgG Mixin Class for polynomial regression.
    Methods
    -------
        polynomial
    '''
    def polynomial(self, deg, data_num=100):
        '''Calculate the cumulative concentration and specific rate of produc/IgG using polynomial regression.
        Parameters
        ----------
            deg : int
                a polynomial degree for polynomial regression.
        '''
        idx = self.measurement_index
        t = self.run_time_hour
        s = self.cumulative_conc['value'].values
        xv = self.viable_cell_conc['value'].values #[idx]
        v = self.volume_before_sampling #[idx]
        unit = self.cumulative_conc['unit'].iat[0]
        state = self.cumulative_conc['state'].iat[0]
        # Get run time dataframe
        run_time = self.run_time

        # Fitting a polynomial
        poly_func = np.poly1d(np.polyfit(x=t[idx], y=s[idx].astype('float'), deg=deg))

        # Calculate cumulative concentration from the polynomial function
        t_poly = np.linspace(t[0], t[-1], data_num)
        # day_poly = np.floor(t_poly / 24).astype(int)
        day_poly = t_poly / 24.0
        run_time_poly = pd.DataFrame(data={RUN_TIME_DAY_COLUMN: day_poly,
                                           RUN_TIME_HOUR_COLUMN: t_poly})
        # use run time for polynomial plotting
        s_poly = poly_func(t_poly)
        s_poly = pd.DataFrame(data=s_poly, columns=['value'])
        s_poly['unit'] = unit
        s_poly['state'] = state
        s_poly['method'] = 'polynomial'
        s_poly['degree'] = deg
        s_poly.index.name = 'Cumulative concentration'

        # Get the derivetive of the polynomial, and evaluate the derivetive at the run time.
        poly_deriv = poly_func.deriv()
        y = poly_deriv(t) # use run time in measured data

        # Calculate the specific rate from the derivetive of the polynomial function
        r_poly = y / (xv * v) * 1000
        # r_poly[0] = np.nan
        r_poly = pd.DataFrame(data=r_poly, columns=['value'])
        r_poly['unit'] = Constants.SP_RATE_UNIT
        r_poly['method'] = 'polynomial'
        r_poly['degree'] = deg
        r_poly.index.name = Constants.SP_RATE

        # Store the variables
        self._poly_degree = deg
        self._poly_func = poly_func
        self._cumulative_poly = pd.concat([run_time_poly, s_poly], axis=1)
        # self._cumulative_poly = pd.concat([run_time, s_poly], axis=1)
        self._sp_rate_poly = pd.concat([run_time, r_poly], axis=1)
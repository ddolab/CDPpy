import numpy as np
import pandas as pd

from CDPpy.Species.Perfusion.Variables import molar_mass_dict
from CDPpy.constants import RUN_TIME_DAY_COLUMN, RUN_TIME_HOUR_COLUMN

class MetaboliteMixin:
    '''Metabolite Mixin Class for polynomial regression.
    Methods
    -------
        polynomial
    '''
    def polynomial(self, deg, data_num=50):
        '''Calculate the cumulative concentration and specific rate of a metabolite using polynomial regression.
        Parameters
        ----------
            deg : int
                a polynomial degree for polynomial regression.
        '''
        global molar_mass_dict

        s = self.cumulative_conc['value'].values
        t = self.run_time_hour
        xv = self.viable_cell_conc['value'].values
        unit = self.cumulative_conc['unit'].iat[0]
        state = self.cumulative_conc['state'].iat[0]

        # Get run time dataframe
        run_time = self.run_time

        # Fitting a polynomial
        poly_func = polyfit(t, s, deg)

        # Calculate cumulative concentration from the polynomial function
        t_poly = np.linspace(t[0], t[-1], data_num)
        # day_poly = np.floor(t_poly / 24).astype(int)
        day_poly = t_poly / 24.0
        run_time_poly = pd.DataFrame(data={RUN_TIME_DAY_COLUMN: day_poly,
                                           RUN_TIME_HOUR_COLUMN: t_poly})

        # Calculate cumulative concentration from the polynomial function
        s_poly = poly_func(t_poly)
        s_poly = pd.DataFrame(data=s_poly, columns=['value'])
        s_poly['unit'] = unit
        s_poly['state'] = state
        s_poly['method'] = 'polynomial'
        s_poly['degree'] = deg
        s_poly.index.name = 'Cumulative concentration'

        # Get the derivetive of the polynomial, and evaluate the derivetive at the run time.
        poly_deriv = poly_func.deriv()
        y = poly_deriv(t)

        # Calculate the specific rate from the derivetive of the polynomial function
        r_poly = y / xv
        if unit==('(mg/ml)'): # Match the unit
            molar_mass = molar_mass_dict[self._name.capitalize()]
            r_poly = r_poly / molar_mass * 1000
        r_poly = pd.DataFrame(data=r_poly, columns=['value'])
        r_poly['unit'] = '(mmol/10^9_cells/hr)'
        r_poly['method'] = 'polynomial'
        r_poly['degree'] = deg
        r_poly.index.name = 'Specific rate'

        # Store the variables
        self._poly_degree = deg
        self._poly_func = poly_func
        self._cumulative_conc_poly = pd.concat([run_time_poly, s_poly], axis=1)
        self._sp_rate_poly = pd.concat([run_time, r_poly], axis=1)

    @property
    def cumulative_conc_poly(self):
        ''''''
        return self._cumulative_conc_poly
    
    @property
    def sp_rate_poly(self):
        ''''''
        return self._sp_rate_poly
    

def polyfit(t, s, deg):
    '''Fitting a polynomial of the degree to the cumulative concentration data.
    Parameters
    ----------
        t : numpy array
            Run time (hr).
        s : numpy array
            Cumulative concentration (mg/mL) or (mmol/L).
        deg : int
            a polynomial degree for polynomial regression.
    Returns
    -------
        np.poly1d()
            a polynomial function that fit to the cumulative concentration data.
    '''
    return np.poly1d(np.polyfit(x=t, y=s, deg=deg))


        
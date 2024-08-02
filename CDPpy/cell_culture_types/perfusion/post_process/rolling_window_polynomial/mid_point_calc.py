import numpy as np

def mid_point_conc(t_day, t_hour, c):
    '''Calculate mid points of the run time and concentration.
    Attributes
    ----------
        t_day: array
            array of run time (day).
        t_hour: array
            array of run time (hr).
        c: array
            concentration (mM).
    '''
    c_mid = np.zeros((len(t_hour)-1))
    t_day_mid = np.zeros((len(t_day)-1))
    t_hour_mid = np.zeros((len(t_hour)-1))

    for i in range(len(t_hour)-1):
        c_mid[i] = 0.5 * (c[i] + c[i+1])
        t_day_mid[i] = 0.5 * (t_day[i] + t_day[i+1])
        t_hour_mid[i] = 0.5 * (t_hour[i] + t_hour[i+1])

    return t_day_mid, t_hour_mid, c_mid
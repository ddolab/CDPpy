'''
Integral Viable Cell Concentration Equation:
S(t) = S(t-1) + {C(t) + C(t-1)} / 2 * {T(t) - T(t-1)}
S: Integral Viable Cell Concentration
C: Viable Cell Concentration
T: Time
'''
def integral_viable_cell(C1, C2, T1, T2) -> float:
    '''Calculate integral of viable cell concentration at t (10^6 cells hr/mL).

    Parameters
    ---------
        C1 : float
            Viable Cell Concentration at t-1 (10^6 cells/mL).
        C2 : float
            Viable Cell Concentration at t (10^6 cells/mL).
        T1 : float
            Time at t-1 (hr).
        T2 : float
            Time at t (hr).
    Returns
    -------
        float
            Integral of viable cell concentration at t (10^6 cells hr/mL).
    '''
    return 0.5 * (C1 + C2) * (T2 - T1)

'''
Production of the Cell Equation:
S(t) = C(t-1) * V1 - C(t-1) * V2
S: Production of the cell
C: Viable Cell Concentration
V1: Culture volume Before Sampling
V2: Culture volume After Sampling
'''
def cell_production(C1, C2, V1, V2) -> float:
    '''Calculate production of the cell at t (10^6 cells).

    Parameters
    ---------
        C1 : float
            Viable Cell Concentration at t-1 (10^6 cells/mL).
        C2 : float
            Viable Cell Concentration at t (10^6 cells/mL).
        V1 : float
            Culture volume Before Sampling at t (mL).
        V2 : float
            Culture volume After Sampling at t-1 (mL).
    Returns
    -------
        float
            production of the cell at t (10^6 cells).
    '''
    return C2 * V1 - C1 * V2

'''
Specific Growth Rate Equation
ds/dt(t) = {S(t) - S(t-1)} / [{} / 2 * {T(t) - T(t-1)}]
'''
def growth_rate(s1, s2, xv1, xv2, v1, v2, t1, t2):
    '''
    '''
    return (s2 - s1) / (0.5 * (xv1 * v2 + xv2 * v1) * (t2 - t1))
'''
x = s[i] - s[i-1]
y = xv[i] * v1[i] + xv[i-1] * v2[i-1]
r[i] = x / (y * 0.5 * (t[i] - t[i-1]))
'''
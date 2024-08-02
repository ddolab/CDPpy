'''
Production Equation:
S(t) = C(t) - C(t-1) + D * {T(t) - T(t-1)} * [{C(t) + C(t-1)} / 2 - F(t)]
S: Production
C: Concentration
T: Time
F: Feed Concentration
'''
def production(C1, C2, T1, T2, D, F) -> float:
    '''Calculate production of a metabolite.
    Parameters
    ---------
        C1 : float
            Concentration at t-1 (mg/mL) or (mmol/L).
        C2 : float
            Concentration at t (mg/mL) or (mmol/L).
        T1 : float
            Time at t-1 (hr).
        T2 : float
            Time at t (hr).
        D : float
            Dillution rate at t (hr^1).
            Flow rate (L/hr) / Culture volume (L)
        F : float
            Feed concentration at t (mg/mL) or (mmol/L).
    Returns
    -------
        float
            Production of a metabolite (mg/mL) or (mmol/L).
    '''
    return C2 - C1 + D * (T2 - T1) * (0.5 * (C1 + C2) - F)


'''
Death Rate Equation:
dXD/dt(t) = [{XD(t)-XD(t-1)} / {T(t)-T(t-1)} + (1+a-a*c) * {D(t)+D(t-1)}/2 * {XD(t)+XD(t-1)}/2] / [{XV(t)+XV(t-1)}/2]
a: Recycling factor
c: concentration factor
T: Time
XD: Dead cell concentration
XV: Viable cell concentration
D: Dillution rate
'''
def death_rate(b, xd1, xd2, xv1, xv2, t1, t2, d1, d2) -> float:
    '''Calculate the death rate of the cell.
    Parameters
    ---------
        b : float
            bleeding ratio
        xd1 : float
            Dead cell concentration at t-1 (10^6 cells/ml).
        xd2 : float
            Dead cell concentration at t (10^6 cells/ml).
        xv1 : float
            Viable cell concentration at t-1 (10^6 cells/ml).
        xv2 : float
            Viable cell concentration at t (10^6 cells/ml).
        t1 : float
            Time at t-1 (hr).
        t2 : float
            Time at t (hr).
        d1 : float
            Dillution rate at t-1 (hr^-1).
        d2 : float
            Dillution rate at t (hr^-1).
    Returns
    -------
        float
            Death rate of the cell (hr^-1).
    '''
    return ((xd2-xd1)/(t2-t1)+(1-b)*(d2+d1)*0.5*(xd2+xd1)*0.5)/((xv2+xv1)*0.5)


'''
Growth Rate Equation:
ds/dt(t) = [{XV(t)-XV(t-1)} / {T(t)-T(t-1)} / {XV(t)+XV(t-1)}/2 + (1+a-a*c) * {D(t)+D(t-1)}/2] / dXD/dt
a: Recycling factor
c: concentration factor
T: Time
XV: Viable cell concentration
D: Dillution rate
dXD/dt: Death rate
'''
def growth_rate(b, xv1, xv2, t1, t2, d1, d2, dr) -> float:
    '''Calculate the death rate of the cell.
    Parameters
    ---------
        b : float
            bleeding ratio
        xv1 : float
            Viable cell concentration at t-1 (10^6 cells/ml).
        xv2 : float
            Viable cell concentration at t (10^6 cells/ml).
        t1 : float
            Time at t-1 (hr).
        t2 : float
            Time at t (hr).
        d1 : float
            Dillution rate at t-1 (hr^-1).
        d2 : float
            Dillution rate at t (hr^-1).
        dr: Death rate at t (hr^-1).
    Returns
    -------
        float
            Growth rate of the cell (hr^-1).
    '''
    return ((xv2-xv1)/(t2-t1)/((xv2+xv1)*0.5)+(1-b)*(d2+d1)*0.5)+dr

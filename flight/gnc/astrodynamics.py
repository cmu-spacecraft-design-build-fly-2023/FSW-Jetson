import numpy as np
import brahe


R_EARTH = 6.378e6

def get_CART_from_OSC(x_oe, degrees=False):
    """
    Return the cartesian state (position and velocity, ECI) given the corresponding set of osculating orbital elements.
    The vector must contain in order (SatelliteDynamics.jl):
        1. a, Semi-major axis [m]
        2. e, Eccentricity [dimensionless]
        3. i, Inclination [rad]
        4. Ω, Right Ascension of the Ascending Node (RAAN) [rad]
        5. ω, Argument of Perigee [rad]
        6. M, Mean anomaly [rad]
    """
    return np.array(brahe.sOSCtoCART(x_oe, use_degrees=degrees))


def get_OSC_from_CART(x_oe, degrees=False):
    """
    Return the set of osculating orbital elements given the cartesian state (position and velocity, ECI).
    The input vector must be in the following form: [x, y, z, xdot, ydot, zdot]
    The resulting vector will be in order (SatelliteDynamics.jl):
        1. _a_, Semi-major axis [m]
        2. _e_, Eccentricity [dimensionless]
        3. _i_, Inclination [rad]
        4. _Ω_, Right Ascension of the Ascending Node (RAAN) [rad]
        5. _ω_, Argument of Perigee [ramd]
        6. _M_, Mean anomaly [rad]
    """
    return np.array(brahe.sCARTtoOSC(x_oe, use_degrees=degrees))
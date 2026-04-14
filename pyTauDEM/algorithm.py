import numpy as np


def calculate_tarboton_slope(e0, adj, res):
    """
    Standard Tarboton (1997) D-Infinity Slope Calculation.
    adj order: E, SE, S, SW, W, NW, N, NE (indices 0 to 7)
    Tarboton, D. G. (1997). 
    A new method for the determination of flow directions and upslope areas in grid digital elevation models. 
    Water resources research, 33(2), 309-319.
    """
    import numpy as np
    max_slope = 0.0
    
    # Define the 8 facet combinations (each facet is formed by the center point e0 and two neighbors)
    # Each facet consists of one orthogonal neighbor (e1) and one diagonal neighbor (e2)
    # For example, the first facet is formed by the center, East (E), and Southeast (SE)
    # The order of neighbors in adj is: E(0), SE(1), S(2), SW(3), W(4), NW(5), N(6), NE(7)
    facets = [
        (0, 1), (2, 1), (2, 3), (4, 3), 
        (4, 5), (6, 5), (6, 7), (0, 7)
    ]

    for i1, i2 in facets:
        e1 = adj[i1] # The direction of the orthogonal neighbor (E, S, W, N)
        e2 = adj[i2] # The direction of the diagonal neighbor (SE, SW, NW, NE)

        s1 = (e0 - e1) / res
        s2 = (e1 - e2) / res 
        
        # Calculating the magnitude of the slope (r) using the two components s1 and s2
        r = np.sqrt(s1**2 + s2**2)
        
        # Calculate the direction theta (0 points towards e1, atan(s2/s1) is the angle towards e2)
        if s1 != 0:
            theta = np.arctan2(s2, s1)
        else:
            theta = np.pi / 2 if s2 > 0 else -np.pi / 2

        # Checking if the gradient direction is within the facet defined by e0, e1, and e2
        if theta < 0:
            # Gradient direction is outside the facet towards e1, so the maximum slope is along e1
            slope = max(0, (e0 - e1) / res)
        elif theta > np.arctan(1.0):
            # Gradient direction is outside the facet towards e2, so the maximum slope is along e2
            slope = max(0, (e0 - e2) / (res * np.sqrt(2)))
        else:
            # Gradient direction is within the facet, so we use the calculated r as the slope
            slope = r
            
        max_slope = max(max_slope, slope)
        
    return float(max_slope)
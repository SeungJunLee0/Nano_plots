import numpy as np

# Define a function to compute invariant mass
def invariant_mass(p1, p2, p3):
    E = p1[0] + p2[0] + p3[0]
    px = p1[1] + p2[1] + p3[1]
    py = p1[2] + p2[2] + p3[2]
    pz = p1[3] + p2[3] + p3[3]
    return np.sqrt(E**2 - px**2 - py**2 - pz**2)

# Define b, lepton, neutrino 4-momentum: (E, px, py, pz)

# Top decay 1
b1     = (115.9430585, -10.95482953, 52.84902277, -102.50695258)
lep1   = (263.2889827, -95.06060696, -105.5310934, -221.6929357)
nu1    = (32.90597826, 5.370971948, 10.03783829, -30.8739027)

# Top decay 2
b2     = (215.86402795, 30.83443073, 12.27684755, -213.24564582)
lep2   = (62.27668291, 60.02151593, -10.2750395, -13.04708485)
nu2    = (63.31351261, 9.788517874, 40.64242428, -47.54975441)

# Compute invariant masses
m_blnu_1 = invariant_mass(b1, lep1, nu1)
m_blnu_2 = invariant_mass(b2, lep2, nu2)

m_blnu_1, m_blnu_2
print("1", m_blnu_1) #1 178.4166787290046
print("2", m_blnu_2) #2 172.20174592134674


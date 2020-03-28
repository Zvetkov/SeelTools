class dMass(object):
    def __init__(self):
        self.SetZero()

    def SetZero(self):
        self.mass = 0.0
        self.m = 0.0
        self.i = []

    def Add(first_mass, second_mass):
        var = 1.0 / (first_mass.mass + second_mass.mass)
        for i in [0, 1, 2]:
            first_mass.c[i] = (first_mass.c[i] * first_mass.mass + second_mass.c[i] * second_mass.mass) * var
        for i in [0, 1, 2]:
            for j in [0, 1, 2]:
                first_mass.i[j] += second_mass.i[j]


def MassSetBoxTotal(m: dMass, a2: int, total_mass: float, lx: float, ly: float, lz: float):
    m.mass = 0.0
    m.SetZero()
    m.i.append((lz**2 + ly**2) * total_mass) * 0.083333336  # =1/12 ???
    m.i.append((lx**2 + lz**2) * total_mass) * 0.083333336
    m.i.append((lx**2 + ly**2) * total_mass) * 0.083333336

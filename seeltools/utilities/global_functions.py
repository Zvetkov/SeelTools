from seeltools.utilities.constants import ACTION_TYPE


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


def GetActionByName(actionName):
    action_id = ACTION_TYPE.get(actionName)
    if action_id is not None:
        return action_id
    else:
        return 0


def GetActionByNum(num):
    actionName = list(ACTION_TYPE.keys())[list(ACTION_TYPE.values()).index(num)]
    if actionName is not None:
        return actionName
    else:
        return ""


class AIParam(object):
    def __init__(self):
        self.id = 0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.w = 0.0
        self.NameFromNum - 0
        self.NumFromName = 0

    def SetAIParamValue(self, string):
        self.Detach()
        self.id = string
        self.Type = 5

    def Detach(self):
        self.id = 0
        self.Type = 0
        self.NameFromNum = 0
        self.NumFromName = 0
        # self.x = 0.0  # ??? why this is missing?
        self.y = 0.0
        self.z = 0.0
        self.w = 0.0

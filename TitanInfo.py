import copy
from Parts import Parts

class TitanInfo:

    def __init__(self, Name, ID, TotalHP):
        self.Name = Name
        self.ID = ID
        self.TotalHP = TotalHP
        self.parts = []

        self.Head = Parts()
        self.ChestUpper = Parts()
        self.ArmUpperRight = Parts()
        self.ArmUpperLeft = Parts()
        self.LegUpperRight = Parts()
        self.LegUpperLeft = Parts()
        self.HandRight = Parts()
        self.HandLeft = Parts()

        self.parts.append(self.Head)
        self.parts.append(self.ChestUpper)
        self.parts.append(self.ArmUpperRight)
        self.parts.append(self.ArmUpperLeft)
        self.parts.append(self.LegUpperRight)
        self.parts.append(self.LegUpperLeft)
        self.parts.append(self.HandRight)
        self.parts.append(self.HandLeft)

    def getID(self):
        return self.ID
    def setPartHP(self, id, hp):
        Target = ''
        if 'Body' in id:
            id = id.replace('Body', '')
            Target = 'Body'
        elif 'Armor' in id:
            id = id.replace('Armor', '')
            Target = 'Armor'
        func = 'self.%s.set%sHP(hp)' % (id, Target)
        eval(func)

    def setState(self, id, state):
        func = 'self.%s.setState(state)' % (id)
        eval(func)

    def setTotalHP(self, TotalHP):
        self.TotalHP = TotalHP

    def getTotalHP(self):
        TotalArmorHP = 0.0
        for part in self.parts:
            if part.getState() != '1':
                TotalArmorHP += part.getArmorHP()
        return TotalArmorHP + self.TotalHP
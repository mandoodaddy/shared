
class Parts:
    Armor = 0.0
    Body = 0.0
    state = ''

    def __init__(self):
        return

    def setState(self, state):
        self.state = state

    def getState(self):
        return self.state

    def setArmorHP(self, Armor):
        self.Armor = Armor

    def getArmorHP(self):
        return self.Armor

    def setBodyHP(self, Body):
        self.Body = Body

    def getBodyHP(self):
        return self.Body

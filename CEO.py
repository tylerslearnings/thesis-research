

class CEO:
    name = ''
    yearStart = 0
    yearEnd = 0

    def __init__(self):
        self.name = ''

    def getYearStart(self):
        return self.yearStart

    def setYearStart(self, yearStart):
        self.yearStart = yearStart

    def getYearEnd(self):
        return self.yearEnd

    def setYearEnd(self, yearEnd):
        self.yearEnd = yearEnd

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name
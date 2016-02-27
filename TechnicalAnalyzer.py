# possible Tokens of interest
class Token:
    name = ''
    terms = []

    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name

    def getTerms(self):
        return self.terms

    def addTerms(self, terms):
        self.terms = terms

    def hasTerm(self, term):
        for word in self.terms:
            if term == word:
                return True

        return False


class TechnicalAnalyzer:
    dictionary = []

    def __init__(self):
        self.createTokens()
        self.createTerms()

    def createTokens(self):
        self.dictionary.append(Token('revenue'))
        self.dictionary.append(Token('profit'))
        self.dictionary.append(Token('loss'))

    def createTerms(self):
        revenueTerms = ['revenue', 'net sales', 'total revenues']
        profitTerms = ['net income', 'profit']
        lossTerms = ['net loss', 'loss', 'net (loss) income']

        self.dictionary[0].addTerms(revenueTerms)
        self.dictionary[1].addTerms(profitTerms)
        self.dictionary[2].addTerms(lossTerms)

    def AnalyzeTerm(self, term):

        for token in self.dictionary:
            if token.hasTerm(term):
                return token.getName()

        return "nil"

    def getDictionary(self):
        return self.dictionary

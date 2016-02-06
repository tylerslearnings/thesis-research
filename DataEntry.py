# Name: Data Entry Class
# Description: This class will act as a single entry to our data set

from DateRange import DateRange

class DataEntry:

    stockSymbol     = ""
    dateRange       = DateRange()
    prodScore       = 0.0
    manageScore     = 0.0
    companyScore    = 0.0
    revenueGrowth   = 0.0
    profitGrowth    = 0.0
    peGrowth        = 0.0
    stockGrowth     = 0.0
    dividendGrowth  = 0.0
    marketGrowth    = 0.0
    yearGrowth      = 0.0

    def __init__(self, sSymbol, dRange, pScore, mScore, cScore, rGrowth, pGrowth, peGrowth, sGrowth, dGrowth, mGrowth, yGrowth):
        self.stockSymbol = sSymbol
        self.dateRange = dRange
        self.prodScore = pScore
        self.manageScore = mScore
        self.companyScore = cScore
        self.revenueGrowth = rGrowth
        self.profitGrowth = pGrowth
        self.peGrowth = peGrowth
        self.stockGrowth = sGrowth
        self.dividendGrowth = dGrowth
        self.marketGrowth = mGrowth
        self.yearGrowth = yGrowth

    




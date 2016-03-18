#Name: Quantitative Analyzer Class
#Description: This class will analyze a stock's quantitative aspects and return a list of data entries

from bs4 import BeautifulSoup
from yahoo_finance import Share
from TechnicalAnalyzer import TechnicalAnalyzer
import urllib2
import datetime
import csv
import ystockquote
from pprint import pprint


REVENUE = 'revenue'
PROFIT = 'profit'
LOSS = 'loss'
def PerformAnalysis(companyName):
    #Generate Query
    url = GenerateQuery(companyName)
    rowList, associatedDates = ExtractTablesAndRows(url)

    urlList = ExtractURLList(rowList)
    incomePageUrlList = Extract10List(urlList)

    revenueList = ExtractRevenueList(companyName, incomePageUrlList)
    profitList = ExtractProfitList(companyName, incomePageUrlList)

    stockGrowth, dividenGrowth, marketGrowth, yearGrowth = GetStockFundamentels(associatedDates, companyName)


    return associatedDates, revenueList, profitList, stockGrowth, dividenGrowth, marketGrowth, yearGrowth





def GenerateQuery(companyName):
    #get CIK
    cik = ""

    with open("cik.coleft.c.txt") as cikDiction:
        for line in cikDiction:
            stringArray = line.split(":")
            cName = stringArray[0].lower()
            if cName == companyName:
                cik = stringArray[1]
                break

    if(cik == ""):
        print "Company Does not Exist in SEC Records"
    url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="+cik+"&owner=exclude&count=40&hidefilings=0"
    return url

def ExtractTablesAndRows(url):
    MINYEAR = 2007
    rows = []
    dateStore = []
    date = datetime.datetime.strptime('26 Mar 2015', '%d %b %Y')
    stopDate = datetime.datetime.strptime('26 Mar 2015', '%d %b %Y')
    currentUrl = url
    i = 1
    while date.year > MINYEAR:
        htmlText = urllib2.urlopen(currentUrl).read()
        soup = BeautifulSoup(htmlText, "html.parser")
        table = soup.find_all("table", {"class" : "tableFile2"})[0]

        tableRows = table.find_all("tr")

        for row in tableRows:
            sRow = BeautifulSoup(str(row), "html.parser")
            if len(sRow.find_all("td")) != 0:

                checkYear = datetime.datetime.strptime(sRow.find_all("td")[3].getText()[:10], "%Y-%m-%d")
                if sRow.find_all("td")[0].getText() == "10-Q" and (checkYear <= stopDate):
                    rows.append(row)
                    dateStore.append(checkYear)

        #check first date
        rSoup = BeautifulSoup(str(table), "html.parser")
        rowCheck = rSoup.find_all("tr")[1]
        dateCheck = BeautifulSoup(str(rowCheck), "html.parser").find_all("td")[3].getText()
        newDate = datetime.datetime.strptime(dateCheck, "%Y-%m-%d")
        date = newDate
        count = 40*i
        currentUrl = url + "&start=" + str(count)
        i += 1

    i = 0
    for date in dateStore:
        if date.year > MINYEAR:
            i += 1
        else:
            break

    newStore = dateStore[0:i]
    newRows = rows[0:i]
    return newRows, newStore

def ExtractURLList(rowList):
    baseURL = "http://www.sec.gov"
    urlList = []
    for i in range(0, len(rowList)):
        row = rowList[i]
        allLinks = row.find_all("a")
        a = allLinks[0]
        urlList.append(baseURL + a['href'])

    return urlList

def Extract10List(urlList):
    baseURL = "http://www.sec.gov"
    TenQPage = []
    for theUrl in urlList:
        htmlText = urllib2.urlopen(theUrl).read()
        soup = BeautifulSoup(htmlText, "html.parser")
        tableRows = soup.find_all("tr")
        for row in tableRows:
            cellList = row.find_all("td")
            if (len(cellList) > 2 and cellList[3].getText() == "10-Q"):
                link = baseURL + row.find_all("a")[0]['href']
                TenQPage.append(link)

    return TenQPage

def ExtractRevenueList(name, incomePageList):
    print "Revenue"
    revenueList = []
    analyzer = TechnicalAnalyzer()
    j = 0
    with open(name + "_revenueList.dat") as file:
        for line in file:
            j += 1
            revenueList.append(float(line))
    file = open(name + "_revenueList.dat", "a+")
    for pageUrl in incomePageList:
        if j <= 0:
            htmlText = urllib2.urlopen(pageUrl).read()
            htmlPage = BeautifulSoup(htmlText, "html.parser")

            rows = htmlPage.find_all("tr")
            revenueRow = None
            for row in rows:
                if len(row.find_all("td")) > 0:
                    revenueLabel = row.find_all("td")[0].getText().lower().strip()

                    if revenueLabel != None and analyzer.AnalyzeTerm(revenueLabel) == REVENUE:
                        revenueRow = row
                        break

            if revenueRow == None:
                print 'ERROR'
            else:
                print pageUrl
                tableElements = BeautifulSoup(str(revenueRow), "html.parser").find_all("td")
                today = '';
                yesterday = '';
                found = 0
                for i in range(1, len(tableElements)):
                    if len(tableElements[i].getText().strip()) > 1 and found == 0:
                        today = tableElements[i].getText().strip().replace(',','')
                        found += 1

                    elif len(tableElements[i].getText().strip()) > 1 and found == 1:
                        yesterday = tableElements[i].getText().strip().replace(',','')
                        break

                revenueChange = (float(today) - float(yesterday)) / float(yesterday)
                print revenueChange
                file.write(str(revenueChange) + "\n")
                revenueList.append(revenueChange)
        else:
            j -= 1

    file.close()
    return revenueList

def ExtractProfitList(name, incomePageList):
    print "Profit"
    profitList = []
    analyzer = TechnicalAnalyzer()
    j = 0
    with open(name + "_profitList.dat") as file:
        for line in file:
            j += 1
            profitList.append(float(line))

    file = open(name + "_profitList.dat", "a+")
    for pageUrl in incomePageList:
        if j <= 0:
            htmlText = urllib2.urlopen(pageUrl).read()
            htmlPage = BeautifulSoup(htmlText, "html.parser")

            rows = htmlPage.find_all("tr")
            profitRow = None
            for row in rows:
                if len(row.find_all("td")) > 0:
                    profitLabel = row.find_all("td")[0].getText().lower().strip()

                if profitLabel != None and analyzer.AnalyzeTerm(profitLabel) == PROFIT:
                    profitRow = row
                    break
                elif profitLabel != None and analyzer.AnalyzeTerm(profitLabel) == LOSS:
                    profitRow = row
                    break

            if profitRow == None:
                    print 'ERROR'
            else:
                firstNegative = 1
                secondNegative = 1
                tableElements = BeautifulSoup(str(profitRow), "html.parser").find_all("td")
                today = '';
                yesterday = '';
                found = 0
                for i in range(1, len(tableElements)):
                    if len(tableElements[i].getText().strip()) > 1 and found == 0:
                        today = tableElements[i].getText().strip().replace(',','')
                        if "(" in today:
                            firstNegative = -1
                            today = today.replace("(", "")
                        print "Today: " + str(today)
                        found += 1

                    elif len(tableElements[i].getText().strip()) > 1 and found == 1:
                        yesterday = tableElements[i].getText().strip().replace(',','')
                        if "(" in yesterday:
                            secondNegative = -1
                            yesterday = yesterday.replace("(", "")
                        print "Yesterday: " + str(yesterday)
                        break

                change = (firstNegative*float(today) - secondNegative*float(yesterday)) / float(yesterday)
                file.write(str(change) + "\n")
                profitList.append(change)
        else:
            j -= 1
    file.close()
    return profitList

def ExtractMarketData(associatedDates):
    shr = getShare('SPX')

    for date in associatedDates:
        pastDate = date.replace(year= date.year - 1)
        print date.year
        print pastDate.year
        allDays = shr.get_historical(pastDate.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d"))
        firstYearPrice = allDays[0]
        lastYearPrice = allDays[-1]

        print lastYearPrice['Close']
        print firstYearPrice['Close']

        return getGrowth(float(lastYearPrice['Close']), float(firstYearPrice['Close']))

def ExtractStockMarketData(associatedDates, companyName):
    print "Market Data"
    shr = getShare(companyName)
    sp500 = Share('^GSPC')
    #print shr.get_historical('2014-04-25', '2014-04-29')

    stockGrowth = []
    marketGrowth = []
    yearGrowth = []

    url = urlBuilder(associatedDates, shr.symbol)


    response = urllib2.urlopen(url)
    reader = csv.reader(response)
    cr = list(reader)

    for date in associatedDates:

        currentDate = date.strftime("%Y-%m-%d")
        pastDate = date.replace(year = date.year - 1).strftime("%Y-%m-%d")
        futureDate = date.replace(year = date.year + 1).strftime("%Y-%m-%d")

        allDays = shr.get_historical(pastDate, currentDate)
        allsp = sp500.get_historical(pastDate, currentDate)
        futureDays = shr.get_historical(currentDate, futureDate)

        firstYearPrice = allDays[0]
        lastYearPrice = allDays[-1]
        futurePrice = futureDays[0]

        firstSP500 = allsp[0]
        secondSP500 = allsp[-1]


        dividendGrowth = 0
        pastGrowth = 0
        change = False
        growthS = getGrowth(float(lastYearPrice['Close']), float(firstYearPrice['Close']))
        growthM = getGrowth(float(secondSP500['Close']), float(firstSP500['Close']))
        growthY = getGrowth(float(firstYearPrice['Close']), float(futurePrice['Close']))

        print str(growthS)
        print growthM
        print growthY
        stockGrowth.append(growthS)
        marketGrowth.append(growthM)
        yearGrowth.append(growthY)

    dividends = dividenFind(associatedDates, cr[1:len(cr) - 1])

    return stockGrowth, dividends, marketGrowth, yearGrowth

def getShare(companyName):
    with open("tickers.txt") as companies:
        for line in companies:
            companiesArray = line.split("|")
            cName = companiesArray[1].lower().strip()

            if cName == companyName:
                share = Share(companiesArray[0])
                return share #Share(companiesArray[0])

def getGrowth(firstYearPrice, secondYearPrice):
    difference = secondYearPrice-firstYearPrice
    growth = difference/firstYearPrice
    percentGrowth = growth
    return percentGrowth

def urlBuilder(associatedDates, share):
    url = 'http://ichart.yahoo.com/table.csv?'

    url = url + 's=' + share + '&c='

    firstYear = associatedDates[-1].year
    lastYear = associatedDates[0].year

    url = url + str(firstYear) + '&a='

    firstMonth = associatedDates[-1].month
    lastMonth = associatedDates[0].month

    url = url + str(firstMonth) + '&b='

    firstDay = associatedDates[-1].day
    lastDay = associatedDates[0].day

    url = url + str(firstDay) + '&f=' + str(lastYear) + '&d=' + str(lastMonth) + '&e=' + str(lastDay) + '&g=v&ignore=.csv'

    return url

def dividenFind(associatedDates, dividenList):
    print "Dividend"
    dividendTrend = []
    for i in range(0, len(associatedDates)):
        currentChange = False

        currentDate = associatedDates[i]
        compareDate = datetime.datetime.strptime(dividenList[0][0], "%Y-%m-%d")
        min = abs(currentDate - compareDate)
        currentIndex = 0
        for j in range(1, len(dividenList)):

            compareDate = datetime.datetime.strptime(dividenList[j][0], "%Y-%m-%d")

            newDiff = abs(currentDate - compareDate)
            if newDiff.days < min.days:
                min = newDiff
                currentIndex = j
                currentChange = True
            else:
                break
        if currentChange == False:
            dividendTrend.append(0.0)

        else:
            pastChange = False
            pastDate = associatedDates[i].replace(year=associatedDates[i].year - 1)
            compareDate = datetime.datetime.strptime(dividenList[0][0], "%Y-%m-%d")
            min = abs(pastDate - compareDate)
            pastIndex = 0

            for j in range(1, len(dividenList)):

                compareDate = datetime.datetime.strptime(dividenList[j][0], "%Y-%m-%d")
                newDiff = abs(pastDate - compareDate)

                if newDiff.days < min.days:
                    min = newDiff
                    pastIndex = j
                    pastChange = True
                else:
                    break


            if pastChange == True:

                pastDividend = float(dividenList[pastIndex][1])
                currentDividend = float(dividenList[currentIndex][1])
                trend = (currentDividend - pastDividend) / pastDividend

                dividendTrend.append(trend)


            else:
                currentDividend = float(dividenList[currentIndex][1])
                dividendTrend.append(currentDividend*100)

    return dividendTrend

def getSymbol(companyName):
    with open("tickers.txt") as companies:
        for line in companies:
            companiesArray = line.split("|")
            cName = companiesArray[1].lower().strip()

            if cName == companyName:
                return companiesArray[0]

def GetStockFundamentels(associatedDates, name):
    symbol = getSymbol(name)
    sP500 = '^GSPC'

    stockGrowth = []
    marketGrowth = []
    yearGrowth = []

    url = urlBuilder(associatedDates, symbol)
    response = urllib2.urlopen(url)
    reader = csv.reader(response)
    cr = list(reader)

    for date in associatedDates:
        currentDate = date.strftime("%Y-%m-%d")
        pastDate = date.replace(year = date.year - 1).strftime("%Y-%m-%d")
        futureDate = date.replace(year = date.year + 1).strftime("%Y-%m-%d")

        if date.weekday() == 5 or date.weekday() ==6:
            currentDate = date - datetime.timedelta(days=3)

        currentYearPrice = float(ystockquote.get_historical_prices(symbol, pastDate, currentDate).items()[-1][1]['Adj Close'])
        pastYearPrice = float(ystockquote.get_historical_prices(symbol, pastDate, currentDate).items()[0][1]['Adj Close'])
        futurePrice = float(ystockquote.get_historical_prices(symbol, currentDate, futureDate).items()[-1][1]['Adj Close'])
        marketPrice = float(ystockquote.get_historical_prices(sP500, pastDate, currentDate).items()[-1][1]['Adj Close'])
        marketPastPrice = float(ystockquote.get_historical_prices(sP500, pastDate, currentDate).items()[0][1]['Adj Close'])

        futureGrowth = (futurePrice - currentYearPrice) / currentYearPrice
        if futureGrowth > 0.1:
            yearGrowth.append(1)
        else:
            yearGrowth.append(0)

        currentGrowth = (currentYearPrice - pastYearPrice) / pastYearPrice
        stockGrowth.append(currentGrowth)

        marketGrowthPrice = (marketPrice - marketPastPrice) / marketPastPrice
        marketGrowth.append(marketGrowthPrice)

    dividends = dividenFind(associatedDates, cr[1:len(cr) - 1])
    return stockGrowth, dividends, marketGrowth, yearGrowth
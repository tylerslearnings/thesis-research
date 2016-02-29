#Name: Quantitative Analyzer Class
#Description: This class will analyze a stock's quantitative aspects and return a list of data entries

from bs4 import BeautifulSoup
from yahoo_finance import Share
from TechnicalAnalyzer import TechnicalAnalyzer
import urllib2
import datetime
import csv


REVENUE = 'revenue'
PROFIT = 'profit'
LOSS = 'loss'
def PerformAnalysis(companyName):
    #Generate Query
    url = GenerateQuery(companyName)
    rowList, associatedDates = ExtractTablesAndRows(url)
    urlList = ExtractURLList(rowList)
    incomePageUrlList = Extract10List(urlList)
    #revenueList = ExtractRevenueList(incomePageUrlList)
    #profitList = ExtractProfitList(incomePageUrlList)

    ExtractStockMarketData(associatedDates, companyName)




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

    return rows, dateStore

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

def ExtractRevenueList(incomePageList):
    revenueList = []
    analyzer = TechnicalAnalyzer()

    for pageUrl in incomePageList:
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
            revenueList.append(revenueChange)


    return revenueList

def ExtractProfitList(incomePageList):
    profitList = []
    analyzer = TechnicalAnalyzer()

    pageUrl = incomePageList[0]

    htmlText = urllib2.urlopen(pageUrl).read()
    htmlPage = BeautifulSoup(htmlText, "html.parser")

    rows = htmlPage.find_all("tr")
    profitRow = None
    for row in rows:
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
        tableElements = BeautifulSoup(str(profitRow), "html.parser").find_all("td")
        today = '';
        yesterday = '';
        found = 0
        for i in range(0, len(tableElements)):
            if len(tableElements[i].getText()) > 1 and found == 0:
                today = tableElements[i + 1].getText().strip().replace(',','')
                found += 1

            elif len(tableElements[i].getText()) > 1 and found == 1:
                yesterday = tableElements[i + 1].getText().strip().replace(',','')
                break

        #print today
        #print yesterday

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

    shr = getShare(companyName)
    sp500 = Share('^GSPC')

    stockGrowth = []
    marketGrowth = []
    yearGrowth = []
    dividends = []

    allDays = None

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

        print growthS
        print growthM
        print growthY
        stockGrowth.append(growthS)
        marketGrowth.append(growthM)
        yearGrowth.append(growthY)

    dividends = dividenFind(associatedDates, cr[1:len(cr) - 1])


def getShare(companyName):
    with open("tickers.txt") as companies:
        for line in companies:
            companiesArray = line.split("|")
            cName = companiesArray[1].lower().strip()

            if cName == companyName:
                return Share(companiesArray[0])

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
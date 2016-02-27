#Name: Quantitative Analyzer Class
#Description: This class will analyze a stock's quantitative aspects and return a list of data entries

from bs4 import BeautifulSoup
from TechnicalAnalyzer import TechnicalAnalyzer
import urllib2
import datetime


REVENUE = 'revenue'
PROFIT = 'profit'
LOSS = 'loss'
def PerformAnalysis(companyName):
    #Generate Query
    url = GenerateQuery(companyName)
    rowList, associatedDates = ExtractTablesAndRows(url)
    urlList = ExtractURLList(rowList)
    incomePageUrlList = Extract10List(urlList)
    revenueList = ExtractRevenueList(incomePageUrlList)
    #profitList = ExtractProfitList(incomePageUrlList)
    for rev in revenueList:
        print rev





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
    MINYEAR = 2006
    rows = []
    dateStore = []
    date = datetime.datetime.strptime('13 Feb 2015', '%d %b %Y')
    stopDate = datetime.datetime.strptime('13 Feb 2015', '%d %b %Y')
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


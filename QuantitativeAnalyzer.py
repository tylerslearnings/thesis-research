#Name: Quantitative Analyzer Class
#Description: This class will analyze a stock's quantitative aspects and return a list of data entries

from bs4 import BeautifulSoup
import urllib2
import datetime

def PerformAnalysis(companyName):
    #Generate Query
    url = GenerateQuery(companyName)
    rowList = ExtractTablesAndRows(url)




def GenerateQuery(companyName):
    #get CIK
    url = ""
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
    date = datetime.date.today()
    currentUrl = url
    i = 1
    j = 0
    while date.year > MINYEAR:
        htmlText = urllib2.urlopen(currentUrl).read()
        soup = BeautifulSoup(htmlText, "html.parser")
        table = soup.find_all("table", {"class" : "tableFile2"})[0]

        tableRows = table.find_all("tr")

        for row in tableRows:
            sRow = BeautifulSoup(str(row), "html.parser")
            if len(sRow.find_all("td")) != 0:
                if sRow.find_all("td")[0].getText() == "10-Q":
                    rows.append(row)

        #check first date
        rSoup = BeautifulSoup(str(table), "html.parser")
        rowCheck = rSoup.find_all("tr")[1]
        dateCheck = BeautifulSoup(str(rowCheck), "html.parser").find_all("td")[3].getText()
        newDate = datetime.datetime.strptime(dateCheck, "%Y-%m-%d")
        date = newDate
        count = 40*i
        currentUrl = url + "&start=" + str(count)
        i += 1

    return rows
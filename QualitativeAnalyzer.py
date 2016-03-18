
from bs4 import BeautifulSoup
import urllib2
from CEO import CEO
import datetime
from alchemyapi import AlchemyAPI

Ceo = "CEO"
PRODUCT = "Product"


def PerformAnalysis(name, associatedDates):
    theAlchemyApi = AlchemyAPI()

    ceoList, productList = GetCompanyInformation(name)
    companyScores = GetCompanyScores(name, associatedDates, theAlchemyApi)
    productScores = GetProductScores(name, productList, associatedDates, theAlchemyApi)
    ceoScores = GetCeoScores(name, ceoList, associatedDates, theAlchemyApi)

    return companyScores, productScores, ceoScores



def GetCompanyInformation(name):
    companyTicker = getTicker(name)
    informationLine = ""
    with open("Stocks") as companies:
        for line in companies:
            elements = line.split("/")

            symbol = elements[0].split(":")[1]
            if symbol == companyTicker:
                informationLine = line
                break


    relevantInformation = informationLine.split("/")[2:]
    i = 0
    currentSection = relevantInformation[i].split(":")[0]
    ceoList = []
    productList = []

    while currentSection == Ceo:
        currentInfo = relevantInformation[i].split(":")
        ceoName = currentInfo[1]
        startYear = int(currentInfo[2])
        endYear = int(currentInfo[3])

        addedCEO = CEO()
        addedCEO.setName(ceoName)
        addedCEO.setYearStart(startYear)
        addedCEO.setYearEnd(endYear)
        ceoList.append(addedCEO)

        i +=1
        currentSection = relevantInformation[i].split(":")[0]

    for j in range(i, len(relevantInformation)):
        currentProduct = relevantInformation[j].split(":")
        productList.append(currentProduct[1])


    return ceoList, productList

def GetCompanyScores(name, associatedDates, alchemyAPI):
    companyScores = []
    i = 0

    with open(name + "_companyScores.dat") as file:
        for line in file:
            i += 1
            companyScores.append(float(line))

    file = open(name + "_companyScores.dat", "a+")
    for currentDate in associatedDates:
        if i <=0:
            pastDate = currentDate.replace(year=currentDate.year - 1)
            tweets = GetTweets(name, currentDate, pastDate)

            response = alchemyAPI.sentiment("text", tweets)
            file.write(response["docSentiment"]["score"] + "\n")
            companyScores.append(float(response["docSentiment"]["score"]))
        else:
            i -= 1

    return companyScores

def GetProductScores(name, productList, associatedDates, alchemyAPI):
    productScores = []
    i = 0
    #Read Existing scores
    with open(name + "_productScores.dat", "r") as file:
        for line in file:
            i += 1
            productScores.append(float(line))

    file = open(name + "_productScores.dat", "a+")
    for currentDate in associatedDates:
        if i <= 0:
            pastDate = currentDate.replace(year=currentDate.year - 1)
            productTweets = ''

            for currentProduct in productList:
                productTweets = productTweets + GetTweets(currentProduct, currentDate, pastDate)

            response = alchemyAPI.sentiment("text", productTweets)
            file.write(response["docSentiment"]["score"] + "\n")
            productScores.append(float(response["docSentiment"]["score"]))
        else:
            i -= 1
    file.close()
    return productScores

def GetCeoScores(name, ceoList, associatedDates, alchemyAPI):
    ceoScores = []
    i = 0
    with open(name + "_ceoScores.dat", "r") as file:
        for line in file:
            i += 1
            ceoScores.append(float(line))

    file = open(name + "_ceoScores.dat", "a+")
    for currentDate in associatedDates:
        if i<= 0:
            pastDate = currentDate.replace(year=currentDate.year - 1)
            ceoTweets = ''
            ceoName = ''
            for ceo in ceoList:
                if ceo.getYearStart() <= currentDate.year and currentDate.year <= ceo.getYearEnd():
                    ceoName = ceo.getName()

            ceoTweets = ceoTweets + GetTweets(ceoName, currentDate, pastDate)

            response = alchemyAPI.sentiment("text", ceoTweets)
            file.write(response["docSentiment"]["score"] + "\n")
            ceoScores.append(float(response["docSentiment"]["score"]))
        else:
            i -= 1

    file.close()
    return ceoScores

def GetTweets(name, currentDate, pastDate):
    tweetList = ''
    dateSegment = currentDate - datetime.timedelta(days=10)
    print currentDate
    while dateSegment > pastDate:
        url = BuildUrl(name, pastDate.strftime("%Y-%m-%d"), dateSegment.strftime("%Y-%m-%d"))
        request = urllib2.Request(url)
        request.add_header("User-Agent", "Mozilla/5.0")
        htmlContent = urllib2.urlopen(request)
        soup = BeautifulSoup(htmlContent, "html.parser")
        allTweets = soup.find_all("div", {"class" : "js-tweet-text-container"})

        for tweet in allTweets:
            tweetList = tweetList + ' ' + tweet.getText().strip()

        dateSegment = dateSegment - datetime.timedelta(days=10)

    return tweetList


def BuildUrl(query, startDate, endDate):
    properQ = query.replace(' ', '%20')
    baseURL = "https://twitter.com/search?"
    query = "q=" + str(properQ) + "%20"
    language = "lang%3Aen%20"
    since = "since%3A" + str(startDate) + "%20"
    until = "until%3A" + str(endDate) + "&src=typd"
    url = baseURL + query + language + since + until

    return url

def getTicker(name):
    with open("tickers.txt") as companies:
        for line in companies:
            companiesArray = line.split("|")
            cName = companiesArray[1].lower().strip()

            if cName == name:
                return companiesArray[0]

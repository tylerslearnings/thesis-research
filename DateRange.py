# Name: Date Range Class
# Description: A class simply made to create a date range for a specific data entry
import datetime

class DateRange:
    startDate   = datetime.date.today()
    endDate     = datetime.date.today()

    def setStartDate(self, date):
        self.startDate = date

    def setEndDate(self, date):
        self.endDate = date

    def setDates(self, sDate, eDate):
        self.startDate = sDate
        self.endDate = eDate
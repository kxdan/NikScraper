from selenium import webdriver
from selenium import webdriver
import selenium.webdriver.support.ui as ui
import os
import logging
import csv

DEBUG = True
logger = logging.getLogger('ITSScraper')
FILENAME = 'Showroom Barcodes(All Categories).csv'

def init():
    # create logger with 'spam_application'
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('ITSScraper.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info("Current OS, are we on linux? " + str(DEBUG))


def getInfoForBarcode(strBarcode, browser):

    browser.get("https://www.its.co.uk/search.aspx?rs=" + strBarcode)
    resultElements = browser.find_elements_by_class_name("df-card")
    logger.info(str(len(resultElements)) + " results found for barcode " + strBarcode)
    if (len(resultElements) == 1):
        try:

            #SuccessCase/1
            resultElement = resultElements[0]
            link = resultElement.find_element_by_xpath("//a[@class='df-card__main doofinderProdCard']")
            link = link.get_attribute("href")
            browser.get(link)

            barCodeSpan = browser.find_element_by_class_name("BarCode")
            barCodeSpan = barCodeSpan.find_element_by_tag_name("span")
            value = barCodeSpan.text
            value = value.split(' ')[1]

            #ErrorCase, fucked form
            if value != strBarcode:
                logger.debug("Bad page barcode " + strBarcode)
                return link + ", " + strBarcode + "," + "incorrect barcode on page - price not found"

            priceWithVAT = browser.find_element_by_class_name("VatInc")
            return link +", " + strBarcode +"," + priceWithVAT.find_element_by_tag_name("span").text

        except:
            return "erroronform," + strBarcode + ",erroronform"
    else:
        logger.debug("Too many results, ignoring " + strBarcode)
        return "unknown" + ", " + strBarcode + "," + "Too many results, search failed"


def getListOfBarcodes():
    lstBarcodes = []
    logger.debug("Writing to file")
    with open(FILENAME) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row != '':
                lstBarcodes += row

    return lstBarcodes

def outputToCsv(lstToOutput):
    with open(FILENAME.split('.')[0] + "-OUTPUT.csv", 'w') as outputFile:
        fileWriter = csv.writer(outputFile)
        for row in lstToOutput:
            fileWriter.writerow([row])

def openBrowser():
    if DEBUG:
        logger.info("Using default linux dir")
        browser = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    else:
        executablepath = os.path.dirname(__file__) +  '/chromedriver.exe'
        #browser = webdriver.Chrome(executable_path="C:/Users/damorri/Downloads/chromedriver_win32/chromedriver.exe")
        browser = webdriver.Chrome(executable_path=executablepath)
    return browser

init()
lstBarcodes = getListOfBarcodes()

#lstBarcodes = ["5706915057058", "5013969704808", "3253560422875", "045242342211", "9341231040160"]

csvFileRows =[]
browser = openBrowser()

count = 0
for element in lstBarcodes:
    print("Processing element: " + str(count) + " of " + str(len(lstBarcodes)))
    logger.debug("Processing element: " + str(count) + " of " + str(len(lstBarcodes)))
    csvFileRows.append(getInfoForBarcode(element, browser))
    count+=1


outputToCsv(csvFileRows)

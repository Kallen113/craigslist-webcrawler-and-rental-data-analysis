"""This script will parse the names of the subregions within a
given craiglist metropolitan/large city region (ie, sfbay, Chicago,  San Diego, etc.).

NB: We need to a priori know the URL to the craigslist homepage
of the given region. 
For ex: <https://sandiego.craigslist.org/> is the homepage for craglist San Diego."""

#import various data analysis, web scraping, and web crawling libraries--ie, pandas, various Selenium modules, etc.
#file processing lbraries (os), time (for .sleep() method), datetime, iteration, and other tools
import csv
import os
import time
import random

# data analysis libraries
import pandas as pd
from pandas.core.frame import DataFrame

#web crawling, web scraping & webdriver libraries and modules
from selenium import webdriver  # NB: this is the main module we will use to implement the webcrawler and webscraping. A webdriver is an automated browser.
from webdriver_manager.chrome import ChromeDriverManager # import webdriver_manager package to automatically take care of any needed updates to Chrome webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options  # Options enables us to tell Selenium to open WebDriver browsers using maximized mode, and we can also disable any extensions or infobars



def parse_subregion_via_xpath(craigslist_url_homepage, list_to_append: list, xpath_arg):
    """ Scrape data from HTML element by looking up xpath (via selenium find_elements_by_xpath() method).
    a.) Initialize selenium WebDriver, and make get request to access given webpage
    b.) Wait until given HTML element has loaded on page using WebDriverWait() method.
    c.) Then, nitialize an empty list, and scrape the HTML element and extract the element's text data, and append to list."""   
    ## Initialize a Webdriver for selenium to implement the webcrawler:

    # specify various options to reduce the likelihood that selenium's webdriver HTML-parsing functions might miss HTML elements we want the script to scrape and parse
    options = Options()  # initialize Options() object, so we can customize and specify options for the web driver
    options.add_argument("--disable-extensions")  # disable any browser extensions
    options.add_argument("start-maximized")   # maximize webdriver's browser windows
    options.add_argument("disable-infobars") # disable browser infobars

    # install and/or update to latest Chrome Webdriver, and implement the options specified above:
    web_driver  = webdriver.Chrome(
        ChromeDriverManager().install(),  # install or update latest Chrome webdriver using using ChromeDriverManager() library
        options=options  # implement the various options specified above
        )

    # access craigslist homepage for given region:
    web_driver.get(craigslist_url_homepage) # do get request to access the homepage of the given craiglist region

    # specify acceptable download delay (in seconds)
    download_delay = 15

    # a.) wait until given HTML element has loaded--ie, until the webpage's "searchform" form tag has been loaded, or up to a maximum 15 seconds (ie, given value of download_delay)


    try: # wait until the ul tag with class name of "sublinks" has been loaded, up to a maximum of 15 seconds (given download_delay)
        WebDriverWait(web_driver, download_delay).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sublinks"))
        )  # NB: you need to use a tuple as the argument of the selenium EC.presence_of_element_located() function, hence the double-parantheses
        print('\nPage has loaded, and the data are ready to download.\n')
    except TimeoutException:
        """ Return error message if loading the webpage takes longer than the maximum n seconds:"""
        print(f"Loading the webpage's searchform element timed out: ie, it took longer than the  maximum number of {download_delay} seconds designated by the download_delay.")

    # initialize empty list to contain the names of subregions
    craigslist_subregions = []  

    # b.) scrape the HTML element, extract text, and append to given list
    for scraped_html in web_driver.find_elements_by_xpath(xpath_arg):
        craigslist_subregions.append(scraped_html.text)  # parse text data from scraped html element
        # sanity check
        print(f'{scraped_html.text}')

    # return scraped data as list
    return craigslist_subregions


def main():
    # NB: look up subregions for craigslist San Diego:
    SD_homepage = 'https://sandiego.craigslist.org/'

    
    # initialize empty list to contain the names of subregions
    craigslist_subregions = []

    # specify xpath argument  
    ul_subregions_xpath = '//*[@id="topban"]/div[1]/ul'


    parse_subregion_via_xpath(SD_homepage, craigslist_subregions, ul_subregions_xpath)


if __name__=="__main__":
    main()
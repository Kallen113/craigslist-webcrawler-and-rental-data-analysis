#import various data analysis, web scraping, and web crawling libraries--ie, pandas, various Selenium modules, etc.
#file processing lbraries (os), time (for .sleep() method), datetime, iteration, and other tools
import os
import time
import random
import itertools
from itertools import islice
from collections import OrderedDict  # use to remove duplicates from rental listing urls list
import datetime

## **NB: To run this webcrawler, we need to use  the python -m 'module' option at command-line, and invoke the main.py Python script at terminal, but without using the .py extension. # The python -m (ie, module) option enables any relative imports to work correctly with the given Python script being invoked by treating the script as a module instead of a regular Python script.
## This is an alternative to adding all imported scripts as well as the parent direc to the sys.path. See Python documentation re: running Python scripts via command-line: <https://docs.python.org/2.7/using/cmdline.html>


# data analysis libraries
import pandas as pd
from pandas.core.frame import DataFrame

#web crawling, web scraping & web access  libraries and modules
from lxml import html
from bs4 import BeautifulSoup
import urllib.request
from selenium import webdriver  # NB: this is the main module we will use to implement the webcrawler and webscraping. A webdriver is an automated browser.
from webdriver_manager.chrome import ChromeDriverManager # import webdriver_manager package to automatically take care of any needed updates to Chrome webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options  # Options enables us to tell Selenium to open WebDriver browsers using maximized mode, and we can also disable any extensions or infobars

# import functions for cleaning misclassified data or city names data that we need to rename, for SF and  Santa Cruz counties, respectively--ie, subregion of 'sfc' or 'scz', respectively
# NB: since these scripts are from the same directory, we should use the '.file_name'--ie, dot prefix to specify we are importing from the same directory as this script:
from .clean_city_names import clean_city_names_for_sf, sf_neighborhoods, clean_given_city_names_data, sj_neighborhoods, oakland_neighborhoods, alameda_neighborhoods, hayward_neighborhoods, richmond_neighborhoods, santa_clara_neighborhoods  # import from same directory (ie,. dot prefix) functions to clean SF city names data and import lists of all neighborhoods for given cities--e.g., SF neighborhoods (including various abbreviations used on craigslist)
from .clean_santa_cruz_data import clean_mislabelled_santa_cruz_data, san_cruz_cities  # import from same directory (ie,. dot prefix) a function to remove rows that are misclassified as 'scz', and import list of Santa Cruz county cities

# import data cleaning script from the parent direc (*ie, scraper_and_data_cleaning_functions.py), which includes various data cleaning and HTML-parser functions via selenium methods:
from scraper_and_data_cleaning_functions import clean_scraped_sqft_data, clean_scraped_bedroom_data, clean_scraped_bathroom_data, clean_scraped_cities_data, parse_kitchen_data,  parse_attrs, print_scraped_sanity_checks


#define the Craigslist web scraper and web crawler, which we will use to scrape Craigslist SF Bay area rental listings data:
class Craigslist_Rentals(object):
    """" Define a class that will enable us to perform a customized search for rental prices--within the SF Bay area--in which
    we can perform a search for a specific region in the SF Bay area (e.g., "pen" refers to the pnensula region ), set the min & max values for the rental prices, the rental period (presumably as monthly), and the sale_date, which is the date on which the apartment or home will be availabile for consumers to move into. """

    def __init__(self, region: str, subregion: str, housing_category: str, min_price: int, max_price: int, rent_period: int, sale_date: str):
        """ Define the customized URL to search for rental listings within the SF Bay Area.
        This URL will be used to implement the selenium web scraper.

        Finally, initialize a selenium webdriver for the web crawler (Chrome in our case) and set the maxnumber of seconds we will allow as a delay in between when the GET request is sent via the web driver and the time in which the crawled webpage takes to load before starting a download for each given webpage."""
        # define various parameters for a customized SF Bay Area Craigslist rental listing URL:
        self.region = region
        self.subregion = subregion
        self.housing_category = housing_category # NB: 'apa' will search for apartments and homes for rent (the intended data for this project). Other categories on craigslist are numerous, including real estate (for sale) homes by broker or by owner, respectively, etc.
        self.min_price = min_price
        self.max_price = max_price
        self.rent_period = rent_period
        self.sale_date = sale_date
        # specify each of the above parameters --using an f-string--to enable us to make a customized search of SF Bay Area rental listings on Craigslist
        self.url = f"https://{region}.craigslist.org/search/{subregion}/{housing_category}?/min_price={min_price}&max_price={max_price}&availabilityMode=0&rent_period={rent_period}&sale_date={sale_date}"
        #sanity check the craigslist URL derived from the __init__() function:
        print(f"The craigslist URL we will use to perform the web crawler is: \n{self.url}")
        # initialize a webdriver for selenium to use for our webcrawler:
        driver_path = r"C:\webdrivers\chromedriver_win32.exe\chromedriver.exe" #specify path to webdriver
        # specify various options to reduce the likelihood that selenium's webdriver HTML-parsing functions might miss HTML elements we want the script to scrape and parse
        options = Options()  # initialize Options() object, so we can customize and specify options for the web driver
        options.add_argument("start-maximized")   # maximize webdriver's browser windows
        options.add_argument("--disable-extensions")  # disable any browser extensions
        options.add_argument("disable-infobars") # disable browser infobars
        # install and/or update latest Chrome Webdriver, and implement the options specified above:
        self.web_driver  = webdriver.Chrome(
            ChromeDriverManager().install(),  # install or update latest Chrome webdriver using using ChromeDriverManager() library 
            options=options  # implement the various options stated above
        )
        self.download_delay = 15   # set maximum download delay of 15 seconds, so the web scraper can wait for the webpage to load and respond to our program's GET request(s) before scraping and downloading data


    def load_craigslist_form_URL(self):
        """ Load the craigslist form URL, as specified in the __init__().
        Use WebDriverWait() function to ensure the web crawler will wait until the Craigslist form object with ID of "searchform" has loaded, and then download and parse the desired data.

        This function will wait up to a maximum number of seconds as designated by download_delay, otherwise a TimeOutException will trigger."""
        self.web_driver.get(self.url) # implement a GET request by loading up the customized Craigslist SF Bay Area rental listing pages via a Chrome webdriver

        """Tell the web scraper to wait until the webpage's "searchform" form tag has been loaded, or up to a maximum 15 seconds (ie, given the value of download_delay"""
        try: # wait until the form tag with ID of "searchform"--ie, the Craigslist page given our search results--has been loaded, or up to a maximum of 5 seconds (given download_delay)
            WebDriverWait(self.web_driver, self.download_delay).until(
                EC.presence_of_element_located((By.ID, "searchform"))
            )  # NB: you need to use a tuple as the argument of the selenium EC.presence_of_element_located() function, hence the double-parantheses
            print('\nPage has loaded, and the data are ready to download.\n')
        except TimeoutException:
            """ Return error message if loading the webpage takes longer than the maximum n seconds:"""
            print(f"Loading the webpage's searchform element timed out: ie, it took longer than the  maximum number of {self.download_delay} seconds designated by the download_delay.")

    def parse_html_via_class_name(self, html_class_name: str, list_to_append: list):
        """ Scrape data from HTML element by looking up class name (via selenium find_elements_by_class_name() method).
        a.) Except if a NoSuchElementException or TimeoutException occurs--indicating a given element does not exist--then wait until given HTML element has loaded on page using WebDriverWait() method.
        b.) Then, scrape the HTML element and extract the element's text data."""
        try:
            ## a.) wait until given HTML element has loaded
            wait_until = WebDriverWait(self.web_driver, self.download_delay)  # wait up to 15 seconds to let HTML element load on given rental listing webpage
            wait_until.until(EC.presence_of_element_located((By.CLASS_NAME, html_class_name)))
            ## b.) scrape the HTML element, extract text, and append to given list
            scraped_html = self.web_driver.find_element_by_class_name(html_class_name)

        except (TimeoutException, NoSuchElementException) as excep:
            """If the given rental listing page does not contain given element, append 'nan' value to indicate missing value."""
            return list_to_append.append('nan')  # indicate missing value

        return list_to_append.append(scraped_html.text)  # parse text data from scraped html element, and append to list for given variable of interest


    def parse_html_via_xpath(self, xpath_arg: str, list_to_append: list):
        """ Scrape data from HTML element by looking up xpath (via selenium's find_elements_by_xpath() method), within a try except control flow clause to account for rental listings that are missing a given HTML element.
        a.) Except if a NoSuchElementException or TimeoutException occurs--indicating a given element does not exist--then wait until given HTML element has loaded on page using WebDriverWait() method.
        b.) Then, scrape the HTML element and extract the element's text data."""
        try:
            # a.) wait until given HTML element has loaded
            wait_until = WebDriverWait(self.web_driver, self.download_delay)  # wait up to 15 seconds to let HTML element load on given rental listing webpage
            wait_until.until(EC.presence_of_element_located((By.XPATH, xpath_arg))) # a.) wait until given HTML element has loaded, or up to 15 seconds
            # b.) scrape the HTML element, extract text, and append to given list
            scraped_html = self.web_driver.find_element_by_xpath(xpath_arg)

        except (TimeoutException, NoSuchElementException) as excep:
            """If the given rental listing page does not contain given element, append 'nan' value to indicate missing value."""
            return list_to_append.append('nan')  # indicate missing value

        return list_to_append.append(scraped_html.text)  # parse text data from scraped html element, and append to list for given variable of interest

    def parse_html_via_xpath_and_click(self, xpath_arg: str, list_to_append: list):
        """ Scrape data from HTML element by looking up xpath (via selenium find_elements_by_xpath() method), but then click to reveal the date-time data."""
        # a.) wait until given HTML element has loaded
        try:
            wait_until = WebDriverWait(self.web_driver, self.download_delay)  # wait up to 15 seconds to let HTML element load on given rental listing webpage
            wait_until.until(EC.presence_of_element_located((By.XPATH, xpath_arg))) # a.) wait until given HTML element has loaded, or up to 15 seconds
            # b.) scrape the HTML element, extract text, and append to given list
            date_posted_click = self.web_driver.find_element_by_xpath(xpath_arg)
            # # provide delay to avoid being flagged by server as a bot, before we access each subsequent listing.
            rand_sl_time = random.randrange(2, 8) # specify a range of pseudo-random values from 2 to 8 seconds
            time.sleep(rand_sl_time)
            # click on element so that it will reveal the date-time
            self.web_driver.execute_script("arguments[0].click();", date_posted_click)  # .executescript() is a JavaScript-based selenium method that tells the webdriver to initiate a click on the given HTML element.

        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as excep:
            """If the given rental listing page does not contain given element, append 'nan' value to indicate missing value."""
            return list_to_append.append('nan')  # indicate missing value

        return list_to_append.append(date_posted_click.text)  # parse text data from scraped html element, and append to list for given variable of interest


    def mk_direc_for_scraped_data(self, parent_direc: str, new_path: str):
        """Create directory (if it doesn't exist) to contain the scraped data, with separate directories for specific regions and subregions."""
        parent_direc = parent_direc  # specify the parent directory where we will create new direc
        # add region and sub-region names as separate child directories
        new_path = new_path + "\\" +f"{self.region}" + "\\" + f"{self.subregion}"
        path_for_csv = os.path.join(parent_direc, new_path)  # specify full path--including the new path we will create

        if not os.path.exists(path_for_csv):
            """ Create directory to contain scraped data, if path does not exist"""
            return os.makedirs(path_for_csv)

    def export_to_csv(self, df: DataFrame, parent_direc_for_csv: str):
        """Save df as CSV in the new path, sans index. Given the mk_direc...() function,
        we will save the CSV file inside the region and subregion subdirectories
        (but only specify parent directory containing all of the scraped data).
        Append today's date and region + subregion names to CSV file name."""
        # specify preface of CSV file name
        csv_preface_name = 'craigslist_rental'
        # add region and subregion sub-directories to path where we will save the CSV file
        path_for_csv = parent_direc_for_csv + "\\" + f"{self.region}" + "\\" + f"{self.subregion}"
        # append today's date and the .csv extension to suffix of CSV file name
        today_dt_str = datetime.date.today().strftime("%m_%d_%Y")  # get today's date in 'mm_dd_YYYY' format
        # add region and subregion names to CSV file, and add .csv extension:
        csv_file_name = csv_preface_name + '_' + self.region + '_' + self.subregion + '_' + today_dt_str + '.csv' # append today's date and .csv extension to the file name
        # export dataframe to CSV. NB: concatenate CSV file name to the path by using os.path.join(). Also, do not export index since it does not contain pertinent data
        return df.to_csv(os.path.join(path_for_csv, csv_file_name), index=False)


    def obtain_listing_data(self):
        """Crawl over each page of rental listings, given starting URL from Craigslist_Rentals class. Obtain the URLs from each page's Craigslist rental listings. Then, parse the data of each 'inner' rental listing by accessing each of these URLs, and use xpath or class name selenium methods to scrape and parse various HTML elements (ie, the listing data that we want to scrape)."""
        #initialize empty lists that will contain the data we will scrape
        listing_urls = []  #list to contain the starting page's listing URLs
        cities = []
        prices = []
        ids = []
        listing_descrip=[]
        bedrooms = []
        sqft = []
        bathrooms = []
        kitchen = []
        attr_vars =[]
        date_posted = []

        # crawl over each listings page, by looking for 'next' page buttons and clicking these after scraping relevant data such as the URL's of the inner listings. An exception will occur once the final page is reached since no additional 'next' page buttons will be present.
        while True:
            try: # iterate over each page of rental listings, given starting URL
                window_current_URL = self.web_driver.current_url # get URL of currently-accessed page
                webpage_html = urllib.request.urlopen(window_current_URL)
                soup_html = BeautifulSoup(webpage_html, "lxml")  # initialize a BeautifulSoup object so we can use this library to more easily parse specific HTML objects
                #iterate over each "a" tag containing the individual rental listing URLs, and append each href URL to the listing_urls list:
                for url in soup_html.findAll("a", {"class":"result-title hdrlnk"}):  # extract 'a' HTML tags that contain the listing URLs, for each of the listings on the Craigslist pages we are crawling on
                    listing_urls.append(url["href"])  # extract the href data from each of the rental listing's URLs, and append these to the list

                ## Navigate to each next page by clicking the button located at the <a> tag:
                next_page = WebDriverWait(self.web_driver, self.download_delay).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'next')]"))
                    )  # wait until 'next page' button element is clickable
                self.web_driver.execute_script("arguments[0].click();", next_page) # click to proceed to the next page--the execute_script() is a selenium method that enables us to invoke a JavaScript method and tell the webdriver to click the 'next' page button
                print("\nNavigating to the next page\n")
                # wait n seconds before accessing the next page, but randomize the amount of time delay, in order to mimic more human-like browser activity
                rand_sl_time = random.randrange(2, 8) # specify a range of pseudo-random values from 2 to 8 seconds
                time.sleep(rand_sl_time) # wait minimum of 1 second to let the page's various HTML contents to load, before we start extracting the various data on each subsequent page.
                print(f"\nNew page's URL--after clicking on next page button is: \n{self.web_driver.current_url}\n")

            # NB: if 1 of the following 3 exceptions occur, we will stop the while loop from navigating to the next page, since the last page will have been reached
            except (TimeoutException, WebDriverException, NoSuchElementException) as excep:
                # indicate that the last page has been reached
                print("Last page reached")

                # parse last page's data
                window_current_URL = self.web_driver.current_url # get URL of currently-accessed page
                webpage_html = urllib.request.urlopen(window_current_URL)
                soup_html = BeautifulSoup(webpage_html, "lxml")  # initialize a BeautifulSoup object so we can use this library to more easily parse specific HTML objects
                #iterate over each a tag containing the individual rental listing URLs, and append each href URL to the listing_urls list:
                for url in soup_html.findAll("a", {"class":"result-title hdrlnk"}):  # extract 'a' HTML tags that contain the listing URLs, for each of the listings on the Craigslist pages we are crawling on
                    listing_urls.append(url['href'])  # extract the href data from the HTML 'a' tags from each of the rental listing's URLs, and append these hrefs to the list
 
                ## remove any duplicate listing urls by assigning it to a list of OrderedDict.fromkeys() method, which will remove duplicate elements (urls) while also retaining the order of the list's elements.
                listing_urls = list(OrderedDict.fromkeys(listing_urls))  # remove any duplicate listing urls

                # wait a minimum of 8 seconds, but randomize the amount of time delay, in order to mimic a more human-like browser activity
                rand_sl_time = random.randrange(8, 15) # specify a range of pseudo-random values from 8 to 15 seconds
                #  iterate over each of the rental listing href URLs
                # N = 3

                for list_url in listing_urls:
                # for list_url in itertools.islice(listing_urls, N):
                        """Ie: keep iterating over each url element of rental listings until a duplicate id is scraped, in which case we should terminate the for loop. """
                        # NB: I can probably use a while true loop instead of the if...else in the finally statement to stop this from becoming a sort of infinite loop
                        try:
                            # access the individual rental listings via the href URLs we have parsed:
                            self.web_driver.get(list_url)

                        except (TimeoutException, ElementClickInterceptedException, NoSuchElementException) as excep:
                            """If a TimeoutException is encountered--e.g., if a rental listing posting has expired, then append 'nan' values for each list (aside from the listing_urls since this has already been populated) for that given listing, and move onto the remaining listing URLs remaining within the for loop. NB: An ElementClickInterceptedException exception occurs when the webdriver attempts to click an element that has the incorrect xpath. """
                            print(f"\n\nTimeoutException, NoSuchElementException, or ElementClickInterceptedException has been encountered for given rental listing:\n{list_url}\n\n")
                            # input nan values for each scraped data list if given listing has been deleted or another issue has caused a TimeoutException error
                            nan_val = 'nan'  # specify nan value, which we will use to append to each of the lists as we attempt to scrape the data:
                            ids.append(nan_val)  ## listing ids
                            prices.append(nan_val)  ##  rental price data
                            cities.append(nan_val)  ##  city names
                            bedrooms.append(nan_val) ## number of bedrooms data
                            bathrooms.append(nan_val) ##  number of bathrooms data
                            sqft.append(nan_val) ##  sqft data
                            listing_descrip.append(nan_val) ##  listing descriptions
                            attr_vars.append(nan_val) # attribute data
                            date_posted.append(nan_val) #date_posted

                        else:
                            """Ie: Run the webcraper functions (based on xpath or class name) *if* the rental listing URL has not been deleted--ie, if none of the 3 denoted errors are encountered. What this means in practice is that the rental listing should be still be active and not deleted. So, we can proceed with scraping the data for the various variables. The xpath or class-name parsing functions will each implement a try...except to check for a NoSuchElementException in case a given rental listing is missing data for one or more of the attributes we want to scrape. """
                            ## Scrape listing ids
                            self.parse_html_via_xpath('/html/body/section/section/section/div[2]/p[1]', ids)

                            ## Scrape rental price data
                            self.parse_html_via_class_name("price", prices)

                            ## Scrape city names
                            self.parse_html_via_xpath("//html/body/section/section/h1/span/small", cities)

                            ##  Parse number of bedrooms data-
                            self.parse_html_via_xpath("/html/body/section/section/h1/span/span[2]", bedrooms)

                            ##  Parse number of bathrooms data
                            self.parse_html_via_xpath("/html/body/section/section/section/div[1]/p[1]/span[1]/b[2]", bathrooms)

                            ## Parse sqft data:
                            self.parse_html_via_xpath("/html/body/section/section/h1/span/span[2]", sqft)


                            ## From listing descriptions, we can scrape data such as kitchen, dishwasher, and refrigerator (ie, several amenities) data:
                            self.parse_html_via_xpath('//*[@id="postingbody"]', listing_descrip)

                            # scrape attribute data
                            self.parse_html_via_xpath("/html/body/section/section/section/div[1]/p[2]", attr_vars)

                            # parse the date posted data (given we have clicked the element----NB: we need to click the element so we can scrape the specific date rather than a str specifying 'x days ago')
                            self.parse_html_via_xpath_and_click("/html/body/section/section/section/div[2]/p[2]/time", date_posted)


                        finally: # move on with for loop regardless of whether or not either of the 2 denoted errors has been encountered
                            print(f"\nListing URL being crawled on:\n  {list_url}\n\n")
                            print(f"Number of listings we have crawled over:\n{len(prices)}\n")
                            print(f"There are {len(listing_urls)-len(prices)} more listings left.")

                            # keep iterating through each url until the listing_urls list has been crawled over fully (ie, based on the number of listing ids) 
                            if len(ids) < len(listing_urls):  # If additional listings in the list have not been crawled on, then move on to the next rental listing in the listing_urls--ie, via pass command
                                # provide delay to avoid being flagged by server as a bot, before we access each subsequent listing.
                                time.sleep(rand_sl_time)
                                pass # I.e.: move on to the next rental listing
                            else:  # Ie: Once we have gone through each listing URL, then immediately terminate the for loop."""
                                break


                ## Final data cleaning and parsing steps-- bedroom, sqft, bathrooms, prices, etc.:

                # sqft data-- 1.) search for 'ft2' substring to indicate presence of sqft data. If this substring is found in given element, then parse the sqft data by removing the given substring and getting only the last element after splitting on whitespace so we can remove the bedroom data, which is always contained just before the sqft data. If sqft data does not exist, then return an 'nan' value instead to denote a null. When the function detects previous 'nan' values, leave unchanged as 'nan'.
                sqft = clean_scraped_sqft_data(sqft)  # parse the sqft data, and ensure it's sqft data by checking if given listing element contains the substring 'ft2'

                # bedrooms data cleaning--
                bedrooms =  clean_scraped_bedroom_data(bedrooms)

                # bathrooms data--
                bathrooms = clean_scraped_bathroom_data(bathrooms)

                # cities (ie, city names) data cleaning:
                cities = clean_scraped_cities_data(cities) # Remove all parantheses markings from each list element

                # prices data cleaning:
                prices = [p.lstrip("$") for p in prices]

                # data cleaning-- remove 'post id: ' prefix and parse out just the id values alone:
                ids = [i.lstrip('post id: ') if 'post id: ' in i else i for i in ids]  # remove 'post id: ' prefix

                ## Parse kitchen data from listing descriptions:
                kitchen = parse_kitchen_data(kitchen, listing_descrip)

                # provide date when webcrawler is run (ie, today's date when webcrawler is run), and impute these date data for *all* scraped records from the latest run of this webcrawler script  *I.e.: reference the len() of any one of the attributes that was scraped
                date_of_webcrawler = [time.strftime("%Y-%m-%d")] * len(ids)  # impute today's date to all records that we scraped from the latest run of this webcrawler script

                """Transform the various lists--which contain the various parsed rental listings' data
                --to a Pandas DataFrame."""
                ## transform each list of scraped data to a dictionary of lists, and then transform to a Pandas DataFrame
                # NB: transforming a dictionary of lists to a Pandas df is a bit faster than using .zip() on the untransformed lists, and then transforming to pandas df--namely: about 63% faster to use a list of dictionaries to dataframe.

                ## Transform the lists to a dictionary of lists, and then use pd.DataFrame() with dictionary comprehension and pd.Series() so that we can retain all of the column names
                dict_of_attrs = {
                    'listing_urls':listing_urls, 'ids':ids, 'sqft':sqft, 'cities':cities, 'prices':prices,
                    'bedrooms':bedrooms, 'bathrooms':bathrooms, 'attr_vars':attr_vars, 'listing_descrip':listing_descrip,
                    'date_of_webcrawler':date_of_webcrawler,'kitchen':kitchen, 'date_posted':date_posted
                    }  # dictionary of the lists containing the scraped data

                ## Transform the dictionary of lists to dataframe:
                df_from_dict = pd.DataFrame({key:pd.Series(val) for key, val in dict_of_attrs.items()})

                ## add name of region and subregion as new cols to df, using the parameters of the Craigslist_Rentals class
                df_from_dict['region'] = f"{self.region}"
                df_from_dict['sub_region'] = f"{self.subregion}"

                ## data wrangling-- parse specific attributes (e.g., 'cats_OK') from the attr_vars and listing_descrip cols as indicator variables
                parse_attrs(df_from_dict) # NB: run parse_attrs() function comprising factored-out code from imported data cleaning script--ie, parse data as indicator variables for df_from_dict DataFrame

                ## Final sanity check on scraped data by printing from df_from_dict DataFrame:
                print_scraped_sanity_checks(df_from_dict)

                return df_from_dict

    def df_to_CSV_data_pipeline(self, df):
        """Clean specific subregions' city names data, create directory for given region and subregion, and export DataFrame containing scraped data to CSV within said directory"""
        ## create directory to contain scraped data (if not exists):
        self.mk_direc_for_scraped_data("D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper", "scraped_data")

        ## specify this (potentially new) path to contain the scraped data CSV files
        scraped_data_path = "D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\scraped_data"

        ## clean data for specific subregions, and export scraped data from Dataframe to CSV file:

        if self.subregion=='sfc':  # clean San Francisco data
            """If subregion is 'sfc', transform city names data from neighborhood names to 'San Francisco', and remove any data misclassified as being within this county."""
            df = clean_city_names_for_sf(sf_neighborhoods, df) # clean scraped data if scraped from 'sfc' subregion
            self.export_to_csv(df, scraped_data_path)
            return df

        elif self.subregion=='scz': # clean Santa Cruz data
            """If subregion is 'scz', remove any data misclassified as being within this county."""
            df = clean_mislabelled_santa_cruz_data(san_cruz_cities, df) # clean scraped data if scraped from 'scz' subregion
            self.export_to_csv(df, scraped_data_path)
            return df

        elif self.subregion=='sby':  # clean South Bay data
            """If subregion is 'sby', clean city names data for cities such as San Jose & Santa Clara."""
            df = clean_given_city_names_data('San Jose', sj_neighborhoods, df)    # clean San Jose data
            df = clean_given_city_names_data('Santa Clara', santa_clara_neighborhoods, df)  # clean Santa Clara data
            self.export_to_csv(df, scraped_data_path)
            return df

        elif self.subregion=='eby':  # clean East Bay data
            """If subregion is 'eby', clean city names data for cities such as Oakland & Hayward."""
            df = clean_given_city_names_data('Oakland', oakland_neighborhoods, df) # clean Oakland data
            df = clean_given_city_names_data('Hayward', hayward_neighborhoods, df)  # clean Hayward data                    
            df = clean_given_city_names_data('Alameda', alameda_neighborhoods, df)  # clean Alameda data
            df = clean_given_city_names_data('Richmond', richmond_neighborhoods, df)  # clean Richmond dat
            self.export_to_csv(df, scraped_data_path)
            return df

        else: 
            """Ie: do not perform any additional data cleaning if subregion is not SF, Santa Cruz, South Bay, or East Bay--in other words, for North Bay or Peninsula data"""
            self.export_to_csv(df, scraped_data_path)
            return df
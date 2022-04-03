#import various data analysis, web scraping, and web crawling libraries--ie, pandas, various Selenium modules, etc.
#file processing lbraries (os), time (for .sleep() method), datetime, iteration, and other tools
import csv
import os
import time
import random
import itertools
from itertools import islice
from collections import OrderedDict  # use to remove duplicates from rental listing urls list
import datetime

# data analysis libraries
import pandas as pd
from pandas.core.frame import DataFrame
from scipy.fft import fft

#web crawling, web scraping & webdriver libraries and modules
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
from scraper_and_data_cleaning_functions import clean_scraped_sqft_data, clean_scraped_bedroom_data, clean_scraped_bathroom_data, clean_scraped_cities_data, parse_kitchen_data,  parse_attrs, clean_bedroom_studio_apt_data, clean_listing_ids_and_remove_nan_substr, print_scraped_sanity_checks


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

        ## Create customized URL for  specify each of the above parameters --using an f-string--to enable us to make a customized search of SF Bay Area rental listings on Craigslist
        self.url = f"https://{region}.craigslist.org/search/{subregion}/{housing_category}?/min_price={min_price}&max_price={max_price}&availabilityMode=0&rent_period={rent_period}&sale_date={sale_date}"
        #sanity check the craigslist URL derived from the __init__() function:
        print(f"The craigslist URL we will use to perform the web crawler is: \n{self.url}")

        ## Initialize a Webdriver for selenium to implement the webcrawler:
        driver_path = r"C:\webdrivers\chromedriver_win32.exe\chromedriver.exe" #specify path to webdriver

        # specify various options to reduce the likelihood that selenium's webdriver HTML-parsing functions might miss HTML elements we want the script to scrape and parse
        options = Options()  # initialize Options() object, so we can customize and specify options for the web driver
        options.add_argument("--disable-extensions")  # disable any browser extensions
        options.add_argument("start-maximized")   # maximize webdriver's browser windows
        options.add_argument("disable-infobars") # disable browser infobars

        # install and/or update to latest Chrome Webdriver, and implement the options specified above:
        self.web_driver  = webdriver.Chrome(
            ChromeDriverManager().install(),  # install or update latest Chrome webdriver using using ChromeDriverManager() library
            options=options  # implement the various options specified above
            )
        self.download_delay = 20   # set maximum download delay of 20 seconds, so the web scraper can wait for the webpage to load and respond to our program's GET request(s) before scraping and downloading data


    def load_craigslist_form_URL(self):
        """ Load the craigslist form URL, as specified in the __init__().
        Use WebDriverWait() function to ensure the web crawler will wait until the Craigslist form object with ID of "searchform" has loaded, and then download and parse the desired data.
        This function will wait up to a maximum number of seconds as designated by download_delay, otherwise a TimeOutException will trigger."""
        self.web_driver.get(self.url) # implement a GET request by loading up the customized Craigslist SF Bay Area rental listing pages via a Chrome webdriver

        # wait until the webpage's "searchform" form tag has been loaded, or up to a maximum 20 seconds (ie, given the value of self.download_delay)
        try: # wait until the form tag with ID of "searchform"--ie, the Craigslist page given our search results--has been loaded, or up to a maximum of 5 seconds (given download_delay)
            WebDriverWait(self.web_driver, self.download_delay).until(
                EC.presence_of_element_located((By.ID, "searchform"))
            )  # NB: you need to use a tuple as the argument of the selenium EC.presence_of_element_located() function, hence the double-parantheses
            print('\nPage has loaded, and the data are ready to download.\n')
        except TimeoutException:
            """ Return error message if loading the webpage takes longer than the maximum n seconds:"""
            print(f"Loading the webpage's searchform element timed out: ie, it took longer than the  maximum number of {self.download_delay} seconds designated by the download_delay.")


    def parse_html_via_xpath(self, xpath_arg: str, list_to_append: list) -> list:
        """ Scrape data from HTML element by looking up xpath (via selenium's find_element_by_xpath() method), within a try except control flow clause to account for rental listings that are missing a given HTML element.
        a.) Except if a NoSuchElementException or TimeoutException occurs--indicating a given element does not exist--then wait until given HTML element has loaded on page using WebDriverWait() method.
        b.) Then, scrape the HTML element and extract the element's text data."""
        try:
            # a.) wait until given HTML element has loaded
            wait_until = WebDriverWait(self.web_driver, self.download_delay)  # wait up to 20 seconds to let HTML element load on given rental listing webpage
            wait_until.until(EC.presence_of_element_located((By.XPATH, xpath_arg))) # a.) wait until given HTML element has loaded, or up to 20 seconds
            # b.) scrape the HTML element, extract text, and append to given list
            scraped_html = self.web_driver.find_element_by_xpath(xpath_arg)

        except (TimeoutException, NoSuchElementException) as e:
            """If the given rental listing page does not contain given element, append 'nan' value to indicate missing value."""
            return list_to_append.append('nan')  # indicate missing value

        return list_to_append.append(scraped_html.text)  # parse text data from scraped html element, and append to list for given variable of interest


    def parse_html_via_xpath_and_click(self, xpath_arg: str, list_to_append: list)-> list:
        """ Scrape data from HTML element by looking up xpath (via selenium find_element_by_xpath() method), but then click to reveal the date-time data."""
        # a.) wait until given HTML element has loaded
        try:
            wait_until = WebDriverWait(self.web_driver, self.download_delay)  # wait up to 20 seconds to let HTML element load on given rental listing webpage
            wait_until.until(EC.presence_of_element_located((By.XPATH, xpath_arg))) # a.) wait until given HTML element has loaded, or up to 20 seconds
            # b.) scrape the HTML element, extract text, and append to given list
            date_posted_click = self.web_driver.find_element_by_xpath(xpath_arg)
            # # provide delay to avoid being flagged by server as a bot, before we access each subsequent listing.
            rand_sl_time = random.randrange(2, 8) # specify a range of pseudo-random values from 2 to 8 seconds
            time.sleep(rand_sl_time)
            # click on element so that it will reveal the date-time value--ie, datetime val when the listing was posted
            self.web_driver.execute_script("arguments[0].click();", date_posted_click)  # .executescript() is a JavaScript-based selenium method that tells the webdriver to initiate a click on the given HTML element.

        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            """If the given rental listing page does not contain given element, append 'nan' value to indicate missing value."""
            return list_to_append.append('nan')  # indicate missing value

        return list_to_append.append(date_posted_click.text)  # parse text data from scraped html element, and append to list for given variable of interest


    def mk_direc_for_scraped_data(self, parent_direc: str, new_path: str) -> str:
        """Create directory (if it doesn't exist) to contain the scraped data, with separate directories for specific regions and subregions."""
        parent_direc = parent_direc  # specify the parent directory where we will create new direc
        # use f-strings to add in backslahes as directory separators
        backslashes_separator = "\\"
        # add region and sub-region names as separate child directories (with the backslashes in between to explicitly separate these as separate parent-child directories)
        new_path = f"{new_path}{backslashes_separator}{self.region}{backslashes_separator}{self.subregion}"
        path_for_csv = os.path.join(parent_direc, new_path)  # specify full path--including the new path we will create

        if not os.path.exists(path_for_csv):
            """ Create directory to contain scraped data, if path does not exist"""
            return os.makedirs(path_for_csv)

    def export_to_csv(self, df: DataFrame, parent_direc_for_csv: str) -> csv:
        """Save df as CSV in the new path, sans index. Given the mk_direc...() function,
        we will save the CSV file inside the region and subregion subdirectories
        (but only specify parent directory containing all of the scraped data).
        Append today's date and region + subregion names to CSV file name."""
        # specify preface of CSV file name
        csv_preface_name = 'craigslist_rental'
        # use f-strings to add in backslahes as directory separators
        backslashes_separator = "\\"
        # add region and subregion sub-directories to path where we will save the CSV file--NB: add in backslashes_separator to separate different sub-directories:
        path_for_csv = f"{parent_direc_for_csv}{backslashes_separator}{self.region}{backslashes_separator}{self.subregion}"

        # append today's date and the .csv extension to suffix of CSV file name
        today_dt_str = datetime.date.today().strftime("%m_%d_%Y")  # get today's date in 'mm_dd_YYYY' format
        # specify underscore -- ie, '_' --as file name separator using f-strings
        underscore_separator = '_'
        # specify CSV file suffix
        csv_suffix = '.csv'
        # add region and subregion names to CSV file, and add .csv extension:
        csv_file_name = f"{csv_preface_name}{underscore_separator}{self.region}{underscore_separator}{self.subregion}{underscore_separator}{today_dt_str}{underscore_separator}{csv_suffix}" # append today's date and .csv extension to the file name
        # export dataframe to CSV. NB: concatenate CSV file name to the path by using os.path.join(). Also, do not export index since it does not contain pertinent data
        return df.to_csv(os.path.join(path_for_csv, csv_file_name), index=False)


    def obtain_listing_data(self)-> dict:
        """Crawl over each page of rental listings, given starting URL from Craigslist_Rentals class. Obtain the URLs from each page's Craigslist rental listings. Then, parse the data of each 'inner' rental listing by accessing each of these URLs, and use xpath or class name selenium methods to scrape and parse various HTML elements (ie, the listing data that we want to scrape)."""
        #initialize empty lists that will contain the data we will scrape:
        listing_urls = []  # URLs for each rental listing
        cities = []    # city names
        prices = []    # rental prices
        ids = []     # listing IDs
        listing_descrip=[]   #  poster's text description of rental listing
        bedrooms = []    # number of bedrooms
        sqft = []    # size of rental in square feet
        bathrooms = []   # number of bathrooms
        kitchen = []   # whether listing contains kitchen
        attr_vars =[]    # str comprising various rental attributes--electric vehicle charger, etc.
        date_posted = []   # date on which listing was originally posted

        # crawl over each listings page, by looking for 'next' page buttons and clicking these after scraping the URLs of the inner listings. An exception will occur once the final page is reached since no additional 'next' page buttons will be present (and then, the webcrawler will iterate over and access each individual rental listing page)
        while True:
            try:
                """Iterate over listing URLS from each page of rental listings, given starting URL"""

                 ## scrape URLs for each rental listing on given page:
                urls = self.web_driver.find_elements_by_xpath('//a[@class="result-title hdrlnk"]')
                for url in urls:   # iterate over each rental listing's URL, and append to list
                    listing_urls.append(url.get_attribute('href'))  # extract the href (URL) data for each rental listing on given listings page


                ## Navigate to each next page, by clicking the 'next' button located at the <a> tag:
                next_page = WebDriverWait(self.web_driver, self.download_delay).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'next')]"))
                    )  # wait until 'next page' button element is clickable
                self.web_driver.execute_script("arguments[0].click();", next_page) # click to proceed to the next page--the execute_script() is a selenium method that enables us to invoke a JavaScript method and tell the webdriver to click the 'next' page button
                print("\nNavigating to the next page of rental listings\n")
                # wait n seconds before accessing the next page, but randomize the amount of time delay, in order to mimic more human-like browser activity
                rand_sl_time = random.randrange(2, 8) # specify a range of pseudo-random values from 2 to 8 seconds
                time.sleep(rand_sl_time) # wait minimum of 1 second to let the page's various HTML contents to load, before we start extracting the various data on each subsequent page.
                print(f"\nNew page's URL:\n{self.web_driver.current_url}\n\n")

            # NB: if 1 of the following 3 exceptions occur, we will stop the while loop from navigating to the next page, since the last page will have been reached
            except (TimeoutException, WebDriverException, NoSuchElementException) as e:
                """ Parse last page's data:"""
                # indicate that the last page has been reached
                print("Last page reached")

                ## scrape URLs for each rental listing on given page:
                urls = self.web_driver.find_elements_by_xpath('//a[@class="result-title hdrlnk"]')
                for url in urls:   # iterate over each listing URL on page, and extract href URL
                    listing_urls.append(url.get_attribute('href'))  # extract the href (URL) data for each rental listing on given listings page


                ## remove any duplicate listing urls by assigning it to a list of OrderedDict.fromkeys() method, which will remove duplicate elements (urls) while also retaining the order of the list's elements.
                listing_urls = list(OrderedDict.fromkeys(listing_urls))  # remove any duplicate listing urls

                ## specify amount of time delay in between GET requests--wait a minimum of 8 seconds, but randomize the amount of time delay, in order to mimic a more human-like browser activity
                rand_sl_time = random.randrange(8, 15) # specify a range of pseudo-random values

                ##  Iterate over each of the rental listing href URLs
                # N = 12   # iterate over N number of rental listing URLs

                for list_url in listing_urls:
                # for list_url in itertools.islice(listing_urls, N):    # iterate up to N listings
                        """Ie: keep iterating over each url element of rental listings until a duplicate id is iterated on, in which case we should terminate the for loop. """
                        try:
                            # access the individual rental listings via the href URLs we have parsed:
                            self.web_driver.get(list_url)

                        except (ElementClickInterceptedException, NoSuchElementException) as e:
                            """If a TimeoutException is encountered--e.g., if a rental listing posting has expired, then append 'nan' values for each list (aside from the listing_urls since this has already been populated) for that given listing, and move onto the remaining listing URLs remaining within the for loop. NB: An ElementClickInterceptedException exception occurs when the webdriver attempts to click an element that has the incorrect xpath. """
                            print(f"\n\nRental listing posting {list_url} has expired or webpage is not accessible since the webcrawler has encountered one of the following exceptions: a TimeoutException, NoSuchElementException, WebDriverException, or ElementClickInterceptedException. \n\n")
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


                        # terminate for loop if the user closes the webdriver browser--at any point of iteration--or if the internet connection is lost:
                        except (WebDriverException, TimeoutException) as e:   # ie: if webdriver connection cannot be established
                            print('\nNB: The WebDriver connection has been lost:')
                            print('TShe internet connection has been lost or WebDriver browser has been closed,\nresulting in a WebDriverException and/or TimeoutException.')
                            print('All previously scraped listings for this session will be saved and outputted to CSV.')
                            break   #  break for loop
 

                        else:
                            """Ie: Run the webcraper functions (based on xpath or class name) *if* the given rental listing URL has not been deleted--ie, if none of the 4 denoted errors are encountered. What this means in practice is that the rental listing should be still be active and not deleted. So, we can proceed with scraping the data for the various variables. The xpath or class-name parsing functions will each implement a try...except to check for a NoSuchElementException in case a given rental listing is missing data for one or more of the attributes we want to scrape. """
                            ## Scrape listing ids
                            self.parse_html_via_xpath('/html/body/section/section/section/div[2]/p[1]', ids)

                            ## Scrape rental price data
                            self.parse_html_via_xpath("/html/body/section/section/h1/span/span[1]", prices)

                            ## Scrape city names
                            self.parse_html_via_xpath("//html/body/section/section/h1/span/small", cities)

                            ##  Scrape number of bedrooms data-
                            self.parse_html_via_xpath("/html/body/section/section/h1/span/span[2]", bedrooms)

                            ##  Scrape number of bathrooms data
                            self.parse_html_via_xpath("/html/body/section/section/section/div[1]/p[1]/span[1]/b[2]", bathrooms)

                            ## Scrape sqft data:
                            self.parse_html_via_xpath('//span[@class="housing"]', sqft)

                            ## Scrape listing descriptions (so we can obtain data on attributes & amenities such as kitchen, dishwasher, and refrigerator (ie, several amenities) data):
                            self.parse_html_via_xpath('//*[@id="postingbody"]', listing_descrip)

                            # Scrape attribute data
                            self.parse_html_via_xpath("/html/body/section/section/section/div[1]/p[2]", attr_vars)

                            # Scrape the date posted data (given we have clicked the element----NB: we need to click the element so we can scrape the specific date rather than a str specifying 'x days ago')
                            self.parse_html_via_xpath_and_click("/html/body/section/section/section/div[2]/p[2]/time", date_posted)


                        finally: # move on with for loop regardless of whether any of the denoted errors has been encountered via the catch except block
                            print(f"\nListing URL being crawled on:\n  {list_url}\n\n")
                            print(f"Number of listings we have crawled over:\n{len(prices)}\n")
                            print(f"There are {len(listing_urls)-len(prices)} more listings left.")


                            # keep iterating through each URL until the listing_urls list has been crawled over fully (ie, based on the number of listing ids)
                            if len(ids) < len(listing_urls):  # If additional listings in the list have not been crawled on, then move on to the next rental listing in the listing_urls--ie, via pass command

                                    # provide delay to avoid being flagged by server as a bot, before we access each subsequent listing:
                                    time.sleep(rand_sl_time)
                                    pass # I.e.: move on to the next rental listing

                            #  Once we have iterated through each listing URL element, then immediately terminate the for loop
                            else:  
                                break

                ## Data cleaning and parsing of scraped lists-- bedroom, sqft, bathrooms, prices, etc.:

                # sqft data-- 1.) search for 'ft2' substring to indicate presence of sqft data. If this substring is found in given element, then parse the sqft data by removing the given substring and getting only the last element after splitting on whitespace so we can remove the bedroom data, which is always contained just before the sqft data. If sqft data does not exist, then return an 'nan' value instead to denote a null. When the function detects previous 'nan' values, leave unchanged as 'nan'.
                sqft = clean_scraped_sqft_data(sqft)  # parse the sqft data, and ensure it's sqft data by checking if given listing element contains the substring 'ft2'

                # bedrooms data cleaning--
                bedrooms =  clean_scraped_bedroom_data(bedrooms)

                # bathrooms data--
                bathrooms = clean_scraped_bathroom_data(bathrooms)

                # cities (ie, city names):
                cities = clean_scraped_cities_data(cities) # Remove all parantheses markings from each list element

                # prices data cleaning:
                prices = [p.lstrip("$") for p in prices]   # remove dollar signs

                # listing ids-- remove 'post id: ' prefix:
                ids = [i.lstrip('post id: ') if 'post id: ' in i else i for i in ids]  # remove 'post id: ' prefix

                ## Parse kitchen data from listing descriptions:
                kitchen = parse_kitchen_data(kitchen, listing_descrip)

                # provide date when webcrawler is run (ie, today's date when webcrawler is run), and impute these date data for *all* scraped records from the latest run of this webcrawler script  *I.e.: reference the len() of any one of the attributes that was scraped
                date_of_webcrawler = [time.strftime("%Y-%m-%d")] * len(ids)  # impute today's date to all records that we scraped from the latest run of this webcrawler script

                ## transform each list of scraped data to a dictionary of lists:
                dict_scraped_lists = {
                    'listing_urls':listing_urls, 'ids':ids, 'sqft':sqft, 'cities':cities, 'prices':prices,
                    'bedrooms':bedrooms, 'bathrooms':bathrooms, 'attr_vars':attr_vars, 'listing_descrip':listing_descrip,
                    'date_of_webcrawler':date_of_webcrawler,'kitchen':kitchen, 'date_posted':date_posted
                    }  # dictionary of the lists containing the scraped data

                # return dictionary of the lists containing the scraped data
                return dict_scraped_lists


    def dict_to_df_pipeline(self, dict_scraped_lists) -> DataFrame:
        ## Transform the dictionary of lists to Pandas' dataframe (by using dictionary comprehension)
        df_from_dict = pd.DataFrame({key:pd.Series(val) for key, val in dict_scraped_lists.items()})  #  transform dict of lists to a Pandas DataFrame--NB: transforming a dictionary of lists to a Pandas df is a bit faster than using .zip() on the untransformed lists, and then transforming to pandas df--namely: about 63% faster to use a list of dictionaries to dataframe.

        ## add name of region and subregion as new cols to df, using the parameters of the Craigslist_Rentals class
        df_from_dict['region'] = f"{self.region}"    # add craigslist region (e.g., 'sfbay') as new col
        df_from_dict['sub_region'] = f"{self.subregion}"  # add craigslist subregion (e.g., 'sby') as new col

        ## data wrangling-- parse specific attributes (e.g., 'cats_OK') from the attr_vars and listing_descrip cols as indicator variables
        parse_attrs(df_from_dict) # NB: run parse_attrs() function comprising factored-out code from imported data cleaning script--ie, parse data as indicator variables for df_from_dict DataFrame

        # clean bedrooms data for studio apt rental listings:
        df_from_dict['bedrooms'] = clean_bedroom_studio_apt_data(df_from_dict, 'listing_descrip', 'bedrooms') # clean bedrooms data

        # clean & filter listing ids--remove all rows not containing valid listing ids (ie, 'nan')
        df_from_dict = clean_listing_ids_and_remove_nan_substr(df_from_dict, 'ids', 'nan')  

        ## Final sanity check on scraped data by printing DataFrame:
        print_scraped_sanity_checks(df_from_dict)

        return df_from_dict

    def df_to_CSV_data_pipeline(self, df) -> csv:
        """Clean specific subregions' city names data, create directory for given region and subregion, and export DataFrame containing scraped data to CSV within said subregion directory"""
        ## create directory to contain scraped data (if not exists):
        self.mk_direc_for_scraped_data("D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper", "scraped_data")

        ## specify this (potentially new) path to contain the scraped data CSV files
        scraped_data_path = "D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\scraped_data"

        ## clean data for specific subregions, and export scraped data from Dataframe to CSV file:
        if self.subregion is 'sfc':  # clean San Francisco data
            """If subregion is 'sfc', transform city names data from neighborhood names to 'San Francisco', and remove any data misclassified as being within this county."""
            df = clean_city_names_for_sf(sf_neighborhoods, df) # clean scraped data if scraped from 'sfc' subregion
            self.export_to_csv(df, scraped_data_path)
            return df

        elif self.subregion is 'scz': # clean Santa Cruz data
            """If subregion is 'scz', remove any data misclassified as being within this county."""
            df = clean_mislabelled_santa_cruz_data(san_cruz_cities, df) # clean scraped data if scraped from 'scz' subregion
            self.export_to_csv(df, scraped_data_path)
            return df

        elif self.subregion is 'sby':  # clean South Bay data
            """If subregion is 'sby', clean city names data for cities such as San Jose & Santa Clara."""
            df = clean_given_city_names_data('San Jose', sj_neighborhoods, df)    # clean San Jose data
            df = clean_given_city_names_data('Santa Clara', santa_clara_neighborhoods, df)  # clean Santa Clara data
            self.export_to_csv(df, scraped_data_path)
            return df

        elif self.subregion is 'eby':  # clean East Bay data
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
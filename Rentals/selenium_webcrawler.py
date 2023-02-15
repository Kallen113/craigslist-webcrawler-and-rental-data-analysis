#import various data analysis, web scraping, and web crawling libraries--ie, pandas, various Selenium modules, etc.
#file processing lbraries (os), time (for .sleep() method), datetime, iteration, and other tools
import csv
import os
import time
import random
from collections import OrderedDict  # use to remove duplicates from rental listing urls list
import datetime

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

# pathlib library to look up whether given path exists and create path if it does not yet exist
from pathlib import Path

# import functions for cleaning misclassified data or city names data that we need to rename (e.g., for SF and  Santa Cruz counties)
# NB: since these scripts are from the same directory, we should use the '.file_name'--ie, dot prefix to specify we are importing from the same directory as this script:
from .clean_city_names import clean_city_names_for_sf, sf_neighborhoods, clean_given_city_names_data, sj_neighborhoods, oakland_neighborhoods, alameda_neighborhoods, hayward_neighborhoods, richmond_neighborhoods, santa_clara_neighborhoods  # import from same directory (ie,. dot prefix) functions to clean SF city names data and import lists of all neighborhoods for given cities--e.g., SF neighborhoods (including various abbreviations used on craigslist)
from .clean_santa_cruz_data import clean_mislabelled_santa_cruz_data, san_cruz_cities  # import from same directory (ie,. dot prefix) a function to remove rows that are misclassified as 'scz', and import list of Santa Cruz county cities

# import data cleaning script  from the data_cleaning sub-directory
from data_cleaning.scraper_and_data_cleaning_functions import clean_scraped_sqft_data, clean_scraped_bedroom_data, clean_scraped_bathroom_data, clean_scraped_cities_data, clean_scraped_date_posted_data, parse_kitchen_data, clean_listing_ids, parse_attrs, clean_bedroom_studio_apt_data, clean_listing_ids_and_remove_nan_substr, print_scraped_sanity_checks # various data cleaning and HTML-parser functions via selenium methods:


#define the Craigslist web scraper and web crawler, which we will use to scrape Craigslist SF Bay area rental listings data:
class Craigslist_Rentals(object):
    """" Define a class that will enable us to perform a customized search for rental prices--within the SF Bay area--in which
    we can perform a search for a specific region in the SF Bay area (e.g., "pen" refers to the Peninsula region), set the min & max values for the rental prices, and specify the rental period (presumably as monthly) and the sale_date, which is the date on which the apartment or home will be availabile for consumers to move into. """

    def __init__(self, region: str, subregion: str, housing_category: str, min_price: int, max_price: int, rent_period: int, sale_date: str):
        """ Define the customized URL to search for rental listings within the SF Bay Area.
        This URL will be used to implement the selenium web scraper.
        Finally, initialize a selenium webdriver for the web crawler (Chrome in our case) and set the max number of seconds we will allow as a delay in between when the GET request is sent via the web driver and the time in which the crawled webpage takes to load before starting a download for each given webpage."""
        # define various parameters for a customized craigslist rental listing URL:
        self.region = region
        self.subregion = subregion
        self.housing_category = housing_category # NB: 'apa' will search for apartments and homes for rent (the intended data for this project). Other categories on craigslist are numerous, including real estate (for sale) homes by broker or by owner, respectively, etc.
        self.min_price = min_price
        self.max_price = max_price
        self.rent_period = rent_period
        self.sale_date = sale_date

        ## Create customized URL for  specify each of the above parameters --using an f-string--to enable us to make a customized search of SF Bay Area rental listings on Craigslist
        self.url = f"https://{region}.craigslist.org/search/{subregion}/{housing_category}?/min_price={min_price}&max_price={max_price}&availabilityMode=0&rent_period={rent_period}&sale_date={sale_date}"
        
        # sanity check and print the starting craigslist URL for the web crawler (ie, the self.url derived from this __init__() method):
        print(f"The craigslist URL we will use to perform the web crawler is:\n{self.url}")

        ## Initialize a Webdriver for selenium to implement the webcrawler:
        # driver_path = r"C:\webdrivers\chromedriver_win32.exe\chromedriver.exe" #specify path to webdriver

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

        self.download_delay = 50   # set maximum download delay of 50 seconds, so the web scraper can wait for the webpage to load and respond to our program's GET request(s) before scraping and downloading data


    def load_craigslist_form_URL(self):
        """ Load the craigslist form URL, as specified in the __init__().
        Use WebDriverWait() function to ensure the web crawler will wait until the Craigslist form object with ID of "searchform" has loaded, and then download and parse the desired data.
        This function will wait up to a maximum number of seconds as designated by download_delay, otherwise a TimeOutException will trigger."""
        self.web_driver.get(self.url) # implement a GET request by loading up the customized Craigslist SF Bay Area rental listing pages via a Chrome webdriver

        # wait until the webpage's "searchform" form tag has been loaded, or up to a maximum 20 seconds (ie, given the value of self.download_delay)
        try: # wait until the form tag with ID of "searchform"--ie, the Craigslist page given our search results--has been loaded, or up to a maximum of 50 seconds (given download_delay)
            WebDriverWait(self.web_driver, self.download_delay).until(
                EC.presence_of_element_located((By.ID, "searchform"))
            )  # NB: you need to use a tuple as the argument of the selenium EC.presence_of_element_located() function, hence the double-parantheses
            print('\nPage has loaded, and we can start scraping the data.\n')
        except TimeoutException:
            # Return error message if loading the webpage takes longer than the maximum n seconds
            print(f"\nLoading the webpage's searchform element timed out: ie, it took longer than the maximum number of {self.download_delay} seconds designated by the download_delay argument.\n")


    def parse_html_via_xpath(self, xpath_arg: str, list_to_append: list) -> list:
        """ Scrape data from HTML element by looking up xpath (via selenium's find_element("xpath") method), within a try except control flow clause to account for rental listings that are missing a given HTML element.
        a.) Except if a NoSuchElementException, TimeoutException, or if a WebDriverException occurs --indicating a given element does not exist or the WebDriver connection has been lost--add an 'nan' value indicating missing data.
        b.) If no exceptions are encountered, scrape (return) the HTML element and extract the element's text data."""
        try:
            # a.) wait until given HTML element has loaded
            wait_until = WebDriverWait(self.web_driver, self.download_delay)  # wait up to 50 seconds to let HTML element load on given rental listing webpage
            wait_until.until(EC.presence_of_element_located((By.XPATH, xpath_arg))) # a.) wait until given HTML element has loaded, or up to 50 seconds
            # b.) scrape the HTML element, extract text, and append to given list
            scraped_html = self.web_driver.find_element("xpath", xpath_arg)

        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            """If the given rental listing page does not contain given element, append 'nan' value to indicate missing value."""
            return list_to_append.append('nan')  # indicate missing value
        
        # parse scraped data's text if no exception is encountered:
        return list_to_append.append(scraped_html.text)  # parse text data from scraped html element, and append to list for given variable of interest

    def parse_html_via_xpath_get_datetime_attr(self, xpath_arg: str, list_to_append: list) -> list:
        """ Scrape data from HTML element by looking up xpath (via selenium's find_element("xpath") method), within a try except control flow clause to account for rental listings that are missing a given HTML element.
        a.) Except if a NoSuchElementException, TimeoutException, or if a WebDriverException occurs --indicating a given element does not exist or the WebDriver connection has been lost--add an 'nan' value indicating missing data.
        b.) If no exceptions are encountered, scrape (return) the HTML element and extract the element's datetime attribute, which comprises a listing's date posted data."""
        try:
            # a.) wait until given HTML element has loaded
            wait_until = WebDriverWait(self.web_driver, self.download_delay)  # wait up to 50 seconds to let HTML element load on given rental listing webpage
            wait_until.until(EC.presence_of_element_located((By.XPATH, xpath_arg))) # a.) wait until given HTML element has loaded, or up to 50 seconds
            # b.) scrape the HTML element, extract text, and append to given list
            scraped_html = self.web_driver.find_element("xpath", xpath_arg)

        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            """If the given rental listing page does not contain given element, append 'nan' value to indicate missing value."""
            return list_to_append.append('nan')  # indicate missing value
        
        # parse scraped data's datetime attribute if no exception is encountered:
        return list_to_append.append(scraped_html.get_attribute('datetime'))  # parse datetime attribute data from scraped html element, and append to list for given variable of interest


    def obtain_listing_urls(self, xpaths_listing_urls,  xpaths_next_page_button)-> list:
        """Crawl over each page of rental listings, given starting URL from Craigslist_Rentals class. Obtain the URLs from each page's Craigslist rental listings. Then, parse the data of each 'inner' rental listing by accessing each of these URLs, and use xpath or class name selenium methods to scrape and parse various HTML elements (ie, the listing data that we want to scrape). 
        Takes in 2 arguments: 
        a) xpaths_listing_urls: xpaths for inner listing page URLs (hrefs) 
        &
        b) xpaths_next_page_button: xpaths for the next page button widget (ie, we need to click these to nagivate to subsequent pages of listings) .
        Finally: Return the listing urls as a list."""
        
        #initialize empty lists that will contain the data we will scrape:
        listing_urls = []  # URLs for each rental listing
        
        # crawl over each page of listings, by looking for 'next' page buttons and clicking these after scraping the URLs of the inner listings. An exception will occur once the final page is reached since no additional 'next' page buttons will be present (and then, the webcrawler will iterate over and access each individual rental listing page)

        while True:

            # # wait until first inner listing's href has been loaded on given page; account for *both* xpath variants that exist on the various craigslist region domains (by using pipe "or" operator)            
            # wait_until = WebDriverWait(self.web_driver, self.download_delay)  # wait up to 50 seconds to let HTML element load on given rental listing webpage
            # wait_until.until(EC.presence_of_element_located((By.XPATH, xpaths_listing_urls))) # wait until given HTML element has loaded, or up to 50 seconds

            # scrape the HTML element, extract text, and append to list 

            # specify xpath to inner listings' data (which includes href URLs); use pipe "or" operator to account for both xpath variants  
            urls = self.web_driver.find_elements("xpath", xpaths_listing_urls)
            
           
            # iterate over each rental listing's URL, extract hrefs, and append to list  
            for url in urls:   
                listing_urls.append(url.get_attribute('href'))  # extract the href (URL) data for each rental listing on given listings page

            ## Navigate to each next page, collecting each rental listings' urls from each given page:

            ## Check that there are no duplicate urls in listing_urls (ie, url hrefs for the inner rental listings pages):
            if len(listing_urls) == len(set(listing_urls)):  # check that there are no duplicate urls in urls list (ie, url hrefs for the rental listings pages)
                
                try:

                    ## Navigate to each next page, by clicking the 'next page' button (NB: different craigslist regions have one of *two* different xpaths to this button):

                    ## Specify xpath for next page link button; use pipe "or" operator to account for both xpath variants  
                    next_page = self.web_driver.find_element("xpath", xpaths_next_page_button)     # the 1st xpath's class name will remain the same until last page of listings; the 2nd xpath stays same throughout each page...
                    
                    # click to proceed to the next page--the execute_script() is a selenium method that enables us to invoke a JavaScript method and tell the webdriver to click the 'next' page button
                    self.web_driver.execute_script("arguments[0].click();", next_page) 
                    print("\nNavigating to the next page of rental listings\n")

                    # wait n seconds before accessing the next page, but randomize the amount of time delay, in order to mimic more human-like browser activity
                    rand_sl_time = random.randrange(1, 3) # specify a range of pseudo-random values from 1 to 3 seconds
                    time.sleep(rand_sl_time) # wait minimum of 1 second to let the page's various HTML contents to load, before we start extracting the various data on each subsequent page.
                    print(f"\nURL of new page:\n{self.web_driver.current_url}\n\n")

                ## account for newer next page button UI (ie, differing xpath) by checking for final page, in which next page button element no longer exists (and is greyed out)
                except (NoSuchElementException, ElementClickInterceptedException) as e:
                    # indicate that the last page has been reached
                    print("\n**Last page reached**\n")
                    
                    ## scrape URLs for each rental listing on final page (accoutn for both xpath variants using pipe "or" operator)

                    # wait_until = WebDriverWait(self.web_driver, self.download_delay)  # wait up to 50 seconds to let HTML element load on given rental listing webpage
                    # wait_until.until(EC.presence_of_element_located((By.XPATH, xpaths_listing_urls))) # wait until given HTML element has loaded, or up to 50 seconds

            
                    # specify url xpath; account for both xpath variants using pipe "or" operator
                    urls = self.web_driver.find_elements("xpath", xpaths_listing_urls)
                    
                    for url in urls:   # iterate over each listing URL on page, and extract href URL
                        listing_urls.append(url.get_attribute('href'))  # extract the href (URL) data for each rental listing on given listings page


                    # ## remove any duplicate listing urls by assigning it to a list of OrderedDict.fromkeys() method, which will remove duplicate elements (urls) while also retaining the order of the list's elements.
                    listing_urls = list(OrderedDict.fromkeys(listing_urls))  # remove any duplicate listing urls

                
                    # sanity check on scraped urls:
                    print(f'The total number of scraped rental listing urls are:{len(listing_urls)}\n')
                    
                    # return list of rental listing urls
                    return listing_urls

        
            ## The last page has been reached since there *are* duplicate urls that have been scraped/encountered by the webcrawler 
            else:

                """ Parse last page's data:"""
                
                # indicate that the last page has been reached
                print("\nLast page reached\n")
                
                ## scrape URLs for each rental listing on final page (accoutn for both xpath variants using pipe "or" operator)
                # xpath_first_listing_url_on_page = '//*[@id="search-results-page-1"]/ol/li[1]/div/a[2] | //*[@id="search-results"]/li[1]/div'  # xpath to 1st inner listing hrefs on page
                # '//*[@id="search-results-page-1"]/ol/li[1]/div/a[2] | //*[@id="search-results"]/li[1]/div'

                # wait_until = WebDriverWait(self.web_driver, self.download_delay)  # wait up to 50 seconds to let HTML element load on given rental listing webpage
                # wait_until.until(EC.presence_of_element_located((By.XPATH, xpath_first_listing_url_on_page))) # wait until given HTML element has loaded, or up to 50 seconds

           
                # specify url xpath; account for both xpath variants using pipe "or" operator
                urls = self.web_driver.find_elements("xpath", xpaths_listing_urls)
                
                
                for url in urls:   # iterate over each listing URL on page, and extract href URL
                    listing_urls.append(url.get_attribute('href'))  # extract the href (URL) data for each rental listing on given listings page


                # ## remove any duplicate listing urls by assigning it to a list of OrderedDict.fromkeys() method, which will remove duplicate elements (urls) while also retaining the order of the list's elements.
                listing_urls = list(OrderedDict.fromkeys(listing_urls))  # remove any duplicate listing urls

                
                # sanity check on scraped urls:
                print(f'The total number of scraped rental listing urls are:{len(listing_urls)}\n')

                # return list of rental listing urls
                return listing_urls

                

    def scrape_listing_data(self, listing_urls:list)->dict:
        """Itereate over each inner listing page and scrape data on various attributes such as city names and rental prices. 
        Return the various lists as a dictionary of lists."""
        #initialize empty lists that will contain the data we will scrape:
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

        ## specify amount of time delay in between GET requests--wait a minimum of 2 seconds, but randomize the amount of time delay, in order to mimic a more human-like browser activity
        rand_sl_time = random.randrange(2, 5) # specify a range of pseudo-random values


        ##  Iterate over each of the rental listing href URLs
        for list_url in listing_urls:
            """Ie: keep iterating over each url element of rental listings until a duplicate id is iterated on, in which case we should terminate the for loop. """
            try:
                # access the individual rental listings via the href URLs we have parsed:
                self.web_driver.get(list_url)

                ## Attempt to click and scrape data re: date when the listing was posted (ie, date_posted)  
                try:
                    # Click and then scrape the date posted data--NB: we need to click the element so we can scrape the specific date rather than a str specifying 'x days ago':
                    self.parse_html_via_xpath_get_datetime_attr('//time[@class="date timeago"]', date_posted)


                ## Append 'nan' vals if the date_posted has not been clicked (allow user to exit webcrawler program and output available data to CSV) or if any of the data we are trying to scrape are missing on given rental listing page:

                ## Account for situations in which listings have been deleted or expired while the script has been running. 
                ## Also, enable user to exit webcrawler program before a given listing's date_posted data has been clicked:
                except (ElementClickInterceptedException, NoSuchElementException) as e:

                    """If an ElementClickInterceptedException or NoSuchElementException is encountered--e.g., if a rental listing posting has expired or if the user exits the webdriver before date_posted can be clicked, then append 'nan' values for each list (aside from the listing_urls since this has already been populated) for that given listing, and move onto the remaining listing URLs remaining within the for loop. NB: An ElementClickInterceptedException exception occurs when the webdriver attempts to click an element that has the incorrect xpath. """
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
                    ## continue iterating (outer for loop) to next rental page from  listing_urls list:
                    continue


            # terminate for loop if the user closes the webdriver browser--at any point of iteration--or if the internet connection is lost:                                    
            except (WebDriverException, TimeoutException, KeyboardInterrupt) as e:   # ie: if webdriver connection cannot be established or has been lost, or if user interrupts script via Keyboard interrupt
                print('\n\nNB: The WebDriver connection has been lost:\n')

                print('The WebDriver browser has been closed, the internet connection has been lost, or a keyboard interrupt has occurred\nresulting in a WebDriverException, TimeoutException, or KeyboardInterrupt.')
                print('\nAll previously scraped listings for this session will be saved and outputted to CSV.')
                break   #  break for loop, and proceed to data transformation, cleaning and data pipelines

            # scrape data (given none of the above exceptions are encountered)
            else:
                """Ie: Run the webcraper functions (based on xpath or class name) *if* the given rental listing URL has not been deleted--ie, if none of the 4 denoted errors are encountered. What this means in practice is that the rental listing should be still be active and not deleted. So, we can proceed with scraping the data for the various variables. The xpath or class-name parsing functions will each implement a try...except to check for a NoSuchElementException in case a given rental listing is missing data for one or more of the attributes we want to scrape. """
                ## Scrape listing ids
                self.parse_html_via_xpath('/html/body/section/section/section/div[2]/p[1]', ids)

                ## Scrape rental price data
                self.parse_html_via_xpath('//span[@class="price"]', prices)


                ## Scrape city names
                self.parse_html_via_xpath("/html/body/section/section/h1/span/span[4]", cities)
                
                ##  Scrape number of bedrooms data-
                self.parse_html_via_xpath('//span[@class="shared-line-bubble"]', bedrooms)


                ##  Scrape number of bathrooms data
                self.parse_html_via_xpath('//span[@class="shared-line-bubble"]', bathrooms)


                ## Scrape sqft data:
                self.parse_html_via_xpath('//span[@class="housing"]', sqft)


                ## Scrape listing descriptions (so we can obtain data on attributes & amenities such as kitchen, dishwasher, and refrigerator (ie, several amenities) data):
                self.parse_html_via_xpath('//*[@id="postingbody"]', listing_descrip)

                ## Scrape attribute data:
                self.parse_html_via_xpath('//p[@class="attrgroup"][last()]', attr_vars)  # the attributes are always the *last* p tag with a class name of "attrgroup" (the number of such p tags differs, ranging from 2-3 typically) 


            ## Aside from a WebDriverException or TimeoutException error, move on with for loop until all urls have been iterated over
            finally: 

                ## keep iterating through each URL until the listing_urls list has been crawled over fully (ie, based on the number of listing ids)
                if len(ids) < len(listing_urls):  # If additional listings in the list have not been crawled on, then move on to the next rental listing in the listing_urls--ie, via pass command

                    ## print some webcrawler progress diagnostics--such as the number of listings accessed--in CLI: 
                    print(f"\nNumber of listings we have crawled over:\n{len(ids)}\n")
                    print(f"There are {len(listing_urls)-len(ids)} more listings left.")

                    ## provide delay in b/w GET requests to avoid being flagged by server as a bot: ie, before we access each subsequent listing:
                    time.sleep(rand_sl_time)
                    ## Access the next rental listing URL (ie, do GET request)
                    pass 

                #  Once we have iterated through each listing URL, terminate the loop
                else:  
                    break
    

        ## Create column to have data showing the date on which the webcrawler module was executed:

        # provide date when webcrawler is run (ie, today's date when webcrawler is run), and impute these date data for *all* scraped records from the latest run of this webcrawler script  *I.e.: reference the len() of any one of the attributes that was scraped
        date_of_webcrawler = [time.strftime("%Y-%m-%d")] * len(ids)  # impute today's date to all records that we scraped from the latest run of this webcrawler script


        ## Transform each list of scraped data to a dictionary of lists:
        dict_scraped_lists = {
            'listing_urls':listing_urls, 'ids':ids, 'sqft':sqft, 'cities':cities, 'prices':prices,
            'bedrooms':bedrooms, 'bathrooms':bathrooms, 'attr_vars':attr_vars, 'listing_descrip':listing_descrip,
            'date_of_webcrawler':date_of_webcrawler,'kitchen':kitchen, 'date_posted':date_posted
            }  # dictionary of the lists containing the scraped data

        # return dictionary of the lists containing the scraped data
        return dict_scraped_lists


    def clean_scraped_data(self, dict_scraped_lists:dict)->dict:
        """Do some data cleaning and wrangling of specific lists (ie, attributes) within the scraped data dictionary of lists"""


        ## Clean and parse city names, ids, kitchen, sqft, bedrooms, and other attributes within the dictionary of lists:

        # clean city names data (cities)--clean names to upper-case and remove parantheses markings from each element
        dict_scraped_lists['cities'] = clean_scraped_cities_data(dict_scraped_lists, 'cities')

        # listing ids-- remove 'post id: ' prefix:
        dict_scraped_lists['ids'] = clean_listing_ids(dict_scraped_lists, 'ids')

        ## Parse kitchen data from listing descriptions:
        dict_scraped_lists['kitchen'] = parse_kitchen_data(dict_scraped_lists, 'listing_descrip')

        # clean the sqft data, and ensure it's sqft data by checking if given listing element contains the substring 'ft2'
        dict_scraped_lists['sqft'] = clean_scraped_sqft_data(dict_scraped_lists)  

        # bedrooms data 
        dict_scraped_lists['bedrooms'] =  clean_scraped_bedroom_data(dict_scraped_lists)

        # bathrooms data
        dict_scraped_lists['bathrooms'] = clean_scraped_bathroom_data(dict_scraped_lists)

        # clean the date_posted data to remove and replace the "T" char
        dict_scraped_lists['date_posted'] = clean_scraped_date_posted_data(dict_scraped_lists)

        return dict_scraped_lists




    def dict_to_df_pipeline(self, dict_scraped_lists:dict) -> DataFrame:
        """Transform scraped data from dictionary of lists to a Pandas' DataFrame, and perform additional data cleaning and parsing"""
        ## Transform the dictionary of lists to Pandas' dataframe (by using dictionary comprehension):
        df_from_dict = pd.DataFrame({key:pd.Series(val) for key, val in dict_scraped_lists.items()})  #  transform dict of lists to a Pandas DataFrame--NB: transforming a dictionary of lists to a Pandas df is a bit faster than using .zip() on the untransformed lists, and then transforming to pandas df--namely: about 63% faster to use a list of dictionaries to dataframe.

        ## Data cleaning and wrangling:
        
        # remove dollar signs for rental prices data
        df_from_dict['prices'] = df_from_dict['prices'].str.replace(
            '$', '', regex=True
            )   

        # parse specific attributes (e.g., 'cats_OK') from the attr_vars and listing_descrip cols as indicator variables:
        parse_attrs(df_from_dict) # NB: run parse_attrs() function comprising factored-out code from imported data cleaning script--ie, parse data as indicator variables for df_from_dict DataFrame

        # clean bedrooms data for studio apt rental listings:
        df_from_dict['bedrooms'] = clean_bedroom_studio_apt_data(df_from_dict, 'listing_descrip', 'bedrooms') # clean bedrooms data

        # clean & filter listing ids--remove all rows not containing valid listing ids (ie, 'nan')
        df_from_dict = clean_listing_ids_and_remove_nan_substr(df_from_dict, 'ids', 'nan')  


        ## add name of region and subregion as new cols to df, using the parameters of the Craigslist_Rentals class
        df_from_dict['region'] = f"{self.region}"    # add craigslist region (e.g., 'sfbay') as new col
        df_from_dict['sub_region'] = f"{self.subregion}"  # add craigslist subregion (e.g., 'sby') as new col

        
        ## Final sanity check on scraped data by printing DataFrame:
        print_scraped_sanity_checks(df_from_dict)

        return df_from_dict

    ## Define 2 additional methods that will be called upon or used as arguments (as specified within the main.py executable) by the df_to_CSV_data_pipeline() method:
    
    # make directory to contain scraped data if it does not yet exist:
    def mk_direc_for_scraped_data(self, parent_direc: str, scraped_data_folder: str) -> str:
        """Create directory (if it doesn't exist) to contain the scraped data, with separate directories for specific regions and subregions."""
        # use f-strings to add in backslahes as directory separators
        backslashes_separator = "\\"
        # add region and sub-region names as separate child directories (with the backslashes in between to explicitly separate these as separate parent-child directories)
        new_path = f"{scraped_data_folder}{backslashes_separator}{self.region}{backslashes_separator}{self.subregion}"
        path_for_csv = os.path.join(parent_direc, new_path)  # specify full path--including the new path we will create (if path does not yet exist)

        scraped_data_path = Path(path_for_csv)

        ## Create directory to contain scraped data (if path does not exists):
        scraped_data_path.mkdir(
        parents=True,  # look through parent directories
        exist_ok=True    # create directory *only* if it does *not* already exist
        )
        
        ## Finally, return the path to the scraped data (where the data pipeline will write/save the outputted CSV file)
        return scraped_data_path


    # export CSV given directory that exists or has been crated via the mk_direc_for_scraped_data() method:
    def export_to_csv(self, df: DataFrame, scraped_data_path: str) -> csv:
        """Save df as CSV in the new path, sans index. Given the mk_direc_for_scraped_data() function,
        we will save the CSV file inside the region and subregion subdirectories.
        Append today's date and region + subregion names to CSV file name."""
        # specify preface of CSV file name
        csv_preface_name = 'craigslist_rental'

        # append today's date and the .csv extension to suffix of CSV file name
        today_dt_str = datetime.date.today().strftime("%m_%d_%Y")  # get today's date in 'mm_dd_YYYY' format
        # specify underscore -- ie, '_' --as file name separator using f-strings
        underscore_separator = '_'
        # specify CSV file suffix
        csv_suffix = '.csv'
        # add region and subregion names to CSV file, and add .csv extension:
        csv_file_name = f"{csv_preface_name}{underscore_separator}{self.region}{underscore_separator}{self.subregion}{underscore_separator}{today_dt_str}{underscore_separator}{csv_suffix}" # append today's date and .csv extension to the file name
        # export dataframe to CSV. NB: concatenate CSV file name to the path by using os.path.join(). Also, do not export index since it does not contain pertinent data:
        return df.to_csv(os.path.join(scraped_data_path, csv_file_name), index=False)


    def df_to_CSV_data_pipeline(self, df: DataFrame,  scraped_data_path: str) -> csv:
        """Clean specific subregions' city names data, create directory for given region and subregion, and export DataFrame containing scraped data to CSV within said subregion directory"""
    
        ## clean data for specific subregions, and export scraped data from Dataframe to CSV file:
        if self.subregion is 'sfc':  # clean San Francisco data
            """If subregion is 'sfc', transform city names data from neighborhood names to 'San Francisco', and remove any data misclassified as being within this county."""
            df = clean_city_names_for_sf(sf_neighborhoods, df) 
            return self.export_to_csv(df, scraped_data_path)

        elif self.subregion is 'scz': # clean Santa Cruz data
            """If subregion is 'scz', remove any data misclassified as being within this county."""
            df = clean_mislabelled_santa_cruz_data(san_cruz_cities, df) # clean 'scz' subregion data
            return self.export_to_csv(df, scraped_data_path)
            
        elif self.subregion is 'sby':  # clean South Bay data
            """If subregion is 'sby', clean city names data for cities such as San Jose & Santa Clara."""
            df = clean_given_city_names_data('San Jose', sj_neighborhoods, df)    # clean San Jose data
            df = clean_given_city_names_data('Santa Clara', santa_clara_neighborhoods, df)  # clean Santa Clara data
            return self.export_to_csv(df, scraped_data_path)

        elif self.subregion is 'eby':  # clean East Bay data
            """If subregion is 'eby', clean city names data for cities such as Oakland & Hayward."""
            df = clean_given_city_names_data('Oakland', oakland_neighborhoods, df) # clean Oakland data
            df = clean_given_city_names_data('Hayward', hayward_neighborhoods, df)  # clean Hayward data
            df = clean_given_city_names_data('Alameda', alameda_neighborhoods, df)  # clean Alameda data
            df = clean_given_city_names_data('Richmond', richmond_neighborhoods, df)  # clean Richmond data
            return self.export_to_csv(df, scraped_data_path)
            
        else:
            """Ie: do not perform any additional data cleaning if subregion is not SF, Santa Cruz, South Bay, or East Bay"""
            return self.export_to_csv(df, scraped_data_path)

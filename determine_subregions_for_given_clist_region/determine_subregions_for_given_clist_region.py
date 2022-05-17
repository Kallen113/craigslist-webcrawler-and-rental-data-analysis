"""This script will parse the names of the subregions within a
given craiglist metropolitan/large city region (ie, sfbay, Chicago,  San Diego, etc.).

NB: We need to a priori know the URL to the craigslist homepage
of the given region. 
For ex: <https://sandiego.craigslist.org/> is the homepage for craglist San Diego."""

#file processing libraries (os), time (for .sleep() method), datetime, iteration, and other tools
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

# inquirer library to add dropdowns and parse user input in terminal/command-line
import inquirer

# # import functions to delineate & parse SF Bay subregions:
from .sfbay_craigslist_subregion_definitions import print_sfbay_subregion_names, inquirer_prompt_user_at_terminal

def parse_subregions_via_xpath(craigslist_url_homepage: str, xpath_arg: str)->list:
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
        print(f"\n\nLoading the webpage's searchform element timed out: ie, it took longer than the  maximum number of {download_delay} seconds designated by the download_delay.")

    # initialize empty list to contain the names of subregions
    craigslist_subregions = []  

    # b.) scrape the HTML element, extract text, and append to given list
    for scraped_html in web_driver.find_elements_by_xpath(xpath_arg):
        craigslist_subregions.append(scraped_html.text)  # parse text data from scraped html element

    
    # close the WebDriver browser, since we are done using it
    web_driver.close()

    # separate each subregion code by separating each backslash 'delimiter', using .split() via list comp:
    craigslist_subregions = [val.split() for val in craigslist_subregions]  # separate each str element by backslash delimiter using .split() method

    # NB: .split() causes the list to become a list of lists, so we need to flatten the list:

    # flatten the list by looping over each sublist in list of lists and using .extend() method on each 'sublist'
    flatten_lis = []  
    for sublist in craigslist_subregions:  # iterate over each element in list
        flatten_lis.extend(sublist)   # flatten list via .extend() method

    # assign the flattened list back to original list:
    craigslist_subregions = list(flatten_lis) 

    # return scraped data as list of subregion codes:
    return craigslist_subregions


# enable user to select the craigslist region--ie, the parent regions--from dropdown list--in terminal/CLI--to implement the webcrawler on, before prompting user to select subregions (ie, child regions for given craigslist region)
def prompt_user_for_region_and_return_region_name(region_vals:dict):
    """Prompt user at command line terminal to select one of the metropolitan regions from a dropdown of region names (parsed from inputted dictionary).
    Then, return the region URL & the craigslist URL corresponding to the selected region. """
    ## NB: the main() function needs to supply a list of the region names--ie, region_vals argument
    regions_lis = [
        inquirer.List('clist_region',
        message="What craigslist region would you like to scrape--NB: please select from the dropdown values?",
        choices= region_vals,  # input the various subregions as the elements for the user to select from this list.
        carousel=True  # allow user to scroll through list of values more seamlessly
        ),
        ]
    region = inquirer.prompt(regions_lis) # prompt user to select one of the regions in command line, from the dropdown list defined above
    region = region["clist_region"]

    # sanity check:
    # ensure correct region is being selected/parsed 
    print(f'The region you selected is:{region}\n\n')

    
    # return the region name & the URL corresponding to the selected region:
    return region   # NB: we need to return the region, but we also need the URL--ie, the dict value-- of the given region name (ie, key) instead!

def return_hompeage_URL_for_given_region(region_vals:dict, region_name: str):
    """Given the region the user selects via terminal, return the corresponding region's hompeage URL for craigslist."""
    # sanity check
    # ensure correct URL is being selected for given user selection of region (ie, key) of dict:
    print(f'The craigslist URL for {region_name} is:\n{region_vals.get(region_name)}\n')

    print(f'Data type of region_vals object val--ie, URL--is:{type(region_vals.get(region_name))}')

    return region_vals.get(region_name) 

def parse_region_code_for_craigslist_URL_main_webcrawler(region_URL):
    """From the region_URL--which is given by the user's selection of the region_name, use .split() method to parse the region code for the given URL, which we will supply as an arg to the Craigslist_Rentals class's init() method, from the selenium_webcrawler.py (ie, the main webcrawler script!!)."""
    return region_URL.split('//')[1].split('.')[0]

# enable user to select subregion from dropdown to implement the webcrawler on:
def prompt_user_for_subregion(subregion_vals):
    subregions_lis = [
        inquirer.List('clist_subregion',
        message="What craigslist sub-region would you like to scrape--NB: please select from the dropdown values?",
        choices=subregion_vals,  # input the various subregions as the elements for the user to select from this list
        carousel=True  # allow user to scroll through list of values more seamlessly
        ),
        ]
    subregion = inquirer.prompt(subregions_lis) # prompt user to select one of the subregions in command line
    subregion = subregion["clist_subregion"]
    return subregion


def main():
    #specify names of regions and their corresponding craigslist urls, store in dict
    clist_region_and_urls = {
        'SF Bay Area, CA':'https://sfbay.craigslist.org/',
        'San Diego, CA':'https://sandiego.craigslist.org/',
        'Chicago, IL':'https://chicago.craigslist.org/',
        'Seattle, WA':'https://seattle.craigslist.org/',
        'Tacoma, WA':'https://seattle.craigslist.org/tac/',
        'Los Angeles, CA':'https://losangeles.craigslist.org/',
        'Phoenix, AZ':'https://phoenix.craigslist.org/',
        'Portland, OR':'https://portland.craigslist.org/',
        'Dallas/Fort Worth, TX':'https://dallas.craigslist.org/',
        'Minneapolis/St. Paul, MN':'https://minneapolis.craigslist.org/',
        'Boston, MA':'https://boston.craigslist.org/',
        'Washington, D.C.':'https://washingtondc.craigslist.org/',
        'Atlanta, GA':'https://atlanta.craigslist.org/',
        'Miami, FL':'https://miami.craigslist.org/',
        'Hawaii (subregions by island)':'https://honolulu.craigslist.org/',
        'Detroit, MI':'https://detroit.craigslist.org/',
        'New York City, NY':'https://newyork.craigslist.org/',
        'Vancouver, Canada':'https://vancouver.craigslist.org/',
        'Toronto, Canada':'https://toronto.craigslist.org/'
        }
    

    # prompt user at terminal/CLI to select one of the listed craigslist regions:
    region_name  = prompt_user_for_region_and_return_region_name(clist_region_and_urls)

    # return the corresponding craigslist hompage URL for the seleected region:
    region_URL = return_hompeage_URL_for_given_region(clist_region_and_urls, region_name)

    # Next, parse clist subregion (if needed):

    if region_name != 'SF Bay Area, CA': # ie, if region is *not*  SF Bay Area, CA

        # run parse_subregions_via_xpath() function to parse craigslist subregion codes

        # specify xpath argument needed to parse the clist subregion codes for a given (parent) region 
        ul_subregions_xpath = '//*[@id="topban"]/div[1]/ul'

        # run parse_subregions_via_xpath() to parse subregion codes into a list, given the following args: region URLs list (ie, clist_region_urls), an empty list to be populated, and an xpath arg
        subregions_list = parse_subregions_via_xpath(region_URL, ul_subregions_xpath)

        # sanity check on list of subregions
        print(f'Subregion vals for given region:\n{subregions_list}\n')

        # select subregion val: ie, prompt user in terminal to select one of the subregions from the subregions_list:
        subregion = prompt_user_for_subregion(subregions_list)  # select a subregion from the list of parsed subregion codes, and parse the value selected

        # sanity check
        print(f'Subregion selected:\n{subregion}')
    
    else:   # ie, user chose SF Bay Area, CA region
        print_sfbay_subregion_names() # print what each sfbay craglslist subregion actually represents--ie, which regions and/or cities. 
        ## specify each Sf Bay subregion:
        sfbay_subregion_vals = ['eby', 'nby', 'pen', 'sby', 'scz', 'sfc'] # specify a list of all Bay Area subregions for craigslist site-- NB: craigslist lumps Santa Cruz ('scz') within their sfbay site.  
        # select subregion val: ie, prompt user in terminal to select one of the subregions:
        subregion = inquirer_prompt_user_at_terminal(sfbay_subregion_vals)  # parse the specific value the user selected  

        # sanity check
        print(f'Subregion value selected:\n{subregion}')


if __name__=="__main__":
    main()
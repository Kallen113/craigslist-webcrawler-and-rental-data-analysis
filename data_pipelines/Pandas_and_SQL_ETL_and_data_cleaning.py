# imports-- file processing & datetime libraries
import os
import glob
from pathlib import Path
import datetime
from dateutil.parser import parse

# data analysis libraries & SQL libraries
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
# SQL ODBC for API connection between Python & SQL Server
import pyodbc
# use json library to open a json file, which contains SQL credentials & configuration--ie, username, password, etc.
import json 
# inquirer library to prompt user for region:
import inquirer

#web crawling, web scraping & webdriver libraries and modules
from selenium import webdriver  # NB: this is the main module we will use to implement the webcrawler and webscraping. A webdriver is an automated browser.
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options  # Options enables us to tell Selenium to open WebDriver browsers using maximized mode, and we can also disable any extensions or infobars

import requests

## Data pipeline of Pandas' df to SQL Server -- import scraped craigslist rental listings data from CSV files to single Pandas' df: 

# 1) Prompt user to select region in which update database via newest scraped data , and then import all scraped data for given region

# 1a) prompt user--via terminal-- to specify which region to update database via newest scraped data 
def prompt_user_to_specify_region_to_update(region_codes):
    regions_lis = [
        inquirer.List('clist_region',
        message="What craigslist region would you like to use to update the database--NB: please select from the dropdown values?",
        choices= region_codes,  # input the various subregions as the elements for the user to select from this list.
        carousel=True  # allow user to scroll through list of values more seamlessly
        ),
        ]
    region = inquirer.prompt(regions_lis) # prompt user to select one of the regions in command line, from the dropdown list defined above
    region = region["clist_region"]

    # print the region code that was selected
    print(f'The region you selected is:\n{region}\n')

    # return the region name & the URL corresponding to the selected region:
    return region   # NB: we need to return the region, but we also need the URL--ie, the dict value-- of the given region name (ie, key) instead!

def return_hompeage_URL_for_given_region(region_vals:dict, region_name: str):
    """Given the region the user selects via terminal, return the corresponding region's hompeage URL for craigslist."""
    # return the value of the corresponding key--ie, return the URL for the given region
    return region_vals.get(region_name)  # return URL for given region

# 1b) Parse region code from user's region selection
def parse_region_code_from_craigslist_URL(region_URL):
    """From the region_URL--which is given by the user's selection of the region_name, use .split() method to parse the region code for the given URL, which we will supply as an arg to the Craigslist_Rentals class's init() method, from the selenium_webcrawler.py (ie, the main webcrawler script!!)."""
    return region_URL.split('//')[1].split('.')[0]

# 1bi) Check whether there is any scraped data saved for given (user-selected) region
def check_data_exists_for_given_region(parent_direc:str, region_code: str):
    # specify parent path of directories containing the scraped rental listings CSV data -- NB: use raw text--as in r'path...', or can we use the double-back slashes to escape back-slashes??
    path =  parent_direc 
    # use backslashes to separate the parent direc from the region code
    backslashes_separator = "\\\\"
    # add *region code* to parent direc so we can recursively search the scraped data for that specific region:
    path = f'{path}{backslashes_separator}{region_code}' # add region code to path

    # recursively look up all CSV files in path
    all_files = glob.glob(os.path.join(path, "*.csv"))
    
    names = [os.path.basename(x) for x in all_files]

    for file_, name in zip(all_files, names):
        #read first row only
        file_df = pd.read_csv(file_,nrows=1)    

        file_df['file_name'] = name
        df = df.append(file_df)

        return df


# 1c) Import all CSV files saved since the last rental listings data were stored in the SQL table, ie, based on the files' suffix indicating the date when the webcrawler was run, relative to the latest_date SQL query results 
def import_all_CSV_since_latest_date_and_concat_to_df(parent_direc:str, region_code: str, latest_date_from_query):
    """Recursively search directory of scraped data for given region, and look up all CSV files.
    Then, import all CSV files to a single Pandas' df using pd.concat(). Only apply filter if the SQL table
    contains at least some data for given region."""

    # recursively search for scraped_data CSV files for given region 


    # get path for scraped data pertaining to the given region:
    path = os.path.join(parent_direc, region_code) 

    print(f"Path to scraped data for {region_code} region:\n{path}") 

    # specify datetime format used for the scraped_data CSV files 
    datetime_format_scraped_data = "%m_%d_%Y"

    # initialize list to contain all scraped data file names 
    files_list = []

    # recursively iterate over parent directory and all of its subdirectories, to get paths to all CSV files
    for dirs, subdirs, files in os.walk(path):


        # iterate over each file within parent directory and all subdirectories
        for file in files:
            
            # only include CSV files: 
            if file.endswith('.csv'):
                # grab full paths for all found CSV files--ie, join directories (dirs) with the CSV file namesn (file from files)  
                files_list.append(os.path.join(dirs, file))


    # assign all CSV file paths to a DataFrame:
    df = pd.DataFrame(files_list, columns=['files'])

    print(f"\n\nSome scraped data CSV file paths:\n{df['files'].head()}\n")
    
    # # Parse the dates from each CSV file, and keep the same 'MM_DD_YYY' format (**including the underscore delimiters!!), as the webcrawler CSV file naming convention:
    df['date_of_file'] = df['files'].str.extract(r'(\d{2}_\d{2}_\d{4})')

    # convert col to datetime
    df['date_of_file'] = pd.to_datetime(df['date_of_file'], format='%m_%d_%Y')

    print(f"Scraped file data dates, before filtering:\n{df['date_of_file'].head()}")

    # Only apply datetime filter **if** the SQL table already contains at least some data for given region--ie, the query result does not comprise a null:

    # # print(f"Logic test:\n\n{latest_date_from_query['latest_date'].str.contains('None').any()}")
    # print(f"Logic test:\n\n{latest_date_from_query.isnull()}")


    # if latest_date_from_query != "None":  # the SQL table contains at least some data for given region

    # if latest_date_from_query['latest_date'].str.contains("None").any():  # the SQL table contains at least some data for given region
    if latest_date_from_query.isnull() is False:  # the SQL table contains at least some data for given region


        # use latest_date_from_query as the start date of our file date-filter:
        # transform the data to be in a "%M-%d-%Y" format, ton match the file naming structure (ie, the underscores and month, then day, then year format are important to filter the files properly):
        start_date = latest_date_from_query.strftime("%m-%d-%Y") # reformat datetime format to match the date_of_file format

        # get date of today (ie, use .today() method to just extract the month, day, and year, not time components such as hours, minutes, etc.)
        # date_now = datetime.datetime.now()
        date_now = datetime.date.today()

        # convert %M month format to %m month format
        end_date = datetime.datetime.strptime(str(date_now), "%Y-%m-%d").date().strftime("%m-%d-%Y")
                

        # sanity check on dates to be used to filter to the daterange
        print(f'Start date for file filter:\n{start_date}')

        print(f'End date for file filter:\n{end_date}\n')

        ## ## Apply  the daterange filter, so we get only the CSV files that are more recent than the data stored in the SQL tables:
        # specify the mask for filtering
        datetime_mask = (df['date_of_file'] > start_date) & (df['date_of_file'] <= end_date)
        # apply the filter
        file_date_slice = df.loc[datetime_mask]

        # having applied the filter, just grab the CSV file paths and convert to list
        file_filtered_dates_list =  file_date_slice['files'].tolist()

        # briefly, look up the total number of CSV files of scraped data after applying the date range filter: 
        print(f"\n**After filtering:\nNumber of all recursively found CSV files:\n{len(file_filtered_dates_list)}\n")

        ## Finally, import the CSV files based on the date-filtered CSV files list, then concat to a single df
        list_of_dfs = [pd.read_csv(file_path) for file_path in file_filtered_dates_list]  # import the filtered CSV files
        
        # concat to a single df:
        df = pd.concat(list_of_dfs)


     # account for scenario in which *no data* has yet been inserted into the SQL table:
    else:   # do not apply datetime filter
        # instead import all available scraped_data files for given region
        list_of_dfs = (pd.read_csv(files) for files in files_list) 
        
        # concat to a single df:
        df = pd.concat(list_of_dfs, ignore_index=True)
    
    return df


# 3.) b.) filter Pandas' dataframe by latest date of date_posted found via MAX( SQL query
def filter_df_since_specified_date(df: DataFrame, latest_date_sql_str: str):
    """Filter the imported scraped dataset to all data newer than the specified date of data stored in the SQL table, which is given via the MAX(posted_date) query results."""
    
    # only apply the filter if the SQL query indicates at least some data has been stored in the SQL table, for given region

    # if latest_date_sql_str != "None": #  a) latest_date_sql_str query result object is not literally "None" 
    if latest_date_sql_str.isnull() is False: #  a) latest_date_sql_str query result object is not literally "None" 

        # define datetime mask, so we ensure we will be inserting only more recent data than what's already stored in the table
        datetime_mask = (df['date_posted'] > latest_date_sql_str)
        # apply the datetime filter
        df = df.loc[datetime_mask]

    # account for a scenario in which *no data* has yet been inserted into the SQL table
    else:   # ie, the query returned target_date of "None" or an empty DataFrame
        print("No data for given region has yet been inserted into the SQL table, so we do not need to apply a datetime filter.")
        pass  # do not apply filter, since no data has yet been inserted into SQL table
    return df




    


# 1d) Verify whether *any* data have preivously been scraped for given region (ie, based on sscraped data stored on current local machine) 
def verify_scraped_data_exists_for_region(df, region_codes):
    # check if at least 1 row of scraped data exists
    if len(df.index) > 0:
        print("\nScraped data for region exists. ETL pipeline can proceed.\n")

    else: # no scraped data are available for selected region
        print("\nPlease select another region from dropdown\n")

        # prompt user to select *another* region,  which actually does contain scraped data
        prompt_user_to_specify_region_to_update(region_codes)



# 2.) Determine latest data of scraped data inserted into SQL table 
class SQL_Database:
    def __init__(self, path_for_SQL_config):

        with open(path_for_SQL_config,'r') as fh:
            config = json.load(fh)  # open config.json file, which contains all SQL database credentials--ie, username, password, database name, etc. 

        self.driver = config['driver']
        self.server = config['server']
        self.database = config['database']
        self.username = config['username']
        self.password = config['password']
        print(f"\nSanity check on database name (ie, based on the json configuration file:\n{self.database}\n")  # sanity check

    # 2 a) Perform SQL query on date_posted col to determine the most recent date of data stored in the table  
    def determine_latest_date(self, region_code: str):
        """Calculate the most recent date of rental listings data that we have inserted into the SQL rental table, for given craigslist region"""
        try:  # try to establish connection to SQL Server table via pyodbc connector
            conn = pyodbc.connect(
            f'DRIVER={self.driver};'
            f'SERVER={self.server};' 
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            'Trusted_Connection=yes;'
            )
        
        except pyodbc.Error as err:  # account for possible pyodbc SQL Server connection error
            print("We were not able to connect to the SQL server database properly. Please double-check config.json and try again.") 

        # initialize cursor so we can execute SQL code
        cursor = conn.cursor() 

        # specify SQL query
        query = "SELECT MAX(date_posted) AS latest_date FROM rental WHERE region = ?;"  # check latest date of stored listings data, for given region 

        # perform query, and convert query results to Pandas' df, with respect to given region (eg, sfbay)
        max_date = pd.read_sql(sql = query, con = conn, params =(region_code,))   # NB!: we need to pass the region_code str argument as a tuple to satisfy .read_sql() method's API for the params parameter!

        cursor.close()
        conn.close()

        return max_date


    # 5.) **insert filtered and cleaned pandas' df into SQL table (**final step of data pipeline)
    def insert_df_to_SQL_ETL(self, df, region_code):
        """Insert scraped Craigslist rental listings data (ie, the Pandas' dataframe) to SQL Server database 'rental' table"""

        # establish connection to SQL Server database-specify login credentials:
        try:  # try to establish connection to SQL Server table via pyodbc connector
            conn = pyodbc.connect(
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            'Trusted_Connection=yes;'
            )
        
        except pyodbc.Error as err:  # account for possible pyodbc SQL Server connection error
            print("Python (via pyodbc driver) was not able to connect to SQL Server database.\nPlease double-check username and other configuration credentials, and try again.") 

        # initialize cursor so we can execute SQL code
        cursor = conn.cursor() 
        # speed up data ingesting by reducing the numbers of calls to server for inserts
        cursor.fast_executemany = True  
        
        # insert scraped data from df to SQL table-- iterate over each row of each df col via .itertuples() method

        ## NB!: **only** include several of the columns for purposes of debugging *why* the SQL inserts are not working
        # --this is posibly due to 2 datetime formats for date_posted & or possibly due to issues with float data of the listingid's or even bathrooms data

        # ## get a subset of the df columns
        # df = df[['ids', 'sqft', 'cities', 'prices', 'bedrooms', 'date_posted']]

        # Get the number of needed '?' placeholders (ie, best practice to help prevent SQL injections) by looking up the # of cols (ie, len()) of the dataframe), and use .join() to have each question mark seprated by commas:
        q_mark_str = ','.join('?'*len(df.columns))    # get '?' placeholders for each col of df

        try:  # try to make data inserts into SQL table
            # specify INSERT INTO SQL statement--iterate over each row in df, and insert into SQL database:
            for row in df.itertuples():  # iterate over each row from df
                cursor.execute(f"""INSERT INTO rental (listing_id, sqft, city, price, bedrooms, bathrooms, attr_vars,
                date_of_webcrawler, kitchen, date_posted, region, sub_region, cats_OK, dogs_OK, wheelchair_accessible,laundry_in_bldg, no_laundry, 
                washer_and_dryer, washer_and_dryer_hookup, laundry_on_site, full_kitchen, dishwasher, refrigerator,
                oven,flooring_carpet, flooring_wood, flooring_tile, flooring_hardwood, flooring_other, 
                apt, in_law_apt, condo, townhouse, cottage_or_cabin, single_fam, duplex, flat, land,
                is_furnished, attached_garage, detached_garage, carport, off_street_parking, no_parking, EV_charging, air_condition, no_smoking) 
                VALUES ({q_mark_str})""",


                # # NB!: try the following query to help ensure
                # # create temp table to insert all data from the pipeline, which we will then use for a MERGE statement to provide a WHEN NOT MATCHED clause to ensure no duplicate ids will be spring up when actually inserting the data into the actual, long-term table
                # CREATE TABLE #MyTempTable (col1 VARCHAR(50), col2, col3...);
                # # insert all of the cleaned data into the temporary table
                # INSERT INTO #MyTempTable(col1, col2, col3, col4)
                # VALUES (?,?,?,?)
                # # create clustered index based on the temporary table's primary key 
                # CREATE CLUSTERED INDEX ix_tempCol1 ON #MyTempTable (col1);
                # # implement the final part of the data pipeline by using a MERGE statement to avoid inserting any duplicate ids, via a USING...WHEN NOT MATCHED THEN clause!:
                # MERGE INTO db_name.dbo.table_name AS TARGET
                # USING #MyTempTable AS SOURCE ON TARGET.COL1 = SOURCE.COL1 AND TARGET.COL2 = SOURCE.COL2 ...
                # WHEN NOT MATCHED THEN
                #     INSERT(col1, col2, col3, col4)
                #     VALUES(source.col1, source.col2, source.col3, source.col4);

                (row.ids,
                row.sqft,
                row.cities,
                row.prices, 
                row.bedrooms,
                row.bathrooms,
                row.attr_vars, 
                row.date_of_webcrawler,
                row.kitchen,
                row.date_posted,
                row.region,
                row.sub_region,
                row.cats_OK,
                row.dogs_OK,
                row.wheelchair_accessible,
                row.laundry_in_bldg, 
                row.no_laundry,
                row.washer_and_dryer,
                row.washer_and_dryer_hookup,
                row.laundry_on_site,
                row.full_kitchen,
                row.dishwasher,
                row.refrigerator,
                row.oven,
                row.flooring_carpet,
                row.flooring_wood,
                row.flooring_tile,
                row.flooring_hardwood,
                row.flooring_other,
                row.apt, 
                row.in_law_apt,
                row.condo,
                row.townhouse,
                row.cottage_or_cabin,
                row.single_fam, 
                row.duplex,
                row.flat,
                row.land,
                row.is_furnished,
                row.attached_garage,
                row.detached_garage,
                row.carport,
                row.off_street_parking,
                row.no_parking,
                row.EV_charging,
                row.air_condition,
                row.no_smoking)
                )

            # save and commit changes to database
            conn.commit()

            print("\n\nWe have inserted the records from the DataFrame, and the SQL Server table has been updated successfully.")
        
         #account for possible errors while inserting dataframe into SQL table
        except pyodbc.Error as ex:
                print("\nAn error occurred while inserting the DataFrame records into the SQL Server table:\n")
                # parse and print the specific pyodbc SQL error message:
                sqlstate = ex.args[1]
                print(sqlstate) 
                quit()


        # # sanity check-- ensure some **new** data has been inserted into SQL table, for given region, ie, based on showing a newer MAX(date_posted)!
        # specify SQL query
        query = "SELECT MAX(date_posted) AS latest_date FROM rental WHERE region = ?;"  # check latest date of stored listings data, for given region 

        # perform query, and convert query results to Pandas' df, with respect to given region (eg, sfbay)
        max_date = pd.read_sql(sql = query, con = conn, params =(region_code,))   # NB!: we need to pass the region_code str argument as a tuple to satisfy .read_sql() method's API for the params parameter!

        print(f"\nThe latest date_posted date--**after** inserting the newer data--for the SQL table is now:\n{max_date}\n")     
        
        cursor.close()
        conn.close()    
    

# 2) b.) Transform query results to string
def datetime_col_to_str_of_datetime(df: DataFrame, datetime_col:str):
    """Given datetime col from pandas' DataFrame, transform to a string of the datetime value."""
    return df[datetime_col].head(1).astype(str).reset_index().loc[0, datetime_col] 

# 2c) Transform query results string to datetime, but change the datetime format to match the CSV file naming format:
def str_to_datetime_with_different_format(str_to_convert: str, initial_datetime_format: str, new_datetime_format: str):
    return datetime.datetime.strptime(str_to_convert, initial_datetime_format).strftime(new_datetime_format)
 
 # NB: the above re-formats the query result to the datetime format we want, but converts it to a str, instead of datetime. Thus, we need to convert the reformatted latest_date_str_mm_dd_yyyy str to datetime:
def str_val_to_datetime(str_to_convert, datetime_format):
    return datetime.datetime.strptime(str_to_convert, datetime_format)



## Transform columns to datetime

## NB: First we need to remove extraneous trailing chars in data_posted
def clean_date_posted_data(df):
    return df['date_posted'].str.rstrip('-0700')



def transform_cols_to_datetime(df: DataFrame, col_to_convert:str):
    """Transform relevant column(s) to datetime using pd.to_datetime() method"""
    return pd.to_datetime(df[col_to_convert])

def transform_cols_to_datetime_specific_format(df: DataFrame, col_to_convert:str, datetime_format):
    """Transform relevant column(s) to datetime using pd.to_datetime() method.
    Specify date format via .strftime() method. We need to chain pd.to_datetime() to another pd.to_datetime() so we can convert the object result
    from .strftime to datetime!
    Use errors = 'coerce' and utc=True arguments to ensure to_datetime() will work
    even if a given row does not contain datetime-like values.
    After running the first to_datetime(), we need to drop any remaining null values, before inserting into the SQL database)"""
    # return datetime format to the nearest hour and minute
    df[col_to_convert] =  pd.to_datetime(df[col_to_convert], errors='coerce', utc=True)
    # remove any resulting null date_posted (ie 'NAT') rows
    df = df.dropna(subset = [col_to_convert])

    return pd.to_datetime(pd.to_datetime(df[col_to_convert]).dt.strftime(datetime_format))



# 4.) Perform all additional data cleaning procedures to prep the dataframe prior to initiating the pyodbc pandas' to SQL Server data pipeline inserts:

def deduplicate_df(df: DataFrame):
    """Remove duplicate rows based on listing ids (keep last ones since we might want to examine the length of time a given rental listing has been posted."""
    return df.drop_duplicates(keep='last', subset = ['ids'])


def remove_nulls_list(df, list_of_cols):
    """Remove rows that do not have price, city name, kitchen, sqft, or listing ID data, as these are essential variables in this rental listings dataset."""
    return df.dropna(subset=list_of_cols)

# def remove_nulls(df):
#     """Remove rows that do not have price, city name, kitchen, sqft, or listing ID data, as these are essential variables in this rental listings dataset."""
#     return df.dropna()

""" Clean the city names data (ie, non null city names) by removing extraneous address & street data, non-sfbay cities, etc."""

# NB!: to more precisely clean city names, we will run a short webcrawler to grab wikipedia table data on all SF Bay city names:
# Identify a list of all unique SF Bay Area & SC county city names, and output to a list

# a) Create a few simple webcrawlers to grab the city names data from 2 wikipedia tables
### SF bay area city names data




# access page, and grab city names, append to list

def obtain_cities_from_wiki_sfbay(webpage_url,list_of_cities):
    # initialize web driver
            
    driver = webdriver.Chrome()  # install or update latest Chrome webdriver using using ChromeDriverManager() library
    
    # access webpage
    driver.get(webpage_url)

    # specify xpath to wiki table containing the city names data:
    xpaths_table = '//table[@class="wikitable plainrowheaders sortable jquery-tablesorter"]'

    # specify max number of seconds to wait for given HTML element to load, before specifying TimeoutException
    download_delay = 20


    # wait until the webpage's "searchform" form tag has been loaded, or up to a maximum 20 seconds (ie, given the value of self.download_delay)
    try: # wait until the form tag with ID of "searchform"--ie, the Craigslist page given our search results--has been loaded, or up to a maximum of 30 seconds (given download_delay)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpaths_table))
        )  # NB: you need to use a tuple as the argument of the selenium EC.presence_of_element_located() function, hence the double-parantheses
        print('\nPage has loaded, and we can start scraping the data.\n')
    except TimeoutException:
        # Return error message if loading the webpage takes longer than the maximum n seconds
        print(f"\nLoading the webpage's searchform element timed out: ie, it took longer than the maximum number of {download_delay} seconds.\n")


    # having waited for page element to load, grab the wiki data tables from webpage:
    table = driver.find_element(By.XPATH, xpaths_table)


    # iterate over each table row and then row_val within each row to get data from the given table, pertaining to the city names
    for row in table.find_elements(By.CSS_SELECTOR, 'tr'): # iterate over each row in the table
        
        
        city_names =  row.find_elements(By.TAG_NAME, 'th')  # iterate over value of each row, *but* ONLY for the 1st column--ie, the 0th index
        # city_names =  row.find_elements(By.TAG_NAME, 'td')[0]  # iterate over value of each row, *but* ONLY for the 1st column--ie, the 0th index

        # extract text, but *skip* the first 2 rows of the table  rows' values since these are only the column names!
        for city_name in city_names[:2]: # skip first 2 rows 

            # append the remaining data to list
            list_of_cities.append(city_name.text)


    # exit webpage 
    driver.close()


    return list_of_cities

# Santa Cruz data from wiki
def obtain_cities_from_wiki_sc(webpage_url,list_of_cities):
    # initialize web driver
            
    driver = webdriver.Chrome()  # install or update latest Chrome webdriver using using ChromeDriverManager() library
    
    # access webpage
    driver.get(webpage_url)

    # specify xpath for the corresponding wiki data tables--NB!: there are 2 tables with the same class name; only select data from the 2nd one
    xpaths_table = '//table[@class="wikitable sortable jquery-tablesorter"][2]//tr//td[2]'  # 2nd table on webpage with this class name

    # specify max number of seconds to wait for given HTML element to load, before specifying TimeoutException
    download_delay = 20


    # wait until the webpage's "searchform" form tag has been loaded, or up to a maximum 20 seconds (ie, given the value of self.download_delay)
    try: # wait until the form tag with ID of "searchform"--ie, the Craigslist page given our search results--has been loaded, or up to a maximum of 30 seconds (given download_delay)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpaths_table))
        )  # NB: you need to use a tuple as the argument of the selenium EC.presence_of_element_located() function, hence the double-parantheses
        print('\nPage has loaded, and we can start scraping the data.\n')
    except TimeoutException:
        # Return error message if loading the webpage takes longer than the maximum n seconds
        print(f"\nLoading the webpage's searchform element timed out: ie, it took longer than the maximum number of {download_delay} seconds.\n")



    # search for given wiki data tables:
    table = driver.find_elements(By.XPATH, xpaths_table)


    print(f'Full table:\n\n{table}\n\n\n\n\n')

    for row in table:
        print(f'City names:{row.text}')
        list_of_cities.append(row.text)





    # exit webpage 
    driver.close()

    # # sanity check
    # print(f'List of city names:\n{list_of_cities}')

    return list_of_cities


# # combine both the sfbay city names & sc county names lists into one:
def combine_lists(list1, list2):
    return list1.extend(list2)

def add_dash_delimiter_in_bw_each_word_of_city_names(city_names:list):
    return [word.replace(' ', '-') for word in city_names]  # use str.replace() method to replace whitespaces with dashes


# clean city names by matching scraped craigslist data to that of the wikipedia table data:
def parse_city_names_from_listing_URL(df, unique_city_names_dash_delim:list):
    """ First, check whether a given listing is of the newer variety--since January 
    2023--and if so, 
    
    1) Use str.contains() method chained to a .join() method in which we perform an 'OR' boolean via
    the pipe (ie, '|' operator--ie, so we can search for multiple substrings (ie, each element 
    from the list arg) to look up any matching instances of city names
    from the unique_city_names... list 
    relative to the rental listing URLs (ie, listing_urls).

    2) Then, parse each such first city name by taking the first matched city name only,

    3) Use these parsed city name values to **replace** the values for the 'cities' column!"""
    
    ## Transform all city name strings to lower-case:
    # apply lower-case for the list of SF Bay + SC county names:
    unique_city_names_dash_delim  = [el.lower() for el in unique_city_names_dash_delim]

    ## convert each element in the referencing columns to lower-case for sake of consistency, ie w/ respect to list of city names
    # listing urls
    df['listing_urls'] = df['listing_urls'].str.lower()  # apply lowercase to all characters of each row's string vals 
    # city names col
    df['cities'] = df['cities'].str.lower()  # apply lowercase to all characters of each row's string vals 

    # specify pipe operator, which we can use as a Boolean "OR" operator for the str.contains() method
    pipe_operator = '|'

    # URL substring path to look up whether the URL contains the listing's city name
    url_path_with_city_names = '/apa/d'

    # specify a regex pattern for a str.extract() method--NB: we need to wrap the pattern within a sort of tuple by using parentheses in strings--ie, '( )', so like the following format: '( regex_pattern...)'
    unique_city_names_dash_delim_pattern = '(' + pipe_operator.join(unique_city_names_dash_delim)+')'  # wrap the city names regex pattern within a 'string' tuple: ie, '(...)'



    # if statement to check whether given listing (ie, row of df) contains '/apa/d' in the listing's URL path (else just '/apa')
    for row in df['listing_urls']:
        # extract city names in reference to the (newer) listing URLs (given the '.../apa/d' in URL path)
        if url_path_with_city_names in row:

        # NB: alternative approach using str.contains() and .any()    
        # if df['listing_urls'].str.contains(url_path_containing_city_names,regex=False).any():

            # # step 1: use str.split() on '/apa/d' and get the 2nd element after performing the split:
            # df['listing_urls_for_str_match'] = df['listing_urls'].str.split('/apa/d/').str[1]  # obtain the 2nd resulting element
            

            #step 3: match a substring from this newly-parsed column-- ie, 'listing_urls_for_str_match'
            # -- to matching substrings from the  sfbay_city_names list:
            # How?: use str.contains() and join pipe operators to each element of the list to perform an essentially  boolean "OR" str.contains() search for any matching city names


    
            # replace cities with matching city names wrt listing_urls_for_str_match col from regex pattern (ie, derived from list of names), using str.extract() 
            df['cities'] = df['listing_urls'].str.extract(unique_city_names_dash_delim_pattern, expand=False)
            # sanity check
            print(df['cities'])

        else:  #ie, older listings in which rental listings do not contain city names--as indicated by just 'apa' instead of 'apa/d' in the listing URL path 


            # replace cities with matching city names wrt listing_urls_for_str_match col from regex pattern (ie, derived from list of names), using str.extract() 
            df['cities'] = df['cities'].str.extract(unique_city_names_dash_delim_pattern, expand=False, regex=True)

        return df

def clean_city_names(df, col):
    """REmove literal 'Nan' from cities col"""
    return df[col].str.replace('Nan', ' ', regex=True)

def remove_dashes_from_words_in_col(df, col):
    return df[col].str.replace('-', ' ', regex=True)


def capitalize_each_word_in_row_for_col(df, col):
    return df[col].str.title()




def clean_split_city_names(df, address_critera: list, neighborhood_criteria:list, split_city_delimiters: list, incorrect_city_names:dict, cities_not_in_region:dict, cities_that_need_extra_cleaning:dict):
    """Clean city names data in several ways:
    a.) Remove extraneous address & neighborhood data placed in the city names HTML object, such as 'Rd', 'Blvd', or 'Downtown'.
    b.) Unsplit city names data that are split via ',' & '/' delimiters.
    c.) Replace abbreviated or mispelled city names.
    ci) Set all city names to lowercase by using .lower(), for sake of consistent data cleaning (casing will be parsed later).
    d.) Remove city names that do not exist within the SF Bay Area (e.g., 'Redding')--ie, by using .replace() and replacing with whitespace (ie, ' '). 
    e.)Remove any digits/integers within the city names data--ie, by using a '\d+' regex as the argument of str.replace() and replace it with empty strings.
    f.) Remove any city names records that are left with merely empty strings (ie, the other steps removed all data for that given cities record).
    g.) Remove any whitespace to avoid the same city names from being treated as different entities by Pandas, Python, or SQL. 
    h.) Use str.capwords() to capitalize words (ie, excluding apostrophes).
    i.) Replace city names that are mispelled after having removed various street and neighborhood substrings such as 'St' or 'Ca'--e.g., '. Helena' should be 'St. Helena'. 
    j) Remove any remaining empty strings, null records, or rows with literal 'nan' values (ie, resulting from previous data cleaning steps)"""
    # specify extraneous street & address data (e.g., 'Rd') that we want to remove from the city names column:
    addr_criteria = '|'.join(address_critera) # Join pipe ('|') symbols to address list so we can str.split() on any one of these criteria (ie, 'or' condition splitting on each element separated by pipes):
    # specify extraneous neighborhood criteria that we should also remove from the column
    nbhood_criteria = '|'.join(neighborhood_criteria) # specify neighborhood names as well as state abbreviation (shown on website as ' Ca') that is shown without the usual comma delimiter, which we should remove from the rows of cities col
    # b.) specify delimiters we need to refer to un-split city names:
    split_city_delimiters = '|'.join(split_city_delimiters) # join pipes to delimiters so we can use str.split() based on multiple 'or' criteria simultaneously
    # clean city names data by removing extraneous address & neighborhood data, and unsplitting city names based on ',' & '\' delimiters
    df['cities'] =  df['cities'].str.split(addr_criteria).str[-1].str.replace(nbhood_criteria, '', case=True).str.lstrip()
    df['cities'] = df['cities'].str.split(split_city_delimiters).str[0] #unsplit city names based on comma or forward-slash delimiters
    # c.) replace specific abbreviated or mispelled city names
    df = df.replace({'cities':incorrect_city_names}, regex=True) # replace mispelled & abbreviated city names
    # ci) Set all city names data to lower-case temporarily, to ease the data cleaning & wrangling:
    df['cities'] = df['cities'].str.lower()
    
    # d) remove data in which the cities are not actually located in the sfbay region:
    df['cities'] = df['cities'].replace(cities_not_in_region, '', regex=True )  # remove (via empty string) cities that are not actually located in the sfbay region
    # e.) Remove digits & integer-like data from cities column:
    df['cities'] = df['cities'].str.replace('\d+', '')  # remove any digits by using '/d+' regex to look up digits, and then replace with empty string
    # f.) Remove any rows that have empty strings or null values for cities col (having performed the various data filtering and cleaning above)
    df = df[df['cities'].str.strip().astype(bool)] # remove rows with empty strings (ie, '') for cities col 
    df = df.dropna(subset=['cities']) # remove any remaining 'cities' null records
    # g.) Remove whitespace
    df['cities'] = df['cities'].str.strip() 
    # h.) capitalize the city names using str.capwords() 
    df['cities'] = df['cities'].str.split().apply(lambda x: [val.capitalize() for val in x]).str.join(' ')
    # i) Replace city names that are mispelled after having removed various street and neighborhood substrings such as 'St' or 'Ca'--e.g., '. Helena' should be 'St. Helena' & 'San los' should be 'San Carlos'. Also, remove any non-Bay Area cities such as Redding:
    df = df.replace({'cities':cities_that_need_extra_cleaning})
    # j) Remove any remaining empty strings, null records, or rows with literal 'nan' values (ie, resulting from previous data cleaning steps)
    # remove rows with literal 'nan' values
    df['cities'] = df['cities'].replace('nan', '', regex=True)

    df = df[df['cities'].str.strip().astype(bool)] # remove rows with empty strings (ie, '') for cities col 
     
    df = df.dropna(subset=['cities']) # remove any remaining 'cities' null records
    return df



def transform_cols_to_indicators(df, list_of_cols):
    """ Transform relevant attribute columns to numeric, and specify NaNs for any missing or non-numeric data. Finally, convert any null records to 0s for ease of inserting into SQL table."""
    df[list_of_cols] = df[list_of_cols].astype('uint8', errors='ignore') # convert any missing data to NaN 
    df[list_of_cols] = df[list_of_cols].fillna(0) # impute any NaN values with 0s since we can be quite certain that any rental listings not explicitly specifying a specific property type, amenity, or attribute do not actually contain said attribute, amenity, or are not said propery type. Finally, this makes it more viable to insert these data into a SQL table.  
    print(f"\n\nSanity check: The data types of {list_of_cols} are now: \n{df[list_of_cols].dtypes}") # sanity check on columns' data types
    return df


def transform_cols_to_int(df, list_of_cols_to_num):
    """ Transform relevant attribute columns to numeric.
    NB: Since the scraped 'prices' data can contain commas, we need to use str.replace(',','') to remove them before converting to numeric."""
    df['prices'] = df['prices'].str.replace(",","") # remove commas from prices data (e.g.: '2500' vs '2,500')
    # clean sqft data --remove all non-numeric data
    df['sqft'] = df['sqft'].astype(str).str.replace(r'\D+', '', regex=True) # remove all non-numeric data from 'sqft' col by using regex to replace any non-numeric data from col to null ('NaN') values via the str.replace() Pandas method
    df['sqft'] = df['sqft'].replace(r'^\s*$', np.nan, regex=True)  # replace all empty str sqft values with  null ('NaN') values 
    # clean prices data-- remove any records posted with sqft instead of price data
    df = df[~df.prices.str.contains("ft2", na=False)] # remove listings records with incorrectly posted prices data 
    # remove rows with any remaining null rows wrt list of cols (ie, sqft, prices, etc.) (so we can readily convert to int):
    df = df.dropna(subset=list_of_cols_to_num) # remove rows with null data 
    # finally, convert all cols from list to 'int64' integer data type:
    df[list_of_cols_to_num] = df[list_of_cols_to_num].astype('int64') # use int64 due to a) the long id values & b.) the occasional null values contained within the sqft col
    print(f"Sanity check: The data types of {list_of_cols_to_num} are now: \n{df[list_of_cols_to_num].dtypes}") # sanity check on columns' data types
    return df


# Clean bathrooms data-- transform records containing 'shared' or 'split' to 1-- Why?: Because we can assume that any rental units comprising a 'shared' bathroom is essentially 1 bathroom
def transform_shared_and_split_to_ones(df: DataFrame, col_to_transform: str):
    """Transform any records (from given col) containing the string values of 'shared' or 'split' to a value of 1."""
    # transform col to object, so we can use Python str methods to transform the data
    # df[col_to_transform] = df[col_to_transform].astype('object') 

    df[col_to_transform] = df[col_to_transform].astype(str)
    bedroom_replace_criteria = ['shared', 'split']
    bedroom_replace_criteria = '|'.join(bedroom_replace_criteria) # join pipe symbols so we can use str.replace() on multiple 'or' conditions simultaneously 
    return df[col_to_transform].str.replace(bedroom_replace_criteria,'1')
    # return df[col_to_transform].str.replace(bedroom_replace_criteria,'')


# replace any ambiguous values for bathrooms data--such as '9+' with empty strings (ie, essentially nulls) 
def replace_ambiguous_data_with_empty_str(df: DataFrame, col_to_transform: str):
    """Replace ambiguous rows of data (ie, any containing a plus sign) for bathrooms col with empty strings"""
    return df[col_to_transform].str.replace(r'\+', '')  # use str.replace() to use a regex to search for plus signs, and in effect remove these by replacing them with empty strings 

# def remove_bedroom_and_br_nulls(df: DataFrame):
#     df[['bedrooms', 'bathrooms']] = df.dropna(subset=['bedrooms', 'bathrooms'])
#     return df


def transform_cols_to_float(df: DataFrame, col_to_transform: str):
    return df[col_to_transform].astype('float32')

def round_to_nearest_decimal_pt(df, col):
    return df[col].round(2) 


def remove_col_with_given_starting_name(df, col_starting_name: str):
    """Remove each column from df that has a given starting name substring."""
    return df.loc[:, ~df.columns.str.startswith(col_starting_name)] 



def main():
    # specify names of metropolitan craigslist region names and their corresponding craigslist urls, store in dict
    clist_region_and_urls = {
        'SF Bay Area, CA':'https://sfbay.craigslist.org/',
        'San Diego, CA':'https://sandiego.craigslist.org/',
        'Chicago, IL':'https://chicago.craigslist.org/',
        'Seattle, WA':'https://seattle.craigslist.org/',
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
    

    # prompt user to select which region for updating the database:
    region_name = prompt_user_to_specify_region_to_update(clist_region_and_urls)

    region_URL = return_hompeage_URL_for_given_region(clist_region_and_urls, region_name)

    # parse region code from homepage url of selected region:
    region_code = parse_region_code_from_craigslist_URL(region_URL)

    # sanity check on region code:
    print(f"\nSelected region code:\n{region_code}\n")

    print(f"Current direc:{os.getcwd()}")


    # # 1) a) Import all scraped rental listings data from given region:

    # specify path to scraped data
    # get root directory of project by getting parent directory (ie, using os's .pardir method) 
    parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    print(f"\nParent (root) directory:\n{parent_directory}\n")

    
    # specify folder of webcrawler's scraped data
    scraped_data_folder = 'scraped_data'

    # get full path to scraped_data, by referring to root directory (ie, parent_directory) & scraped_data_folder
    scraped_data_parent_path = os.path.join(parent_directory, scraped_data_folder)

    print(f'The directory of the scraped data is:\n{scraped_data_parent_path}\n\n')




    try:   
        df_data_check_for_region = check_data_exists_for_given_region(scraped_data_parent_path, region_code)


        # Inform user that data do exist for particular region selected, so the pipeline can continue as expected
        print(f"\nScraped data for {region_code} region exists.\nETL pipeline can proceed\n")


    except ValueError:   # account for potential Valueerror--ie, if there is *no* available scraped data for the given region
        # inform user no data exists for given region, so this script cannot proceed
        print("\nSorry, there is no data available for the selected region.\nPlease run this script again with a different region, or run the webcrawler at least once for the selected region.")


    ## 2) Determine the last date of listings data stored in SQL table, so we can filter the dataset before inserting the data:

    # SQL config json file: specify folder (relative to root directory) & file name of json file containing SQL configuration & login data 
    sql_config_folder_and_json = "SQL_config\\config.json" 

    # get full path to SQL config, by referring to root directory (ie, parent_directory) & sql_config_folder_and_json
    sql_config_path = os.path.join(parent_directory, sql_config_folder_and_json)

    SQL_db = SQL_Database(sql_config_path)  # NB: initialize class and pass in path to the json SQL configuration file 
    
    ## 2a.) implement query to select the latest date based on date_posted:
    latest_date = SQL_db.determine_latest_date(region_code)

    print(f"\n\nThe latest date of the scraped data stored in the SQL table, for the {region_code} region is:\n{latest_date}")


    # leave latest_date unchanged if SQL query results indicate no data have been inserted into SQL database so far for given region
    # if latest_date.values.all()  != "None":
    if latest_date.isna().values.any():
        # keep latest_date_dt as assigned to "None" since no data yet exist in the SQL table
        latest_date_dt = latest_date
        
    # only make adjustments to latest_date object if query returns a non-null value
    else:  
    
        ## 2) b.) Transform query results to string:

        # specify name of df (ie, latest_date) containing the query results and datetime col to transform
        latest_date, dt_col = latest_date, 'latest_date' 
        # convert query results to str
        latest_date_str = datetime_col_to_str_of_datetime(latest_date, dt_col)

        
        # sanity check
        print(f"\n\nThe latest date among the scraped data stored in the SQL table is:\n{latest_date_str}")
        print(f"Data type of this object is--NB: make sure it's str:\n{type(latest_date_str)}")

        # specify datetime format of query results
        initial_datetime_format =  "%Y-%m-%d %H:%M:%S"
        # convert query results from str to datetime
        latest_date_dt = str_val_to_datetime(latest_date_str, initial_datetime_format)


    
    ## 3.) Recursively import all CSV files to scraped data with dates *after* last data inserted into SQL table--ie, the latest_date whose value we obtained from the MAX(date_posted) query

    # import and concat all scraped data for given region *since* latest data stored in SQL table--ie, given by MAX(date_posted):
    df = import_all_CSV_since_latest_date_and_concat_to_df(scraped_data_parent_path, region_code, latest_date_dt)

    ## 3b) Data Cleaning: perform the first data cleaning steps, in particular those that improve runtime efficiency: e.g., by reducing thw size of the dataset by removing duplicate ids or rows with missing data (ie, nulls), etc
    
    ## De-duplicate data based on listing ids--ie, since each rental listing has unique ids
    df = deduplicate_df(df)
    # sanity check
    clist_duplicate_ids_check = df[df.duplicated("ids", keep= False)] 
    print(f"There should be no remaining duplicate listing ids (ie, 0 rows): \n{clist_duplicate_ids_check.shape[0]}") # sanity check --check that number of duplicate rows is false (ie, wrt duplicate listing ids)
    clist_duplicate_ids_check = []  # free memory


    # # ## 3.) Filter pandas' df dataset to data after last data inserted into SQL table--ie, the latest_date_str whose value we initially obtained from the MAX(date_posted) query
    
    # ## NB: before converting to datetime, re-format the string datetime-like columns to match the same yyyy-MM-dd format as that of the SQL Server table!
    # reformat to yyyy-MM-dd datetime format


    ## convert specific cols to datetime before filtering (for skae of consistency and replicability of this data pipeline
    ## NB!: we need to reformat the datetime format of these 2 columns-- why?: b/c the datetime formats of the input data differ from that of the SQL Server datetime data type, 
    
    ## 3a) convert the 2 columns to datetime format--first, convert to datetime, but allow for coerced errors due to date format inconsistencies 


    ## ewxamine the datetime data **before** doing data cleaning on them:
    print(f"\n\ndata_posted col values **before** doing data cleaning:\n{df['date_posted']}\n")



    # # NB:Convert the 2 relevant columns to datetime data type, referring to the initial datetime format:

    # clean date_posted data--remove trailing '-0700' char (if exists)-- before converting to datetime:
    df['date_posted'] == clean_date_posted_data(df)

    # next, remove any 'NaT'or other null values for both datetime columns so that we only include the values that have on of the 2 delineated datetime formats:
    list_of_datetime_cols = ['date_of_webcrawler', 'date_posted']

    df = remove_nulls_list(df, list_of_datetime_cols)

    # convert each of the 2 columns to datetime:
    df['date_of_webcrawler'] = transform_cols_to_datetime(df, 'date_of_webcrawler')

    # specify datetime format for date_posted as nearest hour and minute 
    dt_format = "%Y-%m-%d %H:%M"
    # transform date_posted col to datetime, given specified format
    df['date_posted'] = transform_cols_to_datetime_specific_format(df, 'date_posted', dt_format)


    ## Sanity check to ensure datetime conersion was successful:
    print(f"Sanity check to ensure the columns have been successfully converted to datetime:\n{df[['date_posted', 'date_of_webcrawler']].info()}")




    ## 3b) Filter df by datetime with respect to date_posted--based on the results from the SQL table query date (NB: this is separate from the datetime mask we applied earlier to filter the CSV files, which was based on the date_of_webcrawler values of the suffix of the file names...):
    df = filter_df_since_specified_date(df, latest_date_dt) 


    # sanity check
    print(f"\n\nSanity check: Ensure the data have been filtered properly to be newer than the latest date stored in the SQL table:\n")
    # show oldest and newest date_posted dates in cleaned data, by sorting the values:
    print(f"Newest and oldest date_posted dates for cleaned data:\nNewest: {df['date_posted'].max()}\Oldest: {df['date_posted'].min()}")


    ## remove any rows with null listing ids, prices, sqft, or city names   
    list_cols_to_remove_nulls = ["prices", "ids", "sqft", "kitchen", "cities"]  
    # df = remove_nulls_list(df, list_cols_to_remove_nulls)

    df = remove_nulls_list(df, list_cols_to_remove_nulls)

    # sanity check
    print(f"Remaining price, city name, sqft, kitchen, & listing id nulls: \n{df[list_cols_to_remove_nulls].isnull().sum()}")


    ## 4.) Additional data cleaning, wrangling, & data type transformations:

    ## Clean city names data

    # clean city names data:
    # NB: run a wikipedia table webcrawler to get a list of all possible SF Bay city names:

    # initialize lists:
    sfbay_city_names = []

    # sf bay area city names wiki page:
    sfbay_cities_wiki_url = 'https://en.wikipedia.org/wiki/List_of_cities_and_towns_in_the_San_Francisco_Bay_Area'


    #sfbay data
    obtain_cities_from_wiki_sfbay(sfbay_cities_wiki_url, sfbay_city_names)
    

    # remove remaining col names:
    sfbay_city_names = sfbay_city_names[4:]

    # sanity check
    print(f'sfbay city names:{sfbay_city_names}')

    print(f'There are {len(sfbay_city_names)} city names\nNB: There should be 101.')

    # Sc county city names data:
    # sc county wiki page url
    sc_county_cities_wiki_url = 'https://en.wikipedia.org/wiki/Santa_Cruz_County,_California#Population_ranking'
    # initialize list
    sc_county_city_names = []

    # Santa Cruz data from wiki
    obtain_cities_from_wiki_sc(sc_county_cities_wiki_url, sc_county_city_names)


    #  # clean data by removing extraneous '†' char from city names lists
    sc_county_city_names = list(map(lambda x: x.replace('†',''), sc_county_city_names))
    sfbay_city_names = list(map(lambda x: x.replace('†',''), sfbay_city_names))


    ## finally, remove any whitespace from lists-- use list comprehension
    sc_county_city_names = [s for s in sc_county_city_names if s.strip()]
    sfbay_city_names = [s for s in sfbay_city_names if s.strip()]


    # sanity check
    print(f'\n\nsc county city names:{sc_county_city_names}')
    print(f'There are {len(sc_county_city_names)} city names for SC county.')

    combine_lists(sfbay_city_names, sc_county_city_names)

    # sanity check
    print(f'sanity check on sfbay & sc county city names data:\n\n{sfbay_city_names}')

    print(f'\nThere are {len(sfbay_city_names)} cities')


    sfbay_city_names = add_dash_delimiter_in_bw_each_word_of_city_names(sfbay_city_names)
    
    # sanity check
    print(f"List of SF Bay city names parsed from wiki tables:{sfbay_city_names}")

    # parse city names data based on the full list of cities from the wikipedia pages
    df = parse_city_names_from_listing_URL(df, sfbay_city_names)

    # clean city names (e.g., delete 'Nan' values, etc.)
    df['cities'] = clean_city_names(df, 'cities')

    # remove dashes from city names col:
    df['cities'] = remove_dashes_from_words_in_col(df, 'cities')
    

    df['cities'] = capitalize_each_word_in_row_for_col(df, 'cities')


    # df = clean_split_city_names(df, address_criteria, neighborhood_criteria, split_city_delimiters, incorrect_city_names, cities_not_in_region, cities_that_need_extra_cleaning)
    # sanity check
    print(f"Sanity check--after cleaning the city names, let's examine some of the cleaned data:\n{df.cities.value_counts().tail(10)}")



    ## Remove a few columns that are irrelevant to rental price and in which we do not want to store in the SQL table:
    # remove 'Unnamed' columns, which might be imported errouneously via pd.read_csv()
    df = remove_col_with_given_starting_name(df, 'Unnamed')

    # remove listing_urls column since we do not want to store these data into the SQL Server table-- why?: a.) because listing urls are not relevent to rental prices and b.) the listing urls quickly become invalid or dead links, so we have no need to refer back to them at this stage in the webscraping project.
    df = remove_col_with_given_starting_name(df, 'listing_urls')

    # remove listing_descrip col since we do not want to store these data in SQL table either;
    df = remove_col_with_given_starting_name(df, 'listing_descrip')

    
    ## convert specific cols to indicator variables -- # since there are many cols we want to transform to indicator variables, it's easier to simply drop the few cols that comprise str (aka, object) data 
    cols_to_indicators = df.drop(columns =['ids', 'cities', 'attr_vars', 'sqft', 'prices', 'bedrooms', 'bathrooms', 'date_posted', 'date_of_webcrawler']) 
    cols_to_indicators_lis = list(cols_to_indicators.columns)   # convert col names to list
    df = transform_cols_to_indicators(df, cols_to_indicators_lis) # transform the cols to uint8 

    cols_to_indicators = [] # free memory

    # also, transform kitchen, flat and land  cols separately, since they tend to otherwise convert to float after importing from csv files:
    cols_to_indicators2 = list(df[['kitchen', 'flat', 'land']].columns)   # get list of these 3 cols
    df = transform_cols_to_indicators(df, cols_to_indicators2)   # transform the cols to uint8 

    cols_to_indicators2 = []

    ## convert specific cols to integer data type:
    # specify a list of cols to convert to integer
    cols_to_int = df[['prices', 'bedrooms', 'ids', 'sqft']]
    # cols_to_int = df[['prices', 'bedrooms', 'sqft']]
    cols_to_int_lis = list(cols_to_int.columns)  # use a list of col names
    df = transform_cols_to_int(df, cols_to_int_lis)   # convert list of cols to int 

    cols_to_int = [] # free memmory

    print(f"\n\nSanity check on bathrooms data, **before** addit'l data cleaning:\n{df['bathrooms'].value_counts()}\n\n")



    ## clean bathrooms data by replacing the 'split' and 'shared' string values:
    df['bathrooms'] = transform_shared_and_split_to_ones(df, 'bathrooms')
    # sanity check

    # replace any ambiguous values for bathrooms data--such as '9+' with empty strings (ie, essentially nulls) 
    df['bathrooms']  = replace_ambiguous_data_with_empty_str(df, 'bathrooms')


    print(f"\n\nSanity check on bathrooms data, **after** addit'l data cleaning:\n{df['bathrooms'].value_counts()}\n\n")


    # remove null ids, city names, & bathrooms data, etc, given some data cleaning might have resulted in additional null rows:
    df = remove_nulls_list(df, list_cols_to_remove_nulls) 
    # sanity check
    print(f"\nRemaining ids & bathroom data nulls: \n{df[['ids', 'bathrooms']].isnull().sum()}\n\n")
    print(f"Dataset after most data cleaning:\n{df.info()}")


    # ## remove any bathroom or bedroom nulls:
    # df = remove_bedroom_and_br_nulls(df)
    # # sanity check

    # # ## transform bathrooms data & listing ids to float--Why float?: Because some listings specify half bathrooms--e.g., 1.5 denotes one-and-half bathrooms. Re: ids, integer data type not store the entire id value due to maximum (byte) storage constraints. 
    # # remove any whitespace
    # df['bedrooms'] = df['bedrooms'].apply()
    
    # # convert bathrooms data to float:
    df['bathrooms'] = transform_cols_to_float(df, 'bathrooms')    
    # # sanity check on bathrooms data
    print(f"Bathrooms data:\n{df['bathrooms']}")

    # round bathrooms data to nearest decimal point:
    df['bathrooms'] = round_to_nearest_decimal_pt(df, 'bathrooms')

    # # remove any remaining ids & bathrooms data nulls, due to problems converting to float:
    # df = remove_nulls_list(df, more_cols_to_remove_nulls_lis)   


    #sanity check
    print(f"\nSanity check on ids value counts:\n{df['ids'].value_counts()}\n\n")
    print(f"\nSanity check on bathrooms  data value counts:\n{df[ 'bathrooms'].value_counts()}\n\n")



    # sanity check
    print(f"Sanity check--The remaining columns in the dataset are:\n {df.columns}")
    print(f"And the remaining data are:{df}")

    # ## run de-duplication proces once more, having transformed the data to float: 
    # df = deduplicate_df(df)

    # sanity check
    clist_duplicate_ids_check = df[df.duplicated("ids", keep= False)] 
    print(f"\n\nThere should be no remaining duplicate listing ids (ie, 0 rows):\n{clist_duplicate_ids_check.shape[0]}\n") # sanity check --check that number of duplicate rows is false (ie, wrt duplicate listing ids)


    # NB: after completing all above data filtering and cleaning procedures, proceed to step #5: ie, 5) insert filtered and cleaned pandas' df into SQL rental table
    ## 5.) Pandas df to SQL data pipeline--ie, INSERT the filtered data (*ie, unique data that has not been inserted yet) 

    df = deduplicate_df(df)
    
    #  Execute data pipeline--Ingest data from date-filtered pandas' dataframe to SQL server--data pipeline: 
    SQL_db.insert_df_to_SQL_ETL(df, region_code)




if __name__=="__main__":
    main()

# imports-- file processing & datetime libraries
import os
import glob
import datetime
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

# 1c) Import all available recursively search parent direc to look up CSV files within subdirectories
def recursively_import_all_CSV_and_concat_to_single_df(parent_direc:str, region_code: str, fn_regex=r'*.csv'):
    """Recursively search directory of scraped data for given region, and look up all CSV files.
    Then, import all CSV files to a single Pandas' df using pd.concat()"""
    path =  parent_direc # specify parent path of directories containing the scraped rental listings CSV data -- NB: use raw text--as in r'path...', or can we use the double-back slashes to escape back-slashes??
    # use backslashes to separate the parent direc from the region code
    backslashes_separator = "\\\\"
    # add *region code* to parent direc so we can recursively search the scraped data for that specific region:
    path = f'{path}{backslashes_separator}{region_code}' # add region code to path

    # recursively search path for CSV files, and concat to single DataFrame:
    df_concat = pd.concat((pd.read_csv(file, # import each CSV file
                                        sep=',', encoding = 'utf-8'  # assume standard CSV (ie, comma separated) format and use utf-8 encoding
                                        ) for file in glob.iglob( # iterate over each CSV file in path
                                            os.path.join(path, '**', fn_regex), 
                                            recursive=True)), ignore_index=True)  # recursively iterate over each CSV file in path, and use os.path.join to help ensure this concatenation is OS independent

    return df_concat

# 1d) Verify whether *any* data have been scraped for given region 
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

        ## sanity check:
        print(f"\nLatest date of scraped data inserted into the SQL table:\n{max_date}")
        return max_date


    # 5.) insert filtered and cleaned pandas' df into SQL table
    def insert_df_to_SQL_ETL(self, df):
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

        cursor.fast_executemany = True  # speed up data ingesting by reducing the numbers of calls to server for inserts
        
        # insert scraped data from df to SQL table-- iterate over each row of each df col via .itertuples() method

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


        # # sanity check-- ensure some data has been inserted into new SQL table
        sql_table_count_records = conn.execute("""SELECT COUNT(*) FROM rental;""").fetchall()
        print(f"\nThe number of total records currently stored in the SQL table is:\n{sql_table_count_records[0]}\n")     
        
        sql_query_for_record_samples = conn.execute("""SELECT TOP 3 * FROM rental;""").fetchall() # check out several of the records
        print(f"\nA few of the inserted records are: {sql_query_for_record_samples}")

        cursor.close()
        conn.close()    
    

# 2) b.) Transform query results to string
def datetime_col_to_str_of_datetime(df: DataFrame, datetime_col:str):
    """Given datetime col from pandas' DataFrame, transform to a string of the datetime value."""
    return df[datetime_col].head(1).astype(str).reset_index().loc[0, datetime_col] 


# 3.) a.) Transform Pandas' dataframe 'date_posted' column to datetime:
def transform_cols_to_datetime(df: DataFrame, col_to_convert:str):
    """Transform relevant column(s) to datetime using pd.to_datetime() method"""
    return pd.to_datetime(df[col_to_convert], infer_datetime_format=True) # format= '%Y-%m-%d-%H:%M'


# 3.) b.) filter Pandas' dataframe by latest date of date_posted found via MAX( SQL query
def filter_df_since_specified_date(df: DataFrame, target_date: str):
    """Filter the imported scraped dataset to all data newer than the specified date (as determined via the MAX(posted_date) query)."""
    if target_date != "None":  # account for scenario in which *no data* has yet been inserted into the SQL table
        df = df.loc[df['date_posted'] > target_date]  # filter to data greater than specified date
    else:   # ie, target_date == "None"
        pass  # do not apply filter, since no data has yet been inserted into SQL table
    return df


# 4.) Perform all additional data cleaning procedures to prep the dataframe prior to initiating the pyodbc pandas' to SQL Server data pipeline inserts:

def deduplicate_df(df: DataFrame):
    """Remove duplicate rows based on listing ids (keep last ones since we might want to examine the length of time a given rental listing has been posted."""
    return df.drop_duplicates(keep='last', subset = ['ids'])


def remove_nulls_list(df, list_of_cols):
    """Remove rows that do not have price, city name, kitchen, sqft, or listing ID data, as these are essential variables in this rental listings dataset."""
    return df.dropna(subset=list_of_cols)

def clean_split_city_names(df, address_critera: list, neighborhood_criteria:list, split_city_delimiters: list, incorrect_city_names:dict, cities_not_in_region:dict, cities_that_need_extra_cleaning:dict):
    """Clean city names data in several ways:
    a.) Remove extraneous address & neighborhood data placed in the city names HTML object, such as 'Rd', 'Blvd', or 'Downtown'.
    b.) Unsplit city names data that are split via delimiters such as ',' & '/' .
    c.) Replace abbreviated or mispelled city names, and remove city names that do not exist within the SF Bay Area (e.g., 'Redding').
    d.) Remove any digits/integers within the city names data--ie, by using a '\d+' regex as the argument of str.replace() and replace it with empty strings.
    e.) Remove any city names records that are left with merely empty strings (ie, the other steps removed all data for that given cities record).
    f.) Remove any whitespace to avoid the same city names from being treated as different entities by Pandas, Python, or SQL. 
    g.) Use str.capwords() to capitalize words (ie, excluding apostrophes).
    h.) Replace city names that are mispelled after having removed various street and neighborhood substrings such as 'St' or 'Ca'--e.g., '. Helena' should be 'St. Helena'. """
    # specify extraneous street & address data (e.g., 'Rd') that we want to remove from the city names column:
    addr_criteria = '|'.join(address_critera) # Join pipe ('|') symbols to address list so we can str.split() on any one of these criteria (ie, 'or' condition splitting on each element separated by pipes):
    # specify extraneous neighborhood criteria we should also remove from col
    nbhood_criteria = '|'.join(neighborhood_criteria) # remove neighborhood names as well as state abbreviation (shown on website as 'Ca') that is shown without the usual comma delimiter!
    # b.) specify delimiters we need to refer to un-split city names:
    split_city_delimiters = '|'.join(split_city_delimiters) # join pipes to delimiters so we can use str.split() based on multiple 'or' criteria simultaneously
    # clean city names data by removing extraneous address & neighborhood data, and unsplitting city names based on ',' & '\' delimiters
    df['cities'] =  df['cities'].str.split(addr_criteria).str[-1].str.replace(nbhood_criteria, '', case=True).str.lstrip()
    df['cities'] = df['cities'].str.split(split_city_delimiters).str[0] #unsplit city names based on comma or forward-slash delimiters
    # c.) replace specific abbreviated or mispelled city names, and remove cities that are not actually located in the sfbay region:
    df = df.replace({'cities':incorrect_city_names}) # replace mispelled & abbreviated city names
    df = df.replace({'cities':cities_not_in_region})  # remove (via empty string) cities that are not actually located in the sfbay region
    # d.) Remove digits/integer-like data from cities column:
    df['cities'] = df['cities'].str.replace('\d+', '')  # remove any digits by using '/d+' regex to look up digits, and then replace with empty string
    # e.) Remove any rows that have empty strings or null values for cities col (having performed the various data filtering and cleaning above)
    df = df[df['cities'].str.strip().astype(bool)] # remove rows with empty strings (ie, '') for cities col 
    df = df.dropna(subset=['cities']) # remove any remaining 'cities' null records
    # f.) Remove whitespace
    df['cities'] = df['cities'].str.strip() 
    # g.) capitalize the city names using str.capwords() 
    df['cities'] = df['cities'].str.split().apply(lambda x: [val.capitalize() for val in x]).str.join(' ')
    # h) Replace city names that are mispelled after having removed various street and neighborhood substrings such as 'St' or 'Ca'--e.g., '. Helena' should be 'St. Helena' & 'San los' should be 'San Carlos'. Also, remove any non-Bay Area cities such as Redding:
    df = df.replace({'cities':cities_that_need_extra_cleaning})
    # i) Remove any remaining empty strings or null records
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
    df[col_to_transform] = df[col_to_transform].astype('object') 
    bedroom_replace_criteria = ['shared', 'split']
    bedroom_replace_criteria = '|'.join(bedroom_replace_criteria) # join pipe symbols so we can use str.replace() on multiple 'or' conditions simultaneously 
    return df[col_to_transform].str.replace(bedroom_replace_criteria,'1')

# replace any ambiguous values for bathrooms data--such as '9+' with empty strings (ie, essentially nulls) 
def replace_ambiguous_data_with_empty_str(df: DataFrame, col_to_transform: str):
    """Replace ambiguous rows of data (ie, any containing a plus sign) for bathrooms col with empty strings"""
    return df[col_to_transform].str.replace(r'\+', '')  # use str.replace() to use a regex to search for plus signs, and in effect remove these by replacing them with empty strings 

def remove_bedroom_and_br_nulls(df: DataFrame):
    return df.dropna(subset=['bedrooms', 'bathrooms'])


def transform_cols_to_float(df: DataFrame, col_to_transform: str):
    return df[col_to_transform].astype('float32')


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
        # 'Tacoma, WA':'https://seattle.craigslist.org/tac/',
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

    # prase region code from homepage url of selected region:
    region_code = parse_region_code_from_craigslist_URL(region_URL)

    # sanity check on region code:
    print(f'\nRegion code: {region_code}\n')

    # # 1) Import all scraped rental listings data from given region:
    # specify path to scraped data
    # get root directory of project by getting parent directory (ie, using os's .pardir method) 
    parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    
    # specify folder of webcrawler's scraped data
    scraped_data_folder = 'scraped_data'

    # get full path to scraped_data, by referring to root directory (ie, parent_directory) & scraped_data_folder
    scraped_data_parent_path = os.path.join(parent_directory, scraped_data_folder)

    print(f'The directory of the webcrawler scraped data is:\n{scraped_data_parent_path}\n\n')
    
    try:   
        # attempt to import and concat scraped data for given region:
        df = recursively_import_all_CSV_and_concat_to_single_df(scraped_data_parent_path, region_code)

        # 
        print("\nScraped data for region exists. ETL pipeline can proceed\n")

        # sanity check on imported data
        print(f"Sanity check--Some info of the imported scraped data: {df.info()}") # sanity check: examine size of dataset, columns, etc.

    except ValueError:   # account for potential Valueerror--ie, if there is *no* available scraped data for the given region
        print("\nSorry, there is no data available for the selected region.\n")


    ## 2) Determine the last date of listings data stored in SQL table, so we can filter the dataset before inserting the data:

    # specify path to json file containing SQL configuration/username data
    sql_config_path = "D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\SQL_config\\config.json" 

    SQL_db = SQL_Database(sql_config_path)  # NB: initialize class and pass in path to the json SQL configuration file 
    
    ## 2a.) specify query to select the latest date based on date_posted:
    # sql_query = "SELECT MAX(date_posted) AS latest_date FROM rental;"
    # determine last date of listings records stored in SQL table, **for given region**
    # latest_date = SQL_db.determine_latest_date(sql_query, region_code)

    latest_date = SQL_db.determine_latest_date(region_code)


    ## 2) b.) Transform query results to string:

    # specify name of df (ie, latest_date) containing the query results) and datetime col to transform
    latest_date, dt_col = latest_date, 'latest_date' 
    #apply function using the 2 arguments shown above
    latest_date_str = datetime_col_to_str_of_datetime(latest_date, dt_col)
    # sanity check
    print(f"\n\nThe latest date among the scraped data stored in the SQL table is:\n{latest_date_str}")

    ## 3.) Filter pandas' df dataset to data after last data inserted into SQL table--ie, the latest_date_str whose value we initially obtained from the MAX(date_posted) query
    
    ## NB: convert specific cols to datetime before filtering (for skae of consistency and replicability of this data pipeline)
    df['date_of_webcrawler'] =  transform_cols_to_datetime(df,'date_of_webcrawler')
    df['date_posted'] = transform_cols_to_datetime(df,'date_posted')
    #sanity check
    print("Sanity check on datetime cols: {df[['date_posted', 'date_of_webcrawler']].head()}")

    # filter df by SQL table query date--ie, via latest_date_str:
    df = filter_df_since_specified_date(df, latest_date_str)
    # sanity check:
    print(f"The newest scraped data not stored in the SQL table is--\n*NB: this should be an empty df if we have already stored all of the df's data into the SQL table*: \n\n{df['date_posted']}")

    ## 4.)  Data cleaning:

    ## remove any rows with null listing ids, prices, sqft, or city names   
    list_cols_to_remove_nulls = ['prices', 'ids', 'sqft', 'kitchen', 'cities']  
    df = remove_nulls_list(df, list_cols_to_remove_nulls)

    # sanity check
    print(f"Remaining price, city name, sqft, kitchen, & listing id nulls: \n{df[list_cols_to_remove_nulls].isnull().sum()}")

    ## clean split city names and clean abbreviated or incorrect city names:
    # specify various address and street name that we need to remove from the city names
    address_criteria = ['Boulevard', 'Blvd', 'Road', 'Rd', 'Avenue', 'Ave', 'Street', 'St', 'Drive', 'Dr', 'Real', 'E Hillsdale Blvd', 'Ln', '-brookview', 'Lincoln Hill-'] 

    # specify various extraneous neighborhood names such as 'Downtown' 
    neighborhood_criteria = ['Downtown', 'Central/Downtown', 'North', 'California', 'Ca.', 'Bay Area', 'St. Helena', 'St', 'nyon', 
    'Jack London Square', 'Walking Distance To', 'El Camino', 'Mendocino County', 'San Mateo County', 'Alameda County', 'Rio Nido Nr', 'Mission Elementary', 
    'Napa County', 'Golden Gate', 'Jennings', 'South Lake Tahoe', 'Tahoe Paradise', 'Kingswood Estates', 'South Bay', 'Skyline', 'San Antonio Tx', 
    'East Bay', 'Morton Dr', 'Cour De Jeune', 
    'West End', 'Wikiup', 'Rotary Way', 'Old City', 'Greenwich Cir. Fremont', 'Mission District'] 

    # specify what delimiters we want to search for to unsplit the split city names data:
    split_city_delimiters =  [',', '/', ' - ', '_____', '#']

    # specify dictionary of abbreviated & mispelled cities:
    incorrect_city_names = {'Rohnert Pk':'Rohnert Park', 'Hillsborough Ca': 'Hillsborough','Fremont Ca':'Fremont', 'South Sf': 'South San Francisco', 'Ca':'', 'East San Jose':'San Jose', 'Vallejo Ca':'Vallejo', 'Westgate On Saratoga .':'San Jose', 'Bodega':'Bodega Bay', 'Briarwood At Central Park':'Fremont', 'Campbell Ca':'Campbell', 'Almaden':'San Jose', '.':'', 'East Foothills':'San Jose', 'Lake County':'', 'West End':'Alameda', 'Redwood Shores':'Redwood City', 'Park Pacifica Neighborhood':'Pacifica', 'Pt Richmond':'Richmond'}

    # specify dictionary of cities that are not located in sfbay (ie, not located in the region):
    cities_not_in_region = {'Ketchum':'', 'Baypoinr':'', 'Quito': '', 'Redding':'', 'Bend' :'', 'Near Mount Lassen':'', 'Tracy':'', 'Middletown':'', 'Truckee':'', 'Midtown Sacramento':'', 'Tro Valley-':'', 'Neighborhood':''}

    # specify dictionary of city names that are mispelled after having removed various street and neighborhood substrings:
    cities_that_need_extra_cleaning = {'. Helena': 'St. Helena', '. Helena Deer Park': 'St. Helena', 'San Los':'San Carlos', 'Tro Valley':'Castro Valley', 'Rohnert Pk':'Rohnert Park',
    'Pbell':'Campbell', 'Pbell Ca':'Campbell', 'American Yon':'American Canyon', 'Millbrae On The Burlingame Border':'Millbrae', 'Ockton Ca': 'Stockton', '. Rohnert Park': 'Rohnert Park', 'Udio Behind Main House':'', '***---rohnert Park':'Rohnert Park',
    'Meadow Ridge Cir':'San Jose', 'Irvington High Area':'Fremont', 'Interlaken-watsonville':'Interlaken', 'Dimond District':'Oakland', 'Apt':'', 'Neighborhood':''}

    # clean city names data:
    df = clean_split_city_names(df, address_criteria, neighborhood_criteria, split_city_delimiters, incorrect_city_names, cities_not_in_region, cities_that_need_extra_cleaning)
    # sanity check
    print(f"Sanity check--after cleaning the city names, let's examine some of the cleaned data: {df.cities.value_counts().tail(10)}")
        
    ## convert specific cols to indicator variables -- # since there are many cols we want to transform to indicator variables, it's easier to simply drop the few cols that comprise str (aka, object) data 
    cols_to_indicators = df.drop(columns =['ids', 'listing_urls', 'cities', 'attr_vars', 'listing_descrip', 'sqft', 'prices', 'bedrooms', 'bathrooms', 'date_posted', 'date_of_webcrawler']) 
    cols_to_indicators_lis = list(cols_to_indicators.columns)   # convert col names to list
    df = transform_cols_to_indicators(df, cols_to_indicators_lis) # transform the cols to uint8 

    # also, transform kitchen, flat and land  cols separately, since they tend to otherwise convert to float after importing from csv files:
    cols_to_indicators2 = list(df[['kitchen', 'flat', 'land']].columns)   # get list of these 3 cols
    df = transform_cols_to_indicators(df, cols_to_indicators2)   # transform the cols to uint8 

    ## convert specific cols to integer data type:
    # specify a list of cols to convert to integer
    cols_to_int = df[['prices', 'bedrooms', 'ids', 'sqft']]
    cols_to_int_lis = list(cols_to_int.columns)  # use a list of col names
    df = transform_cols_to_int(df, cols_to_int_lis)   # convert list of cols to int 

    ## clean bathrooms data by replacing the 'split' and 'shared' string values:
    df['bathrooms'] = transform_shared_and_split_to_ones(df, 'bathrooms')
    #sanity check
    print(f"Sanity check on bathrooms data:\n{df['bathrooms'].value_counts()}")

    # replace any ambiguous values for bathrooms data--such as '9+' with empty strings (ie, essentially nulls) 
    df['bathrooms']  = replace_ambiguous_data_with_empty_str(df, 'bathrooms')
    # sanity check
    print(f"New value counts for bathrooms data--having cleaned ambiguous records: \n{df['bathrooms'].value_counts()}")

    ## remove any bathroom or bedroom nulls:
    df = remove_bedroom_and_br_nulls(df)
    # sanity check
    print(f"\nRemaining bedroom & bathroom nulls: \n{df[['bedrooms', 'bathrooms']].isnull().sum()}\n\n")

    ## transform bathrooms data & listing ids to float--Why float?: Because some listings specify half bathrooms--e.g., 1.5 denotes one-and-half bathrooms. Re: ids, integer data type not store the entire id value due to maximum (byte) storage constraints. 
    # convert bathrooms data to float:
    df['bathrooms'] = transform_cols_to_float(df, 'bathrooms')    
    # convert ids to float:
    df['ids'] = transform_cols_to_float(df, 'ids')    
    #sanity check
    print(f"\nSanity check on data type of ids & bathrooms data: {df[['bathrooms', 'ids']].info()}\n\n")

    ## deduplicate based on listing ids--ie, since each rental listing has unique ids
    df = deduplicate_df(df)
    # sanity check
    clist_duplicate_ids_check = df[df.duplicated("ids", keep= False)] 
    print(f"There should be no remaining duplicate listing ids (ie, 0 rows): \n{clist_duplicate_ids_check.shape[0]}") # sanity check --check that number of duplicate rows is false (ie, wrt duplicate listing ids)
    clist_duplicate_ids_check = []  # free memory

    ## Remove a few columns that are irrelevant to rental price and in which we do not want to store in the SQL table:
    # remove 'Unnamed' columns, which might be imported errouneously via pd.read_csv()
    df = remove_col_with_given_starting_name(df, 'Unnamed')

    # remove listing_urls column since we do not want to store these data into the SQL Server table-- why?: a.) because listing urls are not relevent to rental prices and b.) the listing urls quickly become invalid or dead links, so we have no need to refer back to them at this stage in the webscraping project.
    df = remove_col_with_given_starting_name(df, 'listing_urls')

    # remove listing_descrip col since we do not want to store these data in SQL table either;
    df = remove_col_with_given_starting_name(df, 'listing_descrip')

    # sanity check
    print(f"Sanity check--The remaining columns in the dataset are:\n {df.columns}")

    # NB: after completing all above data filtering and cleaning procedures, proceed to step #5: ie, 5) insert filtered and cleaned pandas' df into SQL rental table
    ## 5.) Pandas df to SQL data pipeline--ie, INSERT the filtered data (*ie, unique data that has not been inserted yet)   

    #  Execute data pipeline--Ingest data from date-filtered pandas' dataframe to SQL server--data pipeline: 
    SQL_db.insert_df_to_SQL_ETL(df)


if __name__=="__main__":
    main()

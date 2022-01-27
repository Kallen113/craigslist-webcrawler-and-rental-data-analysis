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

"""
NB: see following links for useful documentation and examples on importing CSV files into SQL Server via Python:
<https://stackoverflow.com/questions/39899088/import-csv-file-into-sql-server-using-python>

Import a CSV File to SQL Server using Python(2021)
<https://datatofish.com/import-csv-sql-server-python/#:~:text=1%20Prepare%20the%20CSV%20File.%20To%20begin%2C%20prepare,as%20well%20as%20...%206%20Perform%20a%20Test>

"""
# import scraped craigslist rental listings data from CSV files to single Pandas' df 
# recursively search parent direc to look up CSV files within subdirectories
def recursively_import_all_CSV_and_concat_to_single_df(parent_direc, fn_regex=r'*.csv'):
    """Recursively search parent directory, and look up all CSV files.
    Then, import all CSV files to a single Pandas' df using pd.concat()"""
    path =  parent_direc # specify parent path of directories containing the scraped rental listings CSV data -- NB: use raw text--as in r'path...', or can we use the double-back slashes to escape back-slashes??
    df_concat = pd.concat((pd.read_csv(file) for file in glob.iglob(
        os.path.join(path, '**', fn_regex), 
        recursive=True)), ignore_index=True)  # os.path.join helps ensure this concatenation is OS independent
    return df_concat

# 2.) Determine latest data of scraped data inserted into SQL table 
class SQL_Database:
    def __init__(self):

        with open("D:\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\Rentals\\SQL_config\\config.json",'r') as fh:
            config = json.load(fh)  # open config.json file, which contains all SQL database credentials--ie, username, password, database name, etc. 

        self.driver = config['driver']
        self.server = config['server']
        self.database = config['database']
        self.username = config['username']
        self.password = config['password']
        print(f"Sanity check on database name (ie, based on the json configurations file:/n{self.database}")# sanity check

    # 2 a) Perform SQL query on date_posted col to determine the most recent date of data stored in the table  
    def determine_latest_date(self, query):
        """Calculate the most recent date of rental listings data that we have inserted into the SQL rental table"""
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
            print("Python was not able to connect to SQL server database and. Please try again.") 

        # initialize cursor so we can execute SQL code
        cursor = conn.cursor() 

        # specify SQL query
        query = query 

        # perform query, and convert query results to Pandas' df
        max_date = pd.read_sql(query, conn)

        cursor.close()
        conn.close()

        ## sanity check:
        print(f"Latest date of scraped data inserted into the SQL table:\n{max_date}")
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
            print("Python was not able to connect to SQL server database and. Please try again.") 

        # initialize cursor so we can execute SQL code
        cursor = conn.cursor() 

        cursor.fast_executemany = True  # speed up data ingesting by reducing the numbers of calls to server for inserts

        # convert all variables from dataframe to str to avoid following SQL Server pyodbc error: 'ProgrammingError: ('Invalid parameter type.  param-index=2 param-type=function', 'HY105')'
        # df = df.astype(str) # convert all df variables to str for ease of loading data into SQl Server table
        
        # insert scraped data from df to SQL table-- iterate over each row of each df col via .itertuples() method

        q_mark_list = ['?']*len(df.columns)

        # # unpack list as string, and join() commas to each '?' char, so we can use these as placeholders in the SQL query
        q_mark_str = ','.join(q_mark_list)
        
        ## NB: create '?' char marks as SQL placeholders for values (to help prevent SQL injections)--we determine the number of needed '?' chars by looking up the # of cols (ie, len()) of the dataframe), and use .join() to have each question mark separated by commas: refers to the len() of the df (ie, the number of cols from the df)  
        q_mark_str = ','.join('?'*len(clist_rental.columns))  

        # insert data by itereating over each row from df:

        try:  # attempt to make data inserts into SQL table (*excepting a database error)
            # specify INSERT INTO SQL statement--iterate over each row in df, and insert into SQL database:
            for row in df.itertuples():  # iterate over each row from df
                cursor.execute(f"""INSERT INTO rental (listing_id, sqft, city, price, bedrooms, bathrooms, attr_vars,
                date_of_webcrawler, kitchen, date_posted, region, sub_region, cats_OK, dogs_OK, wheelchair_accessible,laundry_in_bldg, no_laundry, 
                washer_and_dryer, washer_and_dryer_hookup, laundry_on_site, full_kitchen, dishwasher, refrigerator,
                oven,flooring_carpet, flooring_wood, flooring_tile, flooring_hardwood, flooring_other,apt_type, in_law_apt_type, condo_type, townhouse_type, cottage_or_cabin_type, single_fam_type, duplex_type, is_furnished, attached_garage,
                detached_garage, carport, off_street_parking, no_parking, EV_charging, air_condition, no_smoking) 
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
                row.apt_type, 
                row.in_law_apt_type,
                row.condo_type,
                row.townhouse_type,
                row.cottage_or_cabin_type,
                row.single_fam_type, 
                row.duplex_type,
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

            print("We have inserted the records from the DataFrame, and the SQL Server table has been updated successfully.")
        
        except pyodbc.Error as e: #account for possible errors while inserting dataframe into SQL table
            print("An error occurred while inserting the DataFrame records into the SQL Server table")
            quit()   # terminate SQL script


        # # sanity check-- ensure some data has been inserted into new SQL table
        sql_table_count_records = conn.execute("""SELECT COUNT(*) FROM rental;""").fetchall()
        print(f"The number of records stored in the SQL table is: {sql_table_count_records[0]}")     
        
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
    """Transform relevant column(s) to datetime using pd.to_datetime() method,
    and parse as a datetime format as follows: MMDDYYYY"""
    df[col_to_convert] = pd.to_datetime(
        df[col_to_convert], format= '%Y-%m-%d-%H:%M'
        ) 
    return df


# 3.) b.) filter Pandas' dataframe by latest date of date_posted found via MAX( SQL query
def filter_df_since_specified_date(df: DataFrame, target_date: str):
    """Filter the imported scraped dataset to all data newer than the specified date (as determined via the MAX(posted_date) query)."""
    df = df.loc[df.date_posted > target_date]  # filter to data greater than specified date
    return df


# 4.) Perform all additional data cleaning procedures to prep the dataframe prior to initiating the pyodbc pandas' to SQL Server data pipeline inserts:

def deduplicate_df(df: DataFrame):
    """Remove duplicate rows based on listing ids"""
    return df.drop_duplicates(keep='first', subset = ['ids'])


def remove_nulls_list(df, list_of_cols):
    """Remove rows that do not have price, city name, kitchen, sqft, or listing ID data, as these are essential variables in this rental listings dataset."""
    return df.dropna(subset=list_of_cols)

def clean_split_city_names(df, address_critera: list, neighborhood_criteria:list, split_city_delimiters: list, incorrect_city_names:dict, cities_not_in_region:dict, cities_that_need_extra_cleaning:dict):
    """Clean city names data in several ways:
    a.) Remove extraneous address & neighborhood data placed in the city names HTML object, such as 'Rd', 'Blvd', or 'Downtown'.
    b.) Unsplit city names data that are split via ',' & '/' delimiters.
    c.) Replace abbreviated or mispelled city names, and remove city names that do not exist within the SF Bay Area (e.g., 'Redding').
    d.) Remove any digits/integers within the city names data--ie, by using a '\d+' regex as the argument of str.replace() and replace it with empty strings.
    e.) Remove any city names records thast are left with merely empty strings (ie, the other steps removed all data for that given cities record).
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
    # df['cities'] = df['cities'].str.lower() # transform all records to lower-case, for ease of cleaning the data
    df = df.replace({'cities':cities_that_need_extra_cleaning})
    return df



def transform_cols_to_indicators(df: DataFrame, list_of_cols: list):
    """ Transform relevant attribute columns to numeric, and specify NaNs for any missing or non-numeric data."""
    df[list_of_cols] = df[list_of_cols].astype('uint8', errors='ignore') # convert any missing data to NaN 
    print(f"Sanity check: The data types of {list_of_cols} are now: \n{df[list_of_cols].dtypes}") # sanity check on columns' data types
    return df


def transform_cols_to_int(df, list_of_cols_to_num):
    """ Transform relevant attribute columns to numeric.
    NB: Since the scraped 'prices' data can contain commas, 
    we need to use str.replace(',','') to remove them before converting to numeric."""
    df['prices'] = df['prices'].str.replace(",","") # remove commas from prices data (e.g.: '2500' vs '$2,500')
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
    return df[col_to_transform].astype('float')


def remove_col_with_given_starting_name(df, col_starting_name: str):
    """Remove each column from df that has a given starting name substring."""
    return df.loc[:, ~df.columns.str.startswith(col_starting_name)] 


# NB: after completing all above data filtering and cleaning procedures, then proceed to step #5: ie, 5) insert filtered and cleaned pandas' df into SQL rental table


def main():
    # # 1) Import all scraped rental listings data -- NB: in our case, we have various SF Bay Area listings data
    scraped_data_path = r"D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\scraped_data\\sfbay"
    clist_rental = recursively_import_all_CSV_and_concat_to_single_df(scraped_data_path)
    print(f"Sanity check--Some info of the imported scraped data: {clist_rental.info()}") # sanity check-examine size of dataset, columns, etc.


    ## 2) Determine the last date of listings data stored in SQL table, so we can filter the dataset before inserting the data:

    # initialize an instance of the SQL_Database() class, so we can perform methods from this class, and implement SQL code to the rental table 
    SQL_db = SQL_Database()  # initialize class

    ## 2a.) specify query to select the latest date based on date_posted:
    sql_query = "SELECT MAX(date_posted) AS latest_date FROM rental;"
    # determine last date of listings records stored in SQL table
    latest_date = SQL_db.determine_latest_date(sql_query)

    ## 2) b.) Transform query results to string:

    # specify name of df and datetime col to transform
    df, dt_col = latest_date, 'latest_date' 
    #apply function using the 2 arguments shown above
    latest_date_str = datetime_col_to_str_of_datetime(df, dt_col)
    # sanity check
    print(f"The latest date among the scraped data stored in the SQL table is:\n{latest_date_str}")

    ## 3.) Filter pandas' df dataset to data after last data inserted into SQL table--ie, the latest_date_str whose value we initially obtained from the MAX(date_posted) query
    
    ## NB: convert specific cols to datetime before filtering (for skae of consistency and replicability of this data pipeline)
    clist_rental['date_of_webcrawler'] =  transform_cols_to_datetime(clist_rental,'date_of_webcrawler')
    clist_rental['date_posted'] = transform_cols_to_datetime(clist_rental,'date_posted')
    #sanity check
    print("Sanity check on datetime cols: {clist_rental[['date_posted', 'date_of_webcrawler']].head()}")

    clist_rental = filter_df_since_specified_date(clist_rental, latest_date_str)

    ## 4.)  Data cleaning:

    ## remove any rows with null listing ids, prices, sqft, kitchen data, or city names   
    list_cols_to_remove_nulls = ['prices', 'ids', 'sqft', 'kitchen', 'cities']  
    clist_rental = remove_nulls_list(clist_rental, list_cols_to_remove_nulls)

    # sanity check
    print(f"Remaining price, city name, sqft, kitchen, & listing id nulls: \n{clist_rental[list_cols_to_remove_nulls].isnull().sum()}")

    ## clean split city names and clean abbreviated or incorrect city names 
    # specify various address and street name that we need to remove from the city names 
    address_criteria = ['Boulevard', 'Blvd', 'Road', 'Rd', 'Avenue', 'Ave', 'Street', 'St', 'Drive', 'Dr', 'Real', 'E Hillsdale Blvd'] 
    # specify various extraneous neighborhood names such as 'Downtown' 
    neighborhood_criteria = ['Downtown', 'Central/Downtown', 'North', 'California', 'Ca.', 'Bay Area', 'St. Helena', 'St', 'nyon', 
    'Jack London Square', 'Walking Distance To', 'El Camino', 'Mendocino County', 'San Mateo County', 'Alameda County', 'Rio Nido Nr', 'Mission Elementary', 
    'Napa County', 'Golden Gate', 'Jennings', 'South Lake Tahoe', 'Tahoe Paradise', 'Kingswood Estates', 'South Bay', 'Skyline', 'San Antonio Tx', 
    'East Bay', 'Morton Dr'] 

    # specify what delimiters we want to search for to unsplit the split city names data:
    split_city_delimiters =  [',', '/']
    # specify dictionary of abbreviated & mispelled cities:
    incorrect_city_names = {'Rohnert Pk':'Rohnert Park', 'Hillsborough Ca': 'Hillsborough', 'South Sf': 'South San Francisco', 'Ca':'', 'East San Jose':'San Jose', 'Vallejo Ca':'Vallejo', 'Westgate On Saratoga .':'San Jose', 'Bodega':'Bodega Bay', 'Briarwood At Central Park':'Fremont', 'Campbell Ca':'Campbell', 'Almaden':'San Jose', '.':'', 'East Foothills':'San Jose', 'Lake County':'', 'West End':'Alameda', 'Redwood Shores':'Redwood City'}

    # specify dictionary of cities that are not located in sfbay (ie, not located in the region):
    cities_not_in_region = {'Ketchum':'', 'Baypoinr':'', 'Quito': '', 'Redding':'', 'Bend' :''}

    # specify dictionary of city names that are mispelled after having removed various street and neighborhood substrings:
    cities_that_need_extra_cleaning = {'. Helena': 'St. Helena', '. Helena Deer Park': 'St. Helena', 'San Los':'San Carlos', 'Tro Valley':'Castro Valley', 'Rohnert Pk':'Rohnert Park',
    'Pbell':'Campbell', 'Pbell Ca':'Campbell', 'American Yon':'American Canyon'}

    # clean city names data:
    clist_rental = clean_split_city_names(clist_rental, address_criteria, neighborhood_criteria, split_city_delimiters, incorrect_city_names, cities_not_in_region, cities_that_need_extra_cleaning)
    # sanity check
    print(f"Sanity check--after cleaning the city names, let's examine some of the cleaned data: {clist_rental.cities.value_counts().tail(10)}")
    
    ## convert specific cols to indicator variables -- # since there are many cols we want to transform to indicator variables, it's easier to simply drop the few cols that comprise str (aka, object) data 
    cols_to_indicators = clist_rental.drop(columns =['ids', 'listing_urls', 'cities', 'attr_vars', 'listing_descrip', 'sqft', 'prices', 'bedrooms', 'bathrooms', 'date_posted', 'date_of_webcrawler']) 
    cols_to_indicators_lis = list(cols_to_indicators.columns)
    cols_to_indicators = [] # free space

    clist_rental = transform_cols_to_indicators(clist_rental, cols_to_indicators_lis)
    cols_to_indicators_lis = [] # free up memory
    # also, transform kitchen var separately, since this tends to otherwise convert to float after importing from csv files:
    clist_rental = transform_cols_to_indicators(clist_rental, 'kitchen')

    ## convert specific cols to integer data type
    # specify a list of cols to convert to integer
    cols_to_int = clist_rental[['prices', 'bedrooms', 'ids', 'sqft']]
    cols_to_int_lis = list(cols_to_int.columns)  # use a list of col names
    cols_to_int = [] # free up memory
    clist_rental = transform_cols_to_int(clist_rental, cols_to_int_lis)  # convert list of cols to int

    ## clean bathrooms data by replacing the 'split' and 'shared' string values:
    clist_rental['bathrooms'] = transform_shared_and_split_to_ones(clist_rental, 'bathrooms')
    #sanity check
    print(f"Sanity check on bathrooms data:\n{clist_rental['bathrooms'].value_counts()}")

    # replace any ambiguous values for bathrooms data--such as '9+' with empty strings (ie, essentially nulls) 
    clist_rental['bathrooms']  = replace_ambiguous_data_with_empty_str(clist_rental, 'bathrooms')
    # sanity check
    print(f"New value counts for bathrooms data--having cleaned ambiguous records: \n{clist_rental['bathrooms'].value_counts()}")

    ## remove any bathroom or bedroom nulls:
    clist_rental = remove_bedroom_and_br_nulls(clist_rental)
    # sanity check
    print(f"Remaining bedroom & bathroom nulls: \n{clist_rental[['bedrooms', 'bathrooms']].isnull().sum()}")

    ## transform bathrooms data & listing ids to float--Why float?: Because some listings specify half bathrooms--e.g., 1.5 denotes one-and-half bathrooms. Re: ids, integer data type not store the entire id value due to maximum (byte) storage constraints. 
    # convert bathrooms data to float:
    clist_rental['bathrooms'] = transform_cols_to_float(clist_rental, 'bathrooms')    
    # convert ids to float:
    clist_rental['ids'] = transform_cols_to_float(clist_rental, 'ids')    
    #sanity check
    print(f"Sanity check on data type of ids & bathrooms data: {clist_rental[['bathrooms', 'ids']].info()}")

    ## deduplicate based on listing ids--ie, since each rental listing has unique ids
    clist_rental = deduplicate_df(clist_rental)
    # sanity check
    clist_duplicate_ids_check = clist_rental[clist_rental.duplicated("ids", keep= False)] 
    print(f"There should be no remaining duplicate listing ids (ie, 0 rows): \n{clist_duplicate_ids_check.shape[0]}") # sanity check --check that number of duplicate rows is false (ie, wrt duplicate listing ids)
    clist_duplicate_ids_check = []  # free memory

    ## Remove a few columns that are irrelevant to rental price and in which we do not want to store in the SQL table:
    #  remove 'Unnamed' columns, which might be imported errouneously via pd.read_csv()
    clist_rental = remove_col_with_given_starting_name(clist_rental, 'Unnamed')
    # remove listing_urls column since we do not want to store these data into the SQL Server table-- why?: a.) because listing urls are not relevent to rental prices and b.) the listing urls quickly become invalid or dead links, so we have no need to refer back to them at this stage in the webscraping project.
    clist_rental = remove_col_with_given_starting_name(clist_rental, 'listing_urls')
    # remove listing_descrip column
    clist_rental = remove_col_with_given_starting_name(clist_rental, 'listing_descrip')

    # sanity check
    print(f"Sanity check--The remaining columns in the dataset are:\n {clist_rental.columns}")


    ## 5.) Pandas df to SQL data pipeline--ie, INSERT the filtered data (*ie, unique data that has not been inserted yet)   

    # specify path to json file containing SQL configuration/username data
    sql_config_path = "D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\SQL_config\\config.json" 

    SQL_db = SQL_Database(sql_config_path)  # NB: be sure to pass in path to the json SQL configuration file so we can load in the needed username, password, and configuration data to be able to access the SQL database
    # Ingest data from date-filtered pandas' dataframe to SQL server--data pipeline: 
    SQL_db.insert_df_to_SQL_ETL(clist_rental)

    ## 5.) clean SQL sqft records by doing UPDATEs on sqft WHERE record has 'nan', and transform to SQL-recognized NULL values
    SQL_db.transform_np_nans_to_SQL_nulls()


if __name__=="__main__":
    main()
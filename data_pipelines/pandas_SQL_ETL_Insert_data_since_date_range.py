# imports-- file processing
import os
import glob

# data analysis libraries & SQL libraries
import numpy as np
import pandas as pd
# SQL ODBC for API connection between Python & SQL Server
import pyodbc
import sqlalchemy as sa

""" This script will be a reusable Pandas to SQL ETL 
that can be used to add scraped data that has not
previously been ingested into the SQL table.

How do we ensure the data will be unique for the SQL table?-- 4 Steps:

1.) Import all scraped data as a single pandas' DataFrame
by recursively looking up all CSV files and importing using pd.read_csv() and glob's iglob() method.

2) Verify what dates of data have been stored in the SQL table --(NB: this will involve a few sub-steps to parse the results to be usable as a Pandas' dataframe filter)

2a.) Determine last date of data stored in table: perform SQL query for the last available day (ie, MAX) of data as shown by date_posted:

2b.) Transform the results of the 

3.) Finally, filter the DataFrame of scraped data to be only 
data after--ie, greater than--the last available date (based on date_posted) 
found from the SQL table via step 2).

After these 3 steps, ingest the unique data into the table:

4.) INSERT the new scraped data (ie, the filtered Pandas' df) INTO the SQL table."""

# 1.) import all scraped data by recursively looking up CSV files in parent direc
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
            config = json.load(fh)

        self.driver = config['driver']
        self.server = config['server']
        self.database = config['database']
        self.username = config['username']
        self.password = config['password']

    # 2 a) Perform SQL query on date_posted col to determine the most recent date of data stored in the table  
    def determine_latest_date(self, query):
        """Insert scraped Craigslist rental listings data (ie, the Pandas' dataframe)
        to SQL Server database 'rentals' table"""

        conn = pyodbc.connect(
        f'DRIVER={self.driver};'
        f'SERVER={self.server};'
        f'DATABASE={self.database};'
        f'UID={self.username};'
        f'PWD={self.password};'
        'Trusted_Connection=yes;'
        )

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

    # 4) insert filtered df into SQL table
    def insert_df_to_SQL_ETL(self, df):
        """Insert scraped Craigslist rental listings data (ie, the Pandas' dataframe)
        to SQL Server database 'rentals' table"""

        conn = pyodbc.connect(
        f'DRIVER={self.driver};'
        f'SERVER={self.server};'
        f'DATABASE={self.database};'
        f'UID={self.username};'
        f'PWD={self.password};'
        'Trusted_Connection=yes;'
        )
        # # specify string specifying all of the details for establishing conneciton b/w Python & SQL
        # conn_str = 'DRIVER='+driver+';SERVER='+server_name+';DATABASE='+db_name+';UID='+username+';PWD='+ password +';Trusted_Connection=yes;' 

        # establish connection to SQL Server database, by passing in the database name, etc., using a with statement so it will automatically close the connection & cursor once the with statement has completed execution:
        # with pyodbc.connect(conn_str) as conn: #establish connection to SQL server database via pyodbc connector

        # initialize cursor so we can execute SQL code
        cursor = conn.cursor() 

        cursor.fast_executemany = True  # speed up data ingesting by reducing the numbers of calls to server for inserts

        # convert all variables from dataframe to str to avoid following SQL Server pyodbc error: 'ProgrammingError: ('Invalid parameter type.  param-index=2 param-type=function', 'HY105')'
        df = df.astype(str) # convert all df variables to str for ease of loading data into SQl Server table
        
        # insert scraped data from df to SQL table-- iterate over each row of each df col via .itertuples() method

        # NB: since there are 47 cols, we will need 47 '?' char marks  
        q_mark_list = ['?']*47
        # unpack list as string, and join() commas to each '?' char
        q_mark_str = ','.join(q_mark_list)

        # specify INSERT INTO SQL statement
        # iterate over each row in df, and insert into SQL database

        for row in df.itertuples():  # iterate over each row from df
            cursor.execute(f"""INSERT INTO rental (listing_id, sqft, city, price, bedrooms, bathrooms, attr_vars,
            date_of_webcrawler, kitchen, date_posted, region, sub_region, cats_OK, dogs_OK, wheelchair_accessible,laundry_in_bldg, no_laundry, 
            washer_and_dryer, washer_and_dryer_hookup, laundry_on_site, full_kitchen, dishwasher, refrigerator,
            oven,flooring_carpet, flooring_wood, flooring_tile, flooring_hardwood, flooring_other,apt, in_law_apt, condo, townhouse, cottage_or_cabin, single_fam, duplex, flat, land, is_furnished, attached_garage,
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

        # # sanity check-- ensure *new* data has been inserted into new SQL table by examining the 5 rows with the most recent date_posted
        sql_most_recent_listings = conn.execute("""SELECT date_posted FROM rentals ORDER BY date_posted DESC LIMIT 5;""").fetchall() # query for the 5 most recently-posted listings by ordering the data by date_posted in descending order

        print(f"The listings records with the most recent date_posted dates stored in the SQL table are as follows:\n{sql_most_recent_listings}")
        
        cursor.close()
        conn.close()


# 2) b.) Transform query results to string
def datetime_col_to_str_of_datetime(df, datetime_col):
    """Given datetime col from pandas' DataFrame,
    transform to a string of the datetime value."""
    return df[datetime_col].head(1).astype(str).reset_index().loc[0, datetime_col] 

# 3.) filter Pandas' dataframe by latest date of date_posted in SQL table
def filter_df_since_specified_date(df, target_date):
    """Filter the imported scraped dataset to all data newer than the specified date (as determined via the MAX(posted_date) query)."""
    df = df.loc[df.date_posted > target_date]  # filter to data greater than specified date
    return df


def main():
    # 1) import all scraped rental listings data -- NB: in our case, we have various SF Bay Area listings data
    clist_rental = recursively_import_all_CSV_and_concat_to_single_df(r"D:\\Coding and Code projects\\Python\\craigslist_data_proj\\craigslist_webscraper\\scraped_data\\sfbay")
    clist_rental.info()

    # 2) determine the last date of listings data stored in SQL table:
    SQL_db = SQL_Database()

    # 2a.) specify query to select the latest date based on date_posted:
    sql_query = "SELECT MAX(date_posted) AS latest_date FROM rentals;"
    # determine last date of listings records stored in SQL table
    latest_date = SQL_db.determine_latest_date(sql_query)


    # 2) b.) Transform query results to string:
    # specify name of df and datetime col to transform
    df, dt_col = latest_date, 'latest_date' 
    #apply function using the 2 arguments shown above
    latest_date_str = datetime_col_to_str_of_datetime(df, dt_col)
    # sanity check
    print(f"The latest date among the scraped data stored in the SQL table is:\n{latest_date_str}")

    # 3.) filter to data after last data inserted into SQL table--ie, the latest_date_str whose value we initially obtained from the MAX(date_posted) query
    clist_rental = filter_df_since_specified_date(clist_rental, latest_date_str)

    # 4.) INSERT the filtered data (*ie, unique data that has not been inserted yet)   
    SQL_db.insert_df_to_SQL_ETL(clist_rental)


if __name__=='__main__':
    main()
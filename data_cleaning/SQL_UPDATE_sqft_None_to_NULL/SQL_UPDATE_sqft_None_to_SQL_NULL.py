""" NB: This script will perform a data wrangling procedure to ensure
we can easily query for rental listings records that do not have square feet data.

Namely, we will perform an UPDATE statement that 
will transform all 'None' values to explicit SQL NULL values.

Therefore, we can then use IS NULL to identify records that are missing valid square feet data."""

# imports-- file processing
import os
import glob

# data analysis libraries & SQL libraries
import numpy as np
import pandas as pd
# SQL ODBC for API connection between Python & SQL Server
import pyodbc
import sqlalchemy as sa

# For the sqft col in SQL Server craiglist table: 
# convert all rows with value of 'nan' to blank records so that SQL server will recognize these as NULL values
class SQL_Database:
    def __init__(self):

        with open("D:\\Coding and Code projects\\Python\\craigslist_data_proj\\craigslist_webscraper\\SQL_config\\config.json",'r') as fh:
            config = json.load(fh)

        self.driver = config['driver']
        self.server = config['server']
        self.database = config['database']
        self.username = config['username']
        self.password = config['password']

        print(self.database)

    def transform_np_nans_to_SQL_nulls(self):
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
        # # establish connection to SQL Server database, by passing in the database name, etc., using a with statement so it will automatically close the connection & cursor once the with statement has completed execution:
        # with pyodbc.connect(conn_str) as conn: #establish connection to SQL server database via pyodbc connector

        # specify SQL statement
        sql = """UPDATE rentals 
        SET sqft = NULL
        WHERE sqft = 'nan';"""

        # iterate over each row in df, and insert into SQL database
        cursor.execute(sql)
        
        # # sanity check-- ensure some values of sqft are now recognized as being NULL by checking for values that are *not* NULL:
        sql_table_sqft_not_null = conn.execute("""SELECT * FROM RENTALS WHERE sqft IS NOT NULL;""").fetchall() # select all records where sqft is NULL
        print(f"Records that have non-NULL sqft data are as follows: {sql_table_sqft_not_null}")
        
        
        # save and commit changes to database
        conn.commit()

        cursor.close()
        conn.close()

if __name__=='main':
    SQL_db = SQL_Database()

    SQL_db.transform_np_nans_to_SQL_nulls()
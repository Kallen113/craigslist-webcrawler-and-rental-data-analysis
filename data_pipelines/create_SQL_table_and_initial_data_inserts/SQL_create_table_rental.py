# SQL ODBC for API connection between Python & SQL Server
import pyodbc
# json library to open a json file that contains our SQL credentials (ie, username, password, etc.) and database name 
import json  

"""
NB: This is intended to be a one-off script. 
It will create a table called rentals,
which will store all of the rental listings data we have 
obtained and parsed via the Python selenium webcrawler. 
"""

class SQL_Database():
    def __init__(self):
        # open config.json to access and configure credentials to establish connection between Python and SQL database 
        with open("D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\Rentals\\SQL_config\\config.json",'r') as fh:
            config = json.load(fh) # open config.json file, which contains all SQL database credentials--ie, username, password, database name, etc. 
        # specify SQL database credentials (again, we have obtained this from the config.json)
        self.driver = config['driver']
        self.server = config['server']
        self.database = config['database']
        self.username = config['username']
        self.password = config['password']

        print(f"Sanity check--name of SQL database is: {self.database}") # sanity check--ensure name of SQL database is present and accounted for, based on config.json 
        
        conn = pyodbc.connect(
        f'DRIVER={self.driver};'
        f'SERVER={self.server};'
        f'DATABASE={self.database};'
        f'UID={self.username};'
        f'PWD={self.password};'
        'Trusted_Connection=yes;'
        ) # establish pyodbc connection to SQL database by passing in our credentials, the database name, etc.

        # initialize cursor so we can execute SQL code:
        cursor = conn.cursor() 

        cursor.execute("""CREATE TABLE rental (
            listing_id bigint PRIMARY KEY,
            sqft int,  
            city varchar(40) NOT NULL,
            price int NOT NULL,
            bedrooms int,
            bathrooms decimal(6,1),
            attr_vars varchar(2000),
            date_of_webcrawler datetime,
            kitchen tinyint,
            date_posted datetime,
            region varchar(13),
            sub_region varchar(8),
            cats_OK tinyint,
            dogs_OK tinyint,
            wheelchair_accessible tinyint,
            laundry_in_bldg tinyint,
            no_laundry tinyint, 
            washer_and_dryer tinyint,
            washer_and_dryer_hookup tinyint,
            laundry_on_site tinyint,
            full_kitchen tinyint,
            dishwasher tinyint,
            refrigerator tinyint,
            oven tinyint,
            flooring_carpet tinyint,
            flooring_wood tinyint,
            flooring_tile tinyint,
            flooring_hardwood tinyint,
            flooring_other tinyint,
            apt tinyint,
            in_law_apt tinyint,
            condo tinyint,
            townhouse tinyint,
            cottage_or_cabin tinyint,
            single_fam tinyint,
            duplex tinyint,
            flat tinyint,
            land tinyint,
            is_furnished tinyint,
            attached_garage tinyint,
            detached_garage tinyint,
            carport tinyint,
            off_street_parking tinyint,
            no_parking tinyint,
            EV_charging tinyint,
            air_condition tinyint,
            no_smoking tinyint
            );"""
            )  # create table with the many numerous indicator variables stored as tinyint data type

        # save and commit changes to database
        conn.commit()

        cursor.close()
        conn.close()


def main():
    # specify path to json file containing SQL configuration/username data
    sql_config_path = "D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\SQL_config\\config.json" 

    # implement function to import SQL credentials via config.json file, and then create SQL table, which we will use to store all scraped craigslist rental listings data!
    SQL_Database(sql_config_path)  # create SQL table 'rentals'. NB: be sure to pass in path to the json SQL configuration file so we can load in the needed username, password, and configuration data to be able to access the SQL database  


if __name__=='__main__':
    main()

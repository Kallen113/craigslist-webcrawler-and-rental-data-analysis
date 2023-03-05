# SQL ODBC for API connection between Python & SQL Server
import pyodbc
# json library to open a json file that contains our SQL credentials (ie, username, password, etc.) and database name 
import json  
# os library to deal with directories
import os

class SQL_Database():
    def __init__(self, path_for_SQL_config, db_name_arg: str):
        with open(path_for_SQL_config, 'r') as fh:
            config = json.load(fh)

        self.driver = config['driver']
        self.server = config['server']
        # if we are running this script (one-off), then we have not yet created a database specific to this project: so just use auto-created database such as master instead of retrieving the database name from the config file
        self.database = 'master' 
        self.username = config['username']
        self.password = config['password']

        print(f"Sanity check on SQL config file--name of SQL server is: {self.server}") # sanity check--ensure name of SQL server is present and accounted for, based on config.json 

        conn = pyodbc.connect(
        f'DRIVER={self.driver};'
        f'SERVER={self.server};'
        f'DATABASE={self.database};'
        f'UID={self.username};'
        f'PWD={self.password};'
        'Trusted_Connection=yes;',
        autocommit= True
        ) # establish pyodbc connection to SQL database by passing in our credentials, the database name, etc.


        # specify what we want to name the new database 
        db_name = db_name_arg

        # cnxn = pyodbc.connect(connStr,autocommit = True)

        # cursor = conn.cursor(autocommit = True)
        cursor = conn.cursor()

        # create database if it does not already exist
        cursor.execute("""
        IF NOT EXISTS(SELECT * FROM sys.databases WHERE name =N'{}')
        BEGIN
            CREATE DATABASE {};
        END;""".format(db_name, db_name)
                )
        
        conn.commit()
        cursor.close()

        conn.close()


def main():
    # get root directory of project by moving up one step up in the file tree (ie, since we are one subdirectory below the root directory)

    os.path.join(os.path.dirname( __file__), os.path.pardir) # os.path.pardir provides the parent directory


    # get root directory of project by moving up one step up in the file tree (ie, since we are one subdirectory below the root directory)
    root_path = os.path.join(os.path.dirname( __file__), os.path.pardir) # os.path.pardir provides the parent directory (ie, one step up in file tree)

    print(root_path)

    # specify path to SQL configuration JSON file
    sql_config_path = os.path.join(root_path,'SQL_config\config.json')

    # sanity check to verify that the path to the json file is indeed a file and not merely a folder
    assert os.path.isfile(sql_config_path)

    # specify the database name we will use to store all of this project's data:
    db_name_arg = 'clist'


    # Create clist SQL database if not already exists
    SQL_Database(sql_config_path, db_name_arg)


if __name__== '__main__':
    main()

# SQL ODBC for API connection between Python & SQL Server
import pyodbc
import sqlalchemy as sa

# loop through all ODBC drivers we have access to in Python
for odb_driver in pyodbc.drivers():
    print(f"Each SQL ODBC driver we currently have on our local Python: {odb_driver}")
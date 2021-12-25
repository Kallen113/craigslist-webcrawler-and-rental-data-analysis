# craigslist-webcrawler
## Python selenium webcrawler of craigslist: 

This repo comprises a Python web crawler of craigslist rental listings data using primarily the selenium library to scrape criagslist rental listings data. There are essentially 3 phases to this project, although the first 2 phases are the primary focus: 1) A webcrawler & webscraper of rental listings data; 2.) Data cleaning and a data pipeline using Pandas and pyodbc to insert data from a Pandas' DataFrame to a SQL Server table; and 3.) A data analysis and visualizations of some of the data scraped via the webcrawler program. 

For the data cleaning, data pipeline, and data analysis aspects of this project, I wiill include both the main Python scripts as well as some Jupyter notebooks to demonstrate some of the data cleaning functions, data pipeline, and analysis in action.  

For the data cleaning and pipeline, the scripts create a Pandas' DataFrame to SQL Server pipeline. For data cleaning, I rely primarily on the Pandas and numpy libraries, exploiting vectorized methods where possible, to clean the data. After performing several data cleaning functions, such as deduplicating listings data and transforming specific columns to specific data types, the program then implements the data pipeline. Namely, I employ the pyodbc library to enable Python to interact with a MS SQL Server database. After creating a SQL table and cleaning the rental listings data, the scripts will insert the data from a Pandas' DataFrame into the SQL Server table. ETL of scraped data. 

The focus of this project is on San Francisco Bay Area rental listings (ie, for the sfbay site) data, but the webcrawler and webscraping functions and scripts can be fairly easily adapted to crawl over data from other regions and metropolitan areas, such as NYC, Seattle, etc. 

## Possible Use Cases:

One way to use this webcrawler and data cleaning program is for individuals who are looking for a new place to rent within a given region. For example, after running the webcrawler and data cleaning/pipeline portions of the project, you can then check for the least expensive rental prices within a given city or region, or to look for rental listings that match a specific set of characteristics or amenities that you desire.

### Caveats and Bugs:

While the data that the selenium webcrawler is scraping are accurate and complete for almost every variable, some of the records do not line up with 2 columns: namely, the 1) listing_urls & 2) the listing ids. I could not pinpoint any specific cause of this sort of "bug" in the webcrawler script. However, this is not an especially prompinent shortcoming or flaw. Ultimately, the listing URLs are only useful for enabling the webcrawler script to reference the listings and scrape the data. As for the listing_id, the only important aspect to this column for a webscraping and especially data analysis project is that the listing ids are each unique. NB: in short, given that the rest of the data lines up properly for each record nad have been scraped, it does not really matter once the webcrawler has been implemented. In addition, all of the other 44 of the 46 columns are accurate and line up properly to each record. Nevertheless, this is a bit of a caveat and bug with which to take note.  

### Legal Info & Disclaimer:
The use of this webcrawler is intended to be for personal & educational purposes only. Any commercial uses or purposes associated with the use of this repo's scripts and program are prohibited. No personal data or GIS locations of the rental listings are collected via this webcrawler program, and I do not claim any copyright ownership over any of the data from craigslist or its subsidiaries.  

# craigslist-webcrawler
## Python-- Project Overview, and using selenium for a webcrawler and webscraper of craigslist rental listings data: 

This repo comprises a Python web crawler of craigslist rental listings data using primarily the selenium library to crawl ovewr craigslist rental listings pages and scrape these rental listings data. 

There are essentially 3 phases to this project, although the first 2 phases are the primary focus: 1) A webcrawler & webscraper of rental listings data; 2.) Data cleaning and a data pipeline using Pandas and pyodbc to insert data from a Pandas' DataFrame to a SQL Server table; and 3.) Using the data scraped via the webcrawler program, I will implement a data analysis project and visualizations, with a focus on examining rental prices at the city level. In other words, I will attempt to answer the followiong question: For rental listings in the San Francisco Bay Area (SF Bay Area) cities, what are the major determinants of rental prices, and how well can we predict rental prices using the scraped data? 

## Describing the components of the project in more detail:

1) For the first phase, I will use the selenium (primarily) and beautifulsoup libraries to iterate over various rental listings within each of the SF Bay Area's subregions, such as the Peninsula, South Bay, and East Bay. This program iterates over each rental listing within a given subregion, and then scrapes data on various attributes such as the number of bedrooms, number of bathrooms, squarefeet (ie, the size of the rental home or apartment, etc.), garage or parking options, etc. After some additional parsing using the Pandas library, the scraped data are exported to a CSV file, which is organized into directories that are ordered by subregion.  
2) For the 2nd phase, I will create an ETL data pipeline. The ETL will import one or more of the CSV files--ie, the files outputted by the selenium webcrawler program--as a concatenated Pandas' DataFrame. Then, using Pandas and numpy, the ETL script will clean and transform the dataframe. Finally, after deduplicating, cleaning, and wrangling the dataset, the script will insert the rental listings data into a SQL Server table.
3) For the 3rd phase, we can readily import various rental listings data from the SQL Server table, given we have already run the Python selenium webcrawler program and ETL scripts at least once, respectively. After importing the data, we can then implement various data visualizations and analysis. However, take in mind that this phase of the project is more of a demonstrative purpose of use case for the data and project. In other words, the data analysis portion of this project is mainly to demonstrate what we can do with the data we have scraped using the webcrawler program. 

## Additional Notes on Data Cleaning and the CSV to Pandas to SQL Server ETL Data Pipeline:
For the data cleaning, ETL data pipeline, and data analysis aspects of this project, I wiill include both the main Python scripts as well as some Jupyter notebooks to demonstrate some of the data cleaning functions, data pipeline, and analysis in action.  

For the data cleaning and ETL data pipeline, the script first imports one or more of the CSV files--which contain the scraped rental listings data-- into a Pandas' DataFrame. After cleaning and wrangling the data, the data are then inserted into a SQL Server table. 

For data cleaning, I rely primarily on the Pandas and numpy libraries, exploiting vectorized methods where possible, to clean the data. After performing several data cleaning procedures and functions, such as deduplicating listings data and transforming specific columns to specific data types, the program then implements the data pipeline. Namely, we start with the CSV files  I employ the pyodbc library to enable Python to interact with a MS SQL Server database. After creating a SQL table and cleaning the rental listings data, the scripts will insert the data from a Pandas' DataFrame into the SQL Server table. ETL of scraped data. 

## A Brief Note About the Regions and subregions that this Webcrawler Project Focuses on: 

The focus of this project is on SF Bay Area rental listings (ie, for the sfbay craigslist site) data, but the webcrawler and webscraping functions and scripts can be fairly easily adapted to crawl over data from other regions and metropolitan areas, such as NYC, Seattle, etc. 

## Possible Use Cases:

One way to use this webcrawler and data cleaning program is for individuals who are looking for a new place to rent within a given region. For example, after running the webcrawler and data cleaning/pipeline portions of the project, you can then check for the least expensive rental prices within a given city or region, or to look for rental listings that match a specific set of characteristics or amenities that you desire.

### Caveats and Bugs:

While the data that the selenium webcrawler is scraping are accurate and complete for almost every variable, some of the records do not line up with 2 columns: namely, the 1) listing_urls & 2) the listing ids. I could not pinpoint any specific cause of this sort of "bug" in the webcrawler script. However, this is not an especially prompinent shortcoming or flaw. Ultimately, the listing URLs are only useful for enabling the webcrawler script to reference the listings and scrape the data. As for the listing_id, the only important aspect to this column for a webscraping and especially data analysis project is that the listing ids are each unique. NB: in short, given that the rest of the data lines up properly for each record nad have been scraped, it does not really matter once the webcrawler has been implemented. In addition, all of the other 44 of the 46 columns are accurate and line up properly to each record. Nevertheless, this is a bit of a caveat and bug with which to take note.  

### Legal Info & Disclaimer:
The use of this webcrawler is intended to be for personal & educational purposes only. Any commercial uses or purposes associated with the use of this repo's scripts and program are prohibited. No personal data or GIS locations of the rental listings are collected via this webcrawler program, and I do not claim any copyright ownership over any of the data from craigslist or its subsidiaries.  

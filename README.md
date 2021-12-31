# craigslist-webcrawler
## Python-- Project Overview, and using selenium for a webcrawler and webscraper of craigslist rental listings data: 

This repo comprises a Python web crawler of craigslist rental listings data using primarily the selenium library to crawl ovewr craigslist rental listings pages and scrape these rental listings data. 

There are essentially 3 phases to this project, although the first 2 phases are the primary focus: 1) A webcrawler & webscraper of rental listings data; 2.) Data cleaning and a data pipeline using Pandas and pyodbc to insert data from a Pandas' DataFrame to a SQL Server table; and 3.) Using the data scraped via the webcrawler program, I will implement a data analysis project and visualizations, with a focus on examining rental prices at the city level. In other words, I will attempt to answer the followiong question: For rental listings in the San Francisco Bay Area (SF Bay Area) cities, what are the major determinants of rental prices, and how well can we predict rental prices using the scraped data? 

## Describing the components of the project in more detail:

1) For the first phase, I will use the selenium (primarily) and beautifulsoup libraries to iterate over various rental listings within each of the SF Bay Area's subregions, such as the Peninsula, South Bay, and East Bay. This program iterates over each rental listing within a given subregion, and then scrapes data on various attributes such as the number of bedrooms, number of bathrooms, squarefeet (ie, the size of the rental home or apartment, etc.), garage or parking options, etc. After some additional parsing using the Pandas library, the scraped data are exported to a CSV file, which is organized into directories that are ordered by subregion.  
2) For the 2nd phase, I will create an ETL data pipeline. The ETL will import one or more of the CSV files--ie, the files outputted by the selenium webcrawler program--as a concatenated Pandas' DataFrame. Then, using Pandas and numpy, the ETL script will clean and transform the dataframe. Finally, after deduplicating, cleaning, and wrangling the dataset, the script will insert the rental listings data into a SQL Server table.
3) For the 3rd phase, we can readily import various rental listings data from the SQL Server table, given we have already run the Python selenium webcrawler program and ETL scripts at least once, respectively. After importing the data, we can then implement various data visualizations and analysis. However, take in mind that this phase of the project is more of a demonstrative purpose of use case for the data and project. In other words, the data analysis portion of this project is mainly to demonstrate what we can do with the data we have scraped using the webcrawler program. 

## Software Requirements and Packages Used for this Program:

To implement the Python selenium webcrawler program, we need to have the following software: Python 3 (at least version >= 3.7), Anaconda (if you wish to use Jupyter notebooks, especially for the 3rd phase/data analysis), various packages for Python 3 (as detailed in the sections below), and a command-line interface such as bash or Windows Powershell. While optional, I would also recommend using a code editor such as VS Code.

When actually running any portion or phase of this project's scripts, I would highly recommend using a Python virtual environment. A virtual environment allows us to have an isolated environment that contains all of the packages that are specific to this project. This way, we can more easily deal with a specific set of package dependencies than if we were (more clumsily) installing the packages at the global level.  

### How do we install Python packages?

We do *not* need to manually install Python packages. Instead, we can programmatically install Python packages. To do this--assuming we are using a Python virtual environment for the project--we need to install the packages via a command-line terminal by referencing the requirements.txt file that has been added to the parent CraigslistWebScraper directory.

Namely, we need to take the following 3 steps:

1.) Change to the parent CraigslistWebScraper directory (if needed).
2.) Activate the Python virtual environment.
-- For example, in Windows Powershell say the Python virtual environment is called 'venv':
<<<
venv\Scripts\activate.ps1

3.) Finally, install all of the needed packages by using the pip install command, and referencing the requirements.txt file as the argument: 
<<<
pip install -r requirements.txt

See below for a list of the main Python packages that we will need, although take note that the data analysis portion of the program--ie, the Phase 3--may vary depending on specific user demands and needs. For example, some individuals may not want to use ML models, in which case the sklearn library will clearly be unncessary. 

### Main Python packages for the webcrawler & scraper:

Webcrawler, web scraping, and web access libraries & modules: 
selenium, beautifulsoup, urllib.request, 

Data cleaning & analysis libraries: 
Pandas, DataFrame module from pandas.core.frame  

File processing, time, and datetime: 
os, time, random, datetime


## How do We Actually Implement the Webcrawler?

To implement the Python selenium webcrawler--ie, just the 1st phase of the project itself--we need to execute the main.py script as a module in a command-line terminal such as using bash, Powershell, etc. 

To be clear, this main.py script is found within the CraigslistWebScraper directory, which is this project's main parent directory. 

How do we use a terminal to implement a Python module instead of (say) running a regular Python script?

Within a command-line terminal, we need to use: python -m script_name_without_py_extension.

Ie, for our specific program, we need to do the following:
<<<
python -m main

Why use a Python module? The reason we are using main.py as a module is that we are importing several scripts, including a Python class, to be used for the webcrawler program. If we merely ran main.py as a script, the program would not work since we would not be able to import and use a Python class and all needed functions imported from other scripts.   


## Project File Structure:

What exactly is the file structure used for this project?

We have a parent directory called the CraigslistWebScraper directory, which contains the main.py script that implements the webcrawler. Within this parent directory, we have several sub-directories:

a.) Rentals: this contains most of the selenium webcrawler script, including the Craigslist_Rentals object, which specifies a customized URL for searching user-specified regions, subregions, minimum rental price, and maximum rental price filters for the rental listing webcrawler. 

b.) scraped_data: this contains 1 or more folders that will contain all of the data the Python selenium webcrawler and scraper will scrape and parse from the rental listings data. 

c.) data_pipelines: This contains several scripts associated with the Phase 2 of this project. For example, the SQL_create_table_rental.py script is a one-off script that creates a SQL Server table that can be used to store all of the scraped data. The Pandas_and_SQL_ETL_and_data_cleaning.py script, however, is a multi-use script that implements the CSV to Pandas to SQL Server ETL data pipeline. 

d.) SQL_config: This folder contains config.json, which specifies the SQL Server username and other configuration credentials that we need to refer to in order to connect Python to a SQL Server database using the pyodbc library. The reason for using a json file to store all of the SQL Server configuration details is so we do not need to manually enter the SQL Server credentials each time we need to access the SQL Server table. 

e.) data_analysis: This comprises the Phase 3 scripts. Namely, this subdirectory contains the data analysis and visualization scripts and Jupyter notebooks. 


## Additional Notes on Data Cleaning and the CSV to Pandas to SQL Server ETL Data Pipeline:
For the data cleaning, ETL data pipeline, and data analysis aspects of this project, I wiill include both the main Python scripts as well as some Jupyter notebooks to demonstrate some of the data cleaning functions, data pipeline, and analysis in action.  

For the data cleaning and ETL data pipeline, the script first imports one or more of the CSV files--which contain the scraped rental listings data-- into a Pandas' DataFrame. After cleaning and wrangling the data, the data are then inserted into a SQL Server table. 

For data cleaning, I rely primarily on the Pandas and numpy libraries, exploiting vectorized methods where possible, to clean the data. After performing several data cleaning procedures and functions, such as deduplicating listings data and transforming specific columns to specific data types, the program then implements the data pipeline. Namely, we start with the CSV files  I employ the pyodbc library to enable Python to interact with a MS SQL Server database. After creating a SQL table and cleaning the rental listings data, the scripts will insert the data from a Pandas' DataFrame into the SQL Server table. ETL of scraped data. 

## A Brief Note About the Regions and subregions that this Webcrawler Project Focuses on: 

The focus of this project is on SF Bay Area rental listings (ie, for the sfbay craigslist site) data, but the webcrawler and webscraping functions and scripts can be fairly easily adapted to crawl over data from other regions and metropolitan areas, such as NYC, Seattle, etc. 

## Possible Use Cases:

One way to use this webcrawler and data cleaning program is for individuals who are looking for a new place to rent within a given region. For example, after running the webcrawler and data cleaning/pipeline portions of the project, you can then check for the least expensive rental prices within a given city or region, or to look for rental listings that match a specific set of characteristics or amenities that you desire.

## Current Shortcomings and Bugs:

A bug and shortcoming associated with this webcrawler program is that the data being scraped are sometimes misaligned. Namely: whenever the webcrawler accesses a rental listing that has been removed by the poster or the server, the webcrawler program will incorrectly place the scraped data for the price and all other attributes and data associated with the incorrect URL. While somewhat rare, roughly 2-4% or more of the rental listings appear to be removed while the webcrawler is being run, as a rough estimate (admittedly, only based on a few sample points of webcrawler runs that I've tested thus far).

If only a single posting has been deleted, then the webcralwer program will merely misalign the various data with the incorrect URL by 1 cell for all subsequent listings stored within the outputted CSV file. In other words--after a deleted posting has been encountered--all subsequent rental listings' data will be aligned 1 cell below the actual URL, 
However, all of the rest of the data will be correctly aligned with itself, including the rental listing ids, price, sqft, etc. The deleted posts' data--ie, with missing data for essentially all of the main scraped attributes--will typically be placed at the very bottom cell(s) of the CSV file. 

A worse problem *might* occur when 2 or more postings have been deleted during a single use (session) of the webcrawler program. When 2 postings have been deleted within a given set of rental listings that the program is crawling and scraping over, then the program will misalign the data with the incorrect URL by 2 cells below. However, in some very rare cases, perhaps when there are many postings that have been deleted, then the program will incorrectly misalign the data not only with respect to the rental listing URLs, but also misalign the data with one or more of the other variables, including the listing ids.

As a result, on rare occasion this bug will cause the scraped data to be misaligned and the statistics being scraped will therefore be unreliable.

While a definite and reliable fix to this bug has not yet been ascertained, I likely need to revise the try...except...finally: pass block of code that is implemented within the selenium_webcrawler.py script, which includes most of the webcrawler and webcraper code and functions. This try...except...finally loop is a loop nested within a for loop, which iterates over each of the rental listing URLS found from iterating over each page of rental listings lying within a given subregion within the SF Bay Area. 

1 possible fix is to *revise* the *except* block to append 'nan' values to each list of scraped data, including for the listing ids. The except block already triggers for any TimeOutException errors, which can include deleted rental listing posts. This way, we should theoretically ensure that all of the scraped data is properly aligned, even when the webcrawler encounters rental listings that have been deleted (ie, a TimeOutException error) at the time we access the given listing URL to scrape the data.

NB: *Important* update on Dec 30th-31, 2021: 

Having revised the except block to append 'nan' values for any urls of listings that have been deleted, this try...except...finally block appears to be working correctly.

So instead, the problem might be after the for loop with the inner try...else...finally code blocks has finished executing. 

Namely, there appears to be 1 of 3 possibilities as to where the lists (and corresponding columns) of data are getting misaligned with each other:

1.) The try...except...finally block is causing the data to be misaligned. Why?--If this is the case, then this possibly might be due to the fact that the try block might run for some of the . If this is true, then I need to remove the scraping functions--ie, parse_html_via_xpath(), etc.--and only have it run in--say-- an else statement that will run after the except block has been executed--in other words, scrape the data only until *after* an exception has been checked for. 

As a result, the except block will trigger *before* any of the regular scraping takes place, thus theoretically ensuring that each list's data has been appended evenly and ego not misaligned!

Or, if the issue of misalignment is after the data have been scraped--ie, if the issue is following the execution of the for loop and try...else...finally code blocks.

For example, as 1 specific example of testing, scraping South Bay ('sby') data on December 30, 2021:

By the time I print out each list after doing the data cleaning of the lists right after the for loop and try...except...finally code blocks finish executing, we see discrepancies in the length of some of the lists:

Namely: The ids list of listing ids has the longest length at 741. The prices list of rental prices has the next longest length of 740. 

By contrast, the listing urls (ie, the urls associated with each rental listing), bedrooms and bathrooms lists each have a length of only 735: ie, 5 to 6 fewer elements compared with the ids & prices lists, respectively! 

The above example gives some support to the notion that the possibility #1 is correct: ie, I need to revise the try...except...finally block. 
 
 One specific implementation--ie, to potentially fix the misalignment issue--might be to have a simpler try block, which will merely access the given rental listing url--ie, the list_url iterable. Then, the except block will append 'nan' values for any listing in which we encounter a TimeoutException error. Next, we need to add an else statement below the except block. The else statement's code block will comprise the actual xpath and class name scraper functions. 


2.) The data cleaning of the lists that immediately follows the for loop with try...except...finally that iterates over each rental listing.



3.) The data are misaligned when the lists of data are transformed into a Pandas' DataFrame. Namely, we convert the lists to a dictionary of lists. We then take this dictionary of lists, and convert it to a Pandas' DataFrame.

--While this scenario seems fairly unlikely, it's possible the conversion to the Pandas' DataFrame is removing some of the null listing urls or otherwise causing misalignment. Still, possibilities #1 & 2 seem far more likely.  

## Additional features to add to the webcrawler:

To further mitigate bot detection, I might want add cursor movements and scroll-downs to help mimic human-like browser activity. I could add this to the finally code block--ie, within the try...except...else...finally nested within the listing url for loop. 

### Legal Info & Disclaimer:
The use of this webcrawler is intended to be for personal & educational purposes only. Any commercial uses or purposes associated with the use of this repo's scripts and program are prohibited. No personal data or GIS locations of the rental listings are collected via this webcrawler program, and I do not claim any copyright ownership over any of the data from craigslist or its subsidiaries.  

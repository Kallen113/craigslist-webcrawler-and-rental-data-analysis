# craigslist-webcrawler
## Python-- Project Overview, and using selenium for a webcrawler and webscraper of craigslist rental listings data: 

This repo comprises a Python web crawler of craigslist rental listings data using the selenium and requests library to scrape rental listings data. 

There are essentially 3 phases to this project, although the first 2 phases are the primary focus: 1) A webcrawler & webscraper of rental listings data; 2.) Data cleaning and a data pipeline using Pandas and pyodbc to insert data from a Pandas' DataFrame to a SQL Server table; and 3.) Using the data scraped via the webcrawler program, I will implement a data analysis project and visualizations, with a focus on examining rental prices at the city level. In other words, I will attempt to answer the followiong question: For rental listings in the San Francisco Bay Area (SF Bay Area) cities, what are the major determinants of rental prices, and how well can we predict rental prices using the scraped data? 

## Describing the components of the project in more detail:

1) For the first phase, I will use the selenium (primarily) and beautifulsoup libraries to iterate over various rental listings within each of the SF Bay Area's subregions, such as the Peninsula, South Bay, and East Bay. This program iterates over each rental listing within a given subregion, and then scrapes data on various attributes such as the number of bedrooms, number of bathrooms, squarefeet (ie, the size of the rental home or apartment, etc.), garage or parking options, etc. After some additional parsing using the Pandas library, the scraped data are exported to a CSV file, which is organized into directories that are ordered by subregion.  

2) For the 2nd phase, I will create an ETL data pipeline. The ETL will import one or more of the CSV files--ie, the files outputted by the selenium webcrawler program--as a concatenated Pandas' DataFrame. Then, using Pandas and numpy, the ETL script will clean and transform the dataframe. Finally, after deduplicating, cleaning, and wrangling the dataset, the script will insert the rental listings data into a SQL Server table.

3) For the 3rd phase, we can readily import various rental listings data from the SQL Server table, given we have already run the Python selenium webcrawler program and ETL scripts at least once, respectively. After importing the data, we can then implement various data visualizations and analysis. However, take in mind that this phase of the project is more of a demonstrative purpose of use case for the data and project. In other words, the data analysis portion of this project is mainly to demonstrate what we can do with the data we have scraped using the webcrawler program. 

## Software Requirements and Packages Used for this Program:

To implement the Python selenium webcrawler program, we need to have the following software: 

NB: Note that I'm using a Windows OS, so some of these software and CLIs may differ if you have a Mac or other non-Windows OS.

a) Python 3 (ideally, version >= 3.9); 

b) Anaconda: for 2 reasons: i) So we can use a conda virtual environment for Python, so that we can avoid having to install C++ dependencies manually (which would be required if using a regular Python virtual environment. ii) For the 3rd phase/data analysis phase, we will use Jupyter notebooks so wwe can save our data visualizations, charts, and regression results;

c) Various packages for Python 3 (as detailed in the sections below), which we can install directly from the requirements.txt once we have activated a conda (Python) environment;  


d) A command-line interface (CLI) such as Windows PowerShell. 

----di) Given that a conda virtual environment is recommended for this project, I would especially recommend using *Anaconda PowerShell Prompt* as your CLI. While a regular PowerShell prompt can be used, in order to use conda commands or virtual environments directly via a regular PowerShell CLI (ie, not an Anaconda PowerShell Prompt), you would need to place your installation of Anaconda into your local machine's System PATH.  

e) (Optional): While optional, I would also recommend using a code editor such as VS Code, since we can use Jupyter notebooks and see our visualizations and regression results directly within the code editor as opposed to only using a CLI (which does not allow for plots to be displayed unless we use outside tools or GUIs).

When actually running the webcrawler, I would highly recommend using a conda virtual environment for Python. A virtual environment allows us to have an isolated environment that contains all of the packages that are specific to this project. This way, we can more easily deal with a specific set of package dependencies than if we were (more clumsily) installing the packages at the global level.  

### How do we install Python packages?

We do *not* need to manually install Python packages. Instead, we can programmatically install Python packages using the files from this repo by running pip install from the requirements.txt, once we've activated a virtual environment.

While we can use a regular Python virtual environment for the project, I would *instead* recommend using a conda virtual environment for Python. If we used regular Python virtual environments instead, we would need to install C++ dependencies separately, but using a conda environment will satisfy those requirements. (The only trade-offs to using a aconda virtual environment are that a) we need to install Anaconda & b) it takes longer to initially create a conda vs a regular Python virtual environment). 

To install *all* required packages, we need to install the packages via a CLI by referencing the requirements.txt file that has been added to the parent CraigslistWebScraper directory of this repo.

Namely, we need to take the following 3 steps:

1.) Open a CLI: again, I'd recommend an Anaconda PowerShell Prompt.

2.) Change the directory to the parent CraigslistWebScraper directory.

3.) Create a conda virtual environment, and ensure the Python version if >= 3.7 (NB: you only need to do this step once)

(A regular Python virtual environment can be created instead, but again this is not recommended since you'd need to handle C++ dependencies separately)

Ex: Create a conda virtual env called "clistenv" with Python version 3.9:

<<<
#### conda create -n clistenv python=3.9 anaconda


And, type "y" when prompted to do so to finalize creation of the environment.

4.) Activate the conda virtual environment after it has been created:

Ex: in an Anaconda Powershell Prompt say the conda virtual environment is again called 'clistenv':

<<<
#### conda activate clistenv

5.) Finally, install *all* of the needed packages by using the pip install command, and referencing the requirements.txt file as the argument: 

<<<
#### pip install -r requirements.txt



6.) When you have finished using the webcrawler using a CLI such as PowerShell, use the deactivate command to turn off the virtual env:

<<<
#### deactivate

### Main Python packages for the webcrawler & scraper:

See below for a list of the most important Python packages that we will use for this webcrawler project:

Webcrawler, web scraping, and web access libraries & modules: 
selenium, beautifulsoup, & urllib.request 

Data cleaning & analysis libraries: 
Pandas, DataFrame module from pandas.core.frame, numpy  

File processing, time, and datetime: 
os, time, random, datetime


## How do We Actually Implement the Webcrawler?

To implement the Python selenium webcrawler, we need to execute the main.py script as a module in a command-line terminal such as using Powershell. 

To be clear, this main.py executable is found within the CraigslistWebScraper directory, which is this project's root directory. 

How do we use a terminal to implement a Python module instead of (say) running a regular Python script?

Within a command-line terminal, we need to use: python -m script_name_without_py_extension.

Ie, for our specific program, we need to do the following:

<<<
#### python -m main

Why use a Python module? The reason we are using main.py as a module is that we are importing several scripts, including a Python class, to be used for the webcrawler program. If we merely ran main.py as a script, the program would not work since we would not be able to import and use a Python class and all needed functions imported from other scripts.   


## A Brief Note About the Regions and subregions that this Webcrawler Project Focuses on: 

The focus of this project is on SF Bay Area rental listings (ie, for the sfbay craigslist site) data, but the webcrawler and webscraping functions and scripts can be fairly easily adapted to crawl over data from other regions and metropolitan areas, such as NYC, Seattle, etc. 

## What if I Want to Examine Rental Listings from Metropolitan Areas Outside of the SF Bay Area?

The main.py script--assuming we run the program as a Python module (as described above)--prompts the user via command-line to select one of 18 metropolitan regions (including the SF Bay Area). After selecting the metropolitan region, the user will then be prompted to select a subregion-- for example, district of columbia is a subregion within the Washington, DC (parent) region. 

Here's a partial list of (parent) metropolitan regions:

SF Bay Area, CA; San Diego, CA; Chicago, IL; Seattle, WA, Boston, MA, etc.

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


## Possible Use Cases:

One way to use this webcrawler and data cleaning program is for individuals who are looking for a new place to rent within a given region. For example, after running the webcrawler and data cleaning/pipeline portions of the project, you can then check for the least expensive rental prices within a given city or region, or to look for rental listings that match a specific set of characteristics or amenities that you desire.


## Additional features to add to the webcrawler:

To facilitate a webcrawler for non-SF Bay Area regions, I might add a new script to the project that would scrape data on the subregion names for a given region--e.g., subregions of Chicago or NY. 

To further mitigate bot detection, I might want add cursor movements and scroll-downs to help mimic human-like browser activity. I could add this to the finally code block--ie, within the try...except...else...finally nested within the listing url for loop. 



### Legal Info & Disclaimer:
The use of this webcrawler is intended to be for personal & educational purposes only. Any commercial uses or purposes associated with the use of this repo's scripts and program are prohibited. No personal data or GIS locations of the rental listings are collected via this webcrawler program, and I do not claim any copyright ownership over any of the data from craigslist or its subsidiaries.  

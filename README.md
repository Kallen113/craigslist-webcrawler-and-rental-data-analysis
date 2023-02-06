# craigslist-webcrawler
## Python-- Project Overview, and using selenium for a webcrawler and webscraper of craigslist rental listings data: 

This repo comprises a Python web crawler of craigslist rental listings data using the selenium and requests library to scrape rental listings data. 

There are essentially 3 phases to this project, although the first 2 phases are the primary focus: 1) Webcrawler: A webcrawler & webscraper of rental listings data; 2.) CSV to SQL Server data pipeline: Data cleaning and a data pipeline using Pandas and pyodbc to insert data from a Pandas' DataFrame to a SQL Server table; and 3.) Data Analysis, Visualizations, and Regression Analytsis: Using the data scraped via the webcrawler program, I implement data analysis, visualizations, and statistical analysis with a focus on examing rental prices at the city level. In other words, I will attempt to answer the following question: For rental listings in the San Francisco Bay Area (SF Bay Area) cities, what are the major determinants of rental prices, and how well can we predict rental prices using the scraped data? 

## Describing the components of the project in more detail:

1) Webcrawler & CSV data pipeline: For the first phase, I will use the selenium and requests libraries to iterate over various craigslist rental listings within each of the SF Bay Area's subregions, such as the Peninsula, South Bay, and East Bay. This program iterates over each rental listing within a given subregion, and then scrapes data on various attributes such as the number of bedrooms, number of bathrooms, squarefeet (ie, the size of the rental home or apartment, etc.), garage or parking options, etc. After some additional data cleaning and parsing using the Pandas library, the scraped data are exported to a CSV file, which will automatically be organized into subdirectories that are ordered by subregion.   

2) CSV to SQL data pipeline: For the 2nd phase, I have created an ETL data pipeline. The ETL will import one or more of the CSV files--ie, the files outputted by the selenium webcrawler program--as a concatenated Pandas' DataFrame. Then, using Pandas and numpy, the ETL script will clean and transform the dataframe. Finally, after deduplicating, cleaning, and wrangling the dataset, the script will insert the rental listings data into a SQL Server table.

3) For the 3rd phase, we can readily import various rental listings data from the SQL Server table, given we have already run the Python selenium webcrawler program and ETL scripts at least once, respectively. After importing the data, we can then implement various data visualizations and analysis. However, take in mind that this phase of the project is more of a demonstrative purpose of use case for the data and project. In other words, the data analysis portion of this project is mainly to demonstrate what we can do with the data we have scraped using the webcrawler program. 

## Software Requirements and Packages Used for this Program:

To implement the Python selenium webcrawler program and the CSV to SQL data pipeline, we need to have the following software: 

NB: Note that I'm using a Windows OS, so some of these software and CLIs may differ if you have a Mac or other non-Windows OS.

a) Python 3 (ideally, version >= 3.9); 

b) Anaconda *or* Miniconda (*NB: all scripting has been done using Anaconda, so I cannot 100% verify whether Miniconda would work): We are using this for 2 reasons: i) So we can use a conda virtual environment for Python, so that we can avoid having to install C++ dependencies manually (which would be required if using a regular Python virtual environment). ii) For the 3rd phase/data analysis phase, we will use Jupyter notebooks (which is pre-installed with Anaconda) so we can save our data visualizations, charts, and regression results;

c) Various packages for Python 3 (as detailed in the sections below), which we can install directly from the requirements.txt once we have activated a conda (Python) environment;  

d) A command-line interface (CLI) such as Windows PowerShell or Anaconda PowerShell Prompt. 

----di) Given that a conda virtual environment is recommended for this project, I would especially recommend using *Anaconda PowerShell Prompt* as your CLI. While a regular PowerShell prompt can be used, in order to use conda commands or virtual environments directly via a regular PowerShell CLI (ie, not an Anaconda PowerShell Prompt), you would need to place your installation of Anaconda into your local machine's System PATH.  

e) SQL Server & SSMS: You can download the latest version of SQL Server here: [SQL Server download](https://www.microsoft.com/en-us/sql-server/sql-server-downloads). Also, to download SSMS, go to: [SSMS download](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver16). For more details on installing and setting up SQL Server, see: [SQL Server installation & setup guide](https://www.sqlservertutorial.net/install-sql-server/).

SQL Server is required to implement the CSV (via Pandas) to SQL data pipeline (see Pandas_and_SQL_ETL_and_data_cleaning.py from the data_pipelines subfolder). SSMS is optional, but provides a GUI to more easily implement SQL Server queries, create tables, etc. A different SQL RDBMS--e.g., Oracle SQL--can be used instead of SQL Server, but the SQL RDBMS must be compatible with the pyodbc package's API. Otherwise, the Pandas_and_SQL_ETL_and_data_cleaning.py would need to be revised for your purposes. 

f) (Optional): While optional, I would also recommend using a code editor such as VS Code, since we can use Jupyter notebooks and see our visualizations and regression results directly within the code editor as opposed to only using a CLI (which does not allow for plots to be displayed unless we use outside tools or GUIs).

When actually running the webcrawler, I would highly recommend using a conda virtual environment for Python. This type of virtual environment can only be created if we have installed Anaconda or mini-conda. A virtual environment allows us to have an isolated environment that contains all of the packages that are specific to this project. This way, we can more easily deal with a specific set of package dependencies than if we were (more clumsily) installing the packages at the global level.  

### How do we install Python packages?

We do *not* need to manually install Python packages. Instead, we can programmatically install Python packages using the files from this repo by running pip install from the requirements.txt, once we've activated a virtual environment.

While we can use a regular Python virtual environment for the project, I would *instead* recommend using a conda virtual environment for Python. If we used regular Python virtual environments instead, we would need to install C++ dependencies separately, but using a conda environment will satisfy those requirements. (The only trade-offs to using a conda virtual environment are that a) we need to install Anaconda or Miniconda & b) it takes longer to initially create a conda vs a regular Python virtual environment since more packages are installed by default). 

To install *all* required packages, we need to install the packages via a CLI by referencing the requirements.txt file that has been added to the parent CraigslistWebScraper directory of this repo.

Namely, we need to take the following 3 steps:

1.) Open a CLI: again, I'd recommend using an Anaconda PowerShell Prompt.

2.) Change the directory to the root (parent) directory of the craigslist-webcrawler scripts (ie, where the main.py executable is).

3.) Create a conda virtual environment, and ensure the Python version is >= 3.7 (NB: you only need to do this step once)

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

The main.py script--assuming we run the program as a Python module (as described above)--prompts the user via command-line to select one of 18 metropolitan regions (including the SF Bay Area). After selecting the metropolitan region, the user will then be prompted to select a subregion--for example, "district of columbia" is a subregion within the Washington, DC (parent) region. 

Here's a partial list of (parent) metropolitan regions:

SF Bay Area, CA; San Diego, CA; Chicago, IL; Seattle, WA, Boston, MA, etc.

## Project File Structure:

What exactly is the file structure used for this project?

We have a parent directory called the CraigslistWebScraper directory, which contains the main.py executable that implements the webcrawler. Within this parent directory, we have several sub-directories:

a.) Rentals: this contains most of the selenium webcrawler script, including the Craigslist_Rentals object, which specifies a customized URL for searching user-specified regions, subregions, minimum rental price, and maximum rental price filters for the rental listing webcrawler. 

b.) scraped_data: this contains 1 or more folders that will contain all of the data the Python selenium webcrawler and scraper will scrape and parse from the rental listings data. 

c.) data_pipelines: This contains several scripts associated with the Phase 2 of this project. NB: *Before* you can start running the CSV to SQL Server data pipeline, we need to create a SQL database (see SQL Server installation guide above) within SSMS or SQL Server command-line. After a SQL database and administator user has been created on your local PC, you can start running the scripts in this subdirectory:

---c1) SQL_create_table_rental.py: This script is located within an additional subdirectory--ie, data_pipelines/create_SQL_table_and_initial_data_inserts/. SQL_create_table_rental.py script is a one-off script (ie, it's intended for a one-time use) that creates a SQL Server table that can be used to store all of the scraped data. This script must be run in order to enable the main CSV to SQL data pipeline script to function properly without requiring additional manual usage of SSMS or SQL Server. 

---c2) Pandas_and_SQL_ETL_and_data_cleaning.py: Once the one-off script has been executed, we can start running the Pandas_and_SQL_ETL_and_data_cleaning.py script *each time* we want to insert newly-scraped data into a SQL Server table. This is a multi-use script that implements the CSV to Pandas to SQL Server ETL data pipeline.

This data pipeline uses the pyodbc library's API to access SQL Server via Python. From the CLI, you can select the region & subregion whose scraped data you want to use to insert into the SQL Server table. To do so, the script reads in all available CSV files of scraped data for the given subregion. To ensure we *only* end up inserting new data, we run a simple SQL query to check for the data--for the given subregion--that has *already* been inserted into the SQL Server table by looking up the latest (ie, MAX() of the) date_posted records and use this value to filter the data we imported from our local PC's scraped data (ie, imported from the CSV files). 
After performing several data cleaning and wrangling functions, we insert the new scraped data into our SQL Server table. 

d.) SQL_config: This folder contains config.json, which specifies the SQL Server username and other configuration credentials that we need to refer to in order to connect Python to a SQL Server database using the pyodbc library. The reason for using a json file to store all of the SQL Server configuration details is so we do not need to manually enter the SQL Server credentials each time we need to access the SQL Server table. 

e.) data_analysis: This comprises the Phase 3 scripts. Namely, this subdirectory contains the data analysis and visualization scripts and Jupyter notebooks. 

## Additional Notes on Data Cleaning and the CSV to Pandas to SQL Server ETL Data Pipeline:
For the data cleaning, ETL data pipeline, and data analysis aspects of this project, I wiill include both the main Python scripts as well as some Jupyter notebooks to demonstrate some of the data cleaning functions, data pipeline, and analysis in action.  

For the data cleaning and ETL data pipeline--ie, the , the script first imports one or more of the CSV files--which contain the scraped rental listings data-- into a Pandas' DataFrame. After cleaning and wrangling the data, the data are then inserted into a SQL Server table. 

For data cleaning, I rely primarily on the Pandas and numpy libraries, exploiting vectorized methods where possible, to clean the data. After performing several data cleaning procedures and functions, such as deduplicating listings data and transforming specific columns to specific data types, the program then implements the data pipeline. Namely, we start with the CSV files  I employ the pyodbc library to enable Python to interact with a MS SQL Server database. After creating a SQL table and cleaning the rental listings data, the scripts will insert the data from a Pandas' DataFrame into the SQL Server table. ETL of scraped data. 

## FAQ: 

1) Why is it that when I run the webcrawler program--ie, via <<< python -m main--the program is not running properly on my local machine? For example, I get a ModuleNotFoundError such as: "No module named 'selenium'" or "No module named 'pandas', etc.?

I highly recommend that you use a conda virtual environment via an Anaconda PowerShell Prompt CLI, not a standard Python virtual environment or regular Windows PowerShell since you'd otherwise need to install C++ dependencies separately and manually.

However, if you are already using a conda virtual environment and are using an Anaconda PowerShell Prompt for your CLI, then double-check whether you have installed all required Python packages on the conda environment. As mentioned earlier, you do not have to manually install each Python package individually, but instead install from the requirements.txt file that is saved to the root directory of this project. As is standard practice, this .txt file contains a list of all required Python packages, including the versions of the packages I've used for this project. 

TLDR: To install all required Python packages to a conda virtual environment, do the following 3 steps:

a) Change the directory to the root directory of this webcrawler project:
<<< cd path_to_root_directory_of_webcrawler_propject

b) activate the conda virtual environment:

<<< conda activate clist_env

& 

c) Install the Python packages from the requirements.txt:

<<< pip install -r requirements.txt

After activating the conda virtual environment, you can check which Python packages have been installed to the environment. After activating your conda virtual environment, you can run the following command to list all Python packages that are currently installed on the conda environment:

<<< conda list

2) Where can I find the data that the webcrawler has outputted to CSV?

You can find these data within the scraped_data subdirectory. This folder will automatically be created after running the webcrawler program for the first time (ie, executing main.py via <<< python -m main at command line). This subdirectory will be located directly within the root directory. Any regions and then subregions will have their own additional subdirectories located within the scraped_data folder. 

3) How do I setup a SQL Server table for the CSV to SQL data pipeline?

As stated in earlier sections, you need to have SQL Server installed, and a SQL database server needs to be setup before running any of the data_pipelines scripts. See the link above on how to install SQL Server and do the initial server setup. 

Once a database server has been created and you have created a username and password for yourself, change the *config.json* from the SQL_config subdirectory to reflect your *own* username and password. This is because the Python scripts from the data_pipelines subdirectory reference the config.json via a pyodbc API connection. Via this pyodbc connection, Python can connect to the given SQL database and make changes and/or execute queries from a SQL table located within your local machine's database. To be clear, the config.json on this repo is shown for illustrative purposes only and does not reflect any real-life username or password.

The included scripts in the data_pipelines subdirectory can then be used first to a) create a new SQL database and b) create the SQL table that will store the scraped data from the webcrawler.

4) What if I'm using Mac and/or I want to use a different SQL RDBMS other than SQL Server for the ETL data pipelines?

You might want to use Oracle SQL. Oracle SQL is compatible with the pyodbc Python library that this project uses for the CSV to SQL data pipelines. Some of the scripts from the data_pipelines subdirectory might need to be modified, but most of the code should still run properly without any changes.

## Possible Use Cases:

One way to use this webcrawler and data cleaning program is for individuals who are looking for a new place to rent within a given region. For example, after running the webcrawler and data pipeline portions of the project, you can then check for the least expensive rental prices within a given city or region, or to look for rental listings that match a specific set of characteristics or amenities that you desire. With some basic knowledge of SQL, you can run queries that match the amenities you would want.

Quick SQL query examples: Show the rental prices & sqft for January 2023 rental listings from San Francisco that are 1-bedroom apartments with 1 full (not half) bathroom:

<<<
SELECT price
FROM rental
WHERE city = 'San Francisco'
AND bedrooms = 1 
AND bathrooms = 1
AND apt =1 
AND MONTH(date_posted) = 1
AND YEAR(date_posted) = 2023;

What are the 10 cheapest such apartments from SF for January 2023?:

<<<
WITH rank_rental_price_apt_sf AS (SELECT price, DENSE_RANK() OVER(PARTITION BY city ORDER BY price ASC) AS price_rank FROM rental WHERE apt=1 
AND city ='San Francisco' AND MONTH(date_posted) = 1 AND YEAR(date_posted)= 2023)

SELECT price
FROM rank_rental_price_apt_sf
--select only 10 cheapest rental listings

WHERE price_rank <= 10;


## Additional features to add to the webcrawler:

To further mitigate bot detection, I might want add cursor movements and scroll-downs to help mimic human-like browser activity. I could add this to the finally code block--ie, within the try...except...else...finally nested within the listing url for loop. 


### Legal Info & Disclaimer:
The use of this webcrawler is intended to be for personal & educational purposes only. Any commercial uses or purposes associated with the use of this repo's scripts and program are prohibited. No personal data or GIS locations of the rental listings are collected via this webcrawler program, and I do not claim any copyright ownership over any of the data from craigslist or its subsidiaries.  

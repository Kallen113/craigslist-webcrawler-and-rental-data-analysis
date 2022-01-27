# imports-- file processing
import os
import glob

# data analysis libraries
import numpy as np
import pandas as pd




def recursively_import_all_CSVs_and_import_diff_dfs_via_dict(direc, csv_pattern):
    """Search given directory, and look up all CSV files in it.
    Then, import each CSV file to different Pandas' dfs, contained within a dictionary of DataFrames."""
    # specify directory containing the scraped data
    path =  direc # specify parent path of directories containing the scraped rental listings CSV data -- NB: use raw text--as in r'path...', or can we use the double-back slashes to escape back-slashes??
    # initialize empty dictionary to contain each imported df:
    dict_of_dfs = {}
    # recursively search path for any CSV files:
    csv_files = glob.iglob(os.path.join(path, csv_pattern, recursive=True)) 
    # iterate over each CSV file found in path, and import each CSV as separate dataframes:
    for file in csv_files: 
        dict_of_dfs[file] = pd.read_csv(file)
    return dict_of_dfs

## Import Dataset
# import all scraped SF bay area rental listings data as separate dataframes:

# NB: let's start by importing South Bay data:

# specify parent directory containing all scraped rental listings data:
scraped_data_parent_path = r"D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\scraped_data\\sfbay\\sby"


# specify pattern to search for South Bay CSV files:

# NB: in our case, we want to look up files whose names start with 'craigslist_rental_sfbay_sby_', and then have a .csv extension (ie, via the *.csv wildcard to look up all corresponding CSV files in given path with a 'craigslist_' prefix for the file names)
csv_pattern_sby = 'craigslist_rental_sfbay_sby_*.csv'  # search for all South Bay CSV files


# import all South Bay data as dict of Dataframes:
dict_dfs_sby = recursively_import_all_CSVs_and_import_diff_dfs_via_dict(scraped_data_parent_path, csv_pattern_sby)

# sanity check
print(f"South Bay data--dictionary of dfs:\n{dict_dfs_sby}\n\n")


# Filter to just the Jan 1-20, 2022 data
def filter_df_to_specified_date_range(df, date_col, start_date, cutoff_date):
    """Filter the imported scraped dataset to specified date range. NB: cutoff_date refers to the day after the last date of data you want to retrieve."""
    df = df.loc[(df[date_col]> pd.Timestamp(start_date)) & (df[date_col] < pd.Timestamp(cutoff_date))]  # filter to date range
    return df

# specify date range values
# NB: We want to start with Jan 1st, 2022, and then end with Jan 20th
start_date = 2021, 1, 1  # start with Jan 1, 2022

cutoff_date = 2021, 1, 21  # end just before Jan 21, 2022

df = filter_df_to_specified_date_range(df, 'date_posted', start_date, cutoff_date)

# sanity check
df.sort_values(by =['date_posted'])
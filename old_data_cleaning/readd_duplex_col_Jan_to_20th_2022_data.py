# imports-- file processing
import os
import glob

# data analysis libraries
import numpy as np
import pandas as pd

# for datetime manipulation and filtering
import datetime
datetime.datetime.strptime

#### Readd duplex housing type col to Jan 1-20, 2022 scraped CSV files (NB: duplex col was inadevertently deleted from the 'scraper_and_data_cleaning_functions.py' script, but fixed as of 1/21/2022)

## Import Jan 1-20, 2022 data, but import and process for different subregions, for ease of exporting back to (ie, overwriting original) CSVs:


def import_csvs_from_path_as_separate_dfs(path):
    # change working direc to where CSVs are located
    os.chdir(path)

    # obtain a list of all CSV files stored in specified path
    csvs = [x for x in os.listdir('.') if x.endswith('.csv')]
    
    # obtain a list of all file names of the CSV files
    csv_file_names = [os.path.splitext(os.path.basename(x))[0] for x in csvs]
    
    # initialize empty dict to contain the soon-to-be DataFrames
    dict_of_dfs = {}
    # iterate over each element (ie, file name) in the CSV file names list, and import the CSVs as separate dfs while also appending the file names as keys to the dictionary of DataFrames: 
    for file in range(len(csv_file_names)):
        dict_of_dfs[csv_file_names[file]] = pd.read_csv(csvs[file])  # import CSV files as separate dfs and store as the values of the dictionary, and append the file names as the keys for the dict
    
    return dict_of_dfs


## Import Dataset
# import all scraped SF bay area rental listings data as separate dataframes:

# NB: let's start by importing South Bay data:

# 1st, specify path of South Bay data:
sby_data_path = "D:\Coding and Code projects\Python\craigslist_data_proj\CraigslistWebScraper\scraped_data\sfbay\\sby"


# then, import all sby CSV files as separate DataFrames contained within a dictionary of DataFrames
sby_dict = import_csvs_from_path_as_separate_dfs(sby_data_path)  # import sby data as a dict of dfs

# sanity check
print(f"South Bay data: {sby_dict}")



""" 
NB: 
Next, we need to repeat same process (ie, import each CSV as separate dfs stored in a dictionary) for each of the other subregions:
ie, North Bay ('nby'), Peninsula, etc.:
"""
# import North Bay data
# specify path 
nby_data_path = "D:\Coding and Code projects\Python\craigslist_data_proj\CraigslistWebScraper\scraped_data\sfbay\\nby"


# then, import all CSV files as separate DataFrames contained within a dictionary of DataFrames
nby_dict = import_csvs_from_path_as_separate_dfs(nby_data_path)  # import nby data as a dict of dfs



# import SF data
# specify path 
sfc_data_path = "D:\Coding and Code projects\Python\craigslist_data_proj\CraigslistWebScraper\scraped_data\sfbay\\sfc"


# then, import all CSV files as separate DataFrames contained within a dictionary of DataFrames
sfc_dict = import_csvs_from_path_as_separate_dfs(sfc_data_path)  # import nby data as a dict of dfs



# import Peninsula data
# specify path 
pen_data_path = "D:\Coding and Code projects\Python\craigslist_data_proj\CraigslistWebScraper\scraped_data\sfbay\\pen"


# then, import all CSV files as separate DataFrames contained within a dictionary of DataFrames
pen_dict = import_csvs_from_path_as_separate_dfs(pen_data_path)  # import nby data as a dict of dfs



# import East Bay data
# specify path 
eby_data_path = "D:\Coding and Code projects\Python\craigslist_data_proj\CraigslistWebScraper\scraped_data\sfbay\\eby"


# then, import all CSV files as separate DataFrames contained within a dictionary of DataFrames
eby_dict = import_csvs_from_path_as_separate_dfs(eby_data_path)  # import nby data as a dict of dfs



# import Santa Cruz data
# specify path 
scz_data_path = "D:\Coding and Code projects\Python\craigslist_data_proj\CraigslistWebScraper\scraped_data\sfbay\\scz"


# then, import all CSV files as separate DataFrames contained within a dictionary of DataFrames
scz_dict = import_csvs_from_path_as_separate_dfs(scz_data_path)  # import nby data as a dict of dfs


""" Next, we need to add duplex housting type col,
and ensure it's in the correct position:
--namely: 
In *between* the 'single_fam' & 'is_furnished' columns!!"""

## Create indicator variable for 'duplex' housing type 

# --NB: However, ensure that we place the new col at the correct index location
# NB2: We can look up index location of given col name via the .columns and .get_loc(column_name) methods:

# look up index location of 'single_fam' col
def look_up_index_loc_of_col(df, col):
    """ Return index location of given column, given column name"""
    index_of_col = df.columns.get_loc(col)
    return index_of_col


# get index location of 'single_fam' col--

# The column locations are uniform across each df stored within each subregion dictionary of dfs
# Ergo: We can apply this function to any *one* of the dfs (and from any subregion dict)

# Let's apply the function to the first df stored in the South Bay dictionary, to get index location of col:
index_for_single_fam = look_up_index_loc_of_col(
    sby_dict['craigslist_rental_sfbay_sby_01_05_2022'],  # refer to the first df in South Bay dict
    'single_fam'  # look up index location for 'single_fam' col
    )

# create indicator var using numpy and Pandas' str.contains() based on scraped rental listing attributes and descriptions  
def indicator_vars_from_scraped_data(df, col_to_parse, attr_substr):
    return pd.Series(np.where(df[col_to_parse].str.contains(attr_substr), 1, 0))



# Now, apply indicator_vars...() function to each df in the dictionaries of dfs:
def apply_func_to_dict_of_dfs_and_create_col(dict):
    """Create duplex indicator var col for each dataframe in a dictionary of dataframes"""
    for key in dict:
        dict[key]['duplex'] = indicator_vars_from_scraped_data(dict[key], 'attr_vars', 'duplex')
    return dict 

### Create and add duplex housing type indicator var via indicator_vars...() function to each subregion dictionary of dfs:

# South Bay
sby_dict = apply_func_to_dict_of_dfs_and_create_col(sby_dict)

# North Bay
nby_dict = apply_func_to_dict_of_dfs_and_create_col(nby_dict)

# Peninsula
pen_dict = apply_func_to_dict_of_dfs_and_create_col(pen_dict)


# East Bay

eby_dict = apply_func_to_dict_of_dfs_and_create_col(eby_dict)

# SF
sfc_dict = apply_func_to_dict_of_dfs_and_create_col(sfc_dict)

# Santa Cruz
scz_dict = apply_func_to_dict_of_dfs_and_create_col(scz_dict)




# ## c.) Next, we need to move the location of the 'duplex' col to match the new webcrawler specifications:

def move_col_loc_for_df_dict(dict):
    for key in dict:
        col = dict[key].pop('duplex')  # sequester duplex col from each df 
        dict[key]['duplex'] = dict[key].insert(index_for_duplex, col.name, col)  # move location of duplex col within each dataframe
    return dict 


## 1.) Before applying func, determine the index location where we want to move the 'duplex' col to: 
### --NB: How do we know the correct index location to place the 'duplex' col?-- Add 1 to the single_fam_index to get the location where we want to place the new 'duplex' col within the dataframe: 

# add 1 to the single_fam_index val to get the index location where we want to place the new 'duplex' col in each df:
index_for_duplex = index_for_single_fam + 1 # add 1 to get index location of where we will place the new 'duplex' col in df


## 2.) Now, move the 'duplex' col for each subregion dictionary of dataframes:
# South Bay 
sby_dict = move_col_loc_for_df_dict(sby_dict)


# North Bay data
nby_dict = move_col_loc_for_df_dict(nby_dict)


# Peninsula
pen_dict = move_col_loc_for_df_dict(pen_dict)

# East Bay
eby_dict = move_col_loc_for_df_dict(eby_dict)

# SF
sfc_dict = move_col_loc_for_df_dict(sfc_dict)

# Santa Cruz
scz_dict = move_col_loc_for_df_dict(scz_dict)


""" Finally, export each respective df to over-write the original csv files!"""

def overwrite_csvs_with_cleaned_data_dfs(df_dict, path):
    """Overwrite all of the respective original CSV files with the corresponding cleaned dataframes."""
    for df in df_dict:  # iterate over each DataFrame in dict
        df_dict[df].to_csv(path + "\\" + str(df)+'.csv', index=False) # use each key value (ie, df name from dict) as file name, and add .csv extension to each


# South Bay 
overwrite_csvs_with_cleaned_data_dfs(sby_dict, 'D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\scraped_data\\sfbay\\sby')

# North Bay data
overwrite_csvs_with_cleaned_data_dfs(nby_dict, 'D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\scraped_data\\sfbay\\nby')


# Peninsula
overwrite_csvs_with_cleaned_data_dfs(pen_dict, 'D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\scraped_data\\sfbay\\pen')


# East Bay
overwrite_csvs_with_cleaned_data_dfs(eby_dict, 'D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\scraped_data\\sfbay\\eby')

# SF
overwrite_csvs_with_cleaned_data_dfs(sfc_dict, 'D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\scraped_data\\sfbay\\sfc')

# Santa Cruz
overwrite_csvs_with_cleaned_data_dfs(scz_dict, 'D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\scraped_data\\sfbay\\scz')






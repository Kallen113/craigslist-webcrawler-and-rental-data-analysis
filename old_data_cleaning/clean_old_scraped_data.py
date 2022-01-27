# imports-- file processing
import os
import glob

# data analysis libraries & SQL libraries
import numpy as np
import pandas as pd


## import old scraped data, which needs to be cleaned  
def recursively_import_all_CSV_and_concat_to_single_df(parent_direc, fn_regex=r'*.csv'):
    """Recursively search parent directory, and look up all CSV files.
    Then, import all CSV files and concatenate into a single Pandas' df using pd.concat()"""
    path =  parent_direc # specify parent path of directories containing the scraped rental listings CSV data -- NB: use raw text--as in r'path...', or can we use the double-back slashes to escape back-slashes??
    df_concat = pd.concat((pd.read_csv(file) for file in glob.iglob(
        os.path.join(path, '**', fn_regex), 
        recursive=True)), ignore_index=True
        )  # os.path.join helps ensure this concatenation is OS independent

    return df_concat


## Clean data based on 3 main things:

# 1.) deduplicate data based on listing ids

# 2.) Remove misaligned data by:
# --firstly a.) using a regex pattern on the listing_urls (ie, rental listing urls)
# to check for the 'true' listing ids.
# Let's call this 'true_listing_ids'. 

"""-- *NB*: given that listing ids are always 10 digits, a regex that can parse the listing ids is
as follows:
<<<
regex_pattern = r"[0-9]{10}"   # search for any series of 10 consecutive digits 
"""
# --then: b.) identifying any rows in which the scraped ids column differ (ie, are not exactly equal to) 
# the 'true' listing ids. 

# 3.) Rename existing cols as needed, 
# and *add* and parse 3 or 4 additional dummy variable cols such as 'flat' & 'land'


# 1) deduplicate
def deduplicate_df(df):
    """Remove duplicate rows based on listing ids"""
    return df.drop_duplicates(keep='first', subset = ['ids'])


# 2.) Remove misaligned data:

# 2 a) Use regex to parse the 'true' listing ids:
def regex_create_pandas_col(df, col, regex_pattern):
    """Create new series for DataFrame based on regex pattern results, given DataFrame (df) and Series (ie, col). """
    return df[col].str.extract(regex_pattern) # apply regex pattern to parse data from col and create new column

# 2 b) Transform ids col to int, and then object, so that data types of ids and 'true_listing_ids' cols match each other (and without the unneeded 1st decimal points (ie, the '.0' values) )
def transform_col_to_int(df, col):
    return df[col].astype(float).astype('Int64') # use Int64 (or int64) due to the long id values


# 
def transform_dtype_of_col(df, col, data_type):
    """Convert col to specified data type"""
    return df[col].astype(data_type)


# 2 c) Remove rows from dataframe by comparing scraped ids vs the 'true' listing ids
def remove_rows_if_cols_not_equal(df, col1, col2):
    """Remove row from given DataFrame if values from col1 and col2 are not equal"""
    df = df.loc[df[col1] == df[col2]]
    return df


# 3 a.) Rename cols

def rename_cols(df, rename_cols_dict):
    df = df.rename(columns=rename_cols_dict)
    return df

# specify dictionary to specify what cols to rename, and vals for the renamed cols
dict_rename_cols = {
    'apt_type':'apt',
    'in_law_apt_type':'in_law_apt',
    'condo_type':'condo',
    'townhouse_type':'townhouse',
    'cottage_or_cabin_type':'cottage_or_cabin',
    'single_fam_type':'single_fam',
    'duplex_type':'duplex'    
    }


df = rename_cols(df, dict_rename_cols)

# 3 b.) Parse and add new dummy var cols




# create indicator var using numpy and Pandas' str.contains() based on scraped rental listing attributes and descriptions  
def indicator_vars_from_scraped_data(df, col_to_parse, attr_substr):
    return pd.Series(np.where(df[col_to_parse].str.contains(attr_substr), 1, 0))


# 'flat:
df['flat'] = indicator_vars_from_scraped_data(df, 'attr_vars', 'flat')

# land
df['land'] = indicator_vars_from_scraped_data(df, 'attr_vars', 'land')


# 3 c) Move the 2 new indicator cols to the corresponding locations to match the webcrawler

## Namely: move 'flat' to index just to right of 'duplex', and move 'land' to right of 'flat'

## Ergo: let's start by looking up index location of 'duplex':

# look up index location of given col
def look_up_index_loc_of_col(df, col):
    """ Return index location of given column, given column name"""
    index_of_col = df.columns.get_loc(col)
    return index_of_col



def move_col_loc_for_df_dict(df, col, index_loc_to_move):
    col = df.pop(col)  # sequester given col from each df 
    df = df.insert(index_loc_to_move, col.name, col)  # move location of given col within df
    return df 


# 3 d) Remove unneeded cols:
def remove_cols(df):
    df = df.drop(columns=['true_listing_ids', 'Unnamed: 0'])
    return df


# 4.) Export cleaned data to one large CSV file--in the 'old_scraped_data' sub-directory within the main sfbay folder containing scraped rental listings data:
def df_to_csv(df, direc, CSV_file_name):
    return df.to_csv(direc + '\\'+ CSV_file_name, index=False)


def main():
    ## specify directory and import data
    scraped_data_path = r"D:\\Coding and Code projects\\Python\\craigslist_data_proj\\old_scraped_data"
    # import data
    df = recursively_import_all_CSV_and_concat_to_single_df(scraped_data_path)
    print(f"Sanity check--overview (ie, via .info() method) of the imported scraped data data:: {df.info()}") # sanity check-examine size of dataset, columns, etc.
    
    ## Clean data
    # deduplicate:
    df = deduplicate_df(df)

    # 2) Remove misaligned data:

    # 2 a) First, use regex to parse the 'true' listing ids:

    # specify regex pattern to parse the 'true' listing ids from the listing urls:
    regex_pattern = r"([0-9]{10})"  # *NB*: wrap regex pattern in tuple to be able to use Pandas' str.extract() method, which our regex_create_pandas_col() function relies on!

    # parse the 'true' listing ids:
    df['true_listing_ids'] = regex_create_pandas_col(df, 'listing_urls', regex_pattern)

    # 2 b) Transform ids col to object, so that data types of ids and 'true_listing_ids' cols match each other
    # convert 'ids' to integer
    df['ids'] = transform_col_to_int(df, 'ids')
    # convert 'ids' data type to object:
    df['ids'] = transform_dtype_of_col(df, 'ids', str)

    # 2 c) Remove rows from dataframe by comparing scraped ids (ie, 'ids') vs the 'true' listing ids (ie, 'true_listing_ids')
    df = remove_rows_if_cols_not_equal(df, 'ids', 'true_listing_ids') 

    # 3 a) Rename cols:
    df = rename_cols(df, dict_rename_cols)
    
    # 3 b) Add and parse additional indicator var cols:
    # 'flat:
    df['flat'] = indicator_vars_from_scraped_data(df, 'attr_vars', 'flat') 

    # land
    df['land'] = indicator_vars_from_scraped_data(df, 'attr_vars', 'land')

    # 3 c) Move the 2 new indicator cols to the corresponding locations to match the webcrawler

    ## Namely: move 'flat' to index just to right of 'duplex', and move 'land' to right of 'flat'

    ## Ergo: let's start by looking up index location of 'duplex':

    # index location of 'duplex' col
    index_of_duplex = look_up_index_loc_of_col(df,  'duplex')  # look up index location for 'duplex' col)

    # Now, determine the new 'flat' col index location by adding 1 to the duplex index loc
    flat_new_loc = index_of_duplex + 1 # add 1 to duplex loc to determine the location where we want to move 'flat'

    # Determine 'land' col new index location--NB: Since we want 'land' 1 col to right of 'flat', simply add 1 to the flat_new_loc
    land_new_loc = flat_new_loc + 1 # add 1 to flat's (soon-to-be) new location so it is contiguous 1 col to the right

    # move 'flat' col:
    df = move_col_loc_for_df_dict(df, 'flat', flat_new_loc)

    # move 'land' col:
    df = move_col_loc_for_df_dict(df, 'land', land_new_loc) 

    ## 4) Export cleaned/transformed data:
    # NB: I've manually created a new sub-folder within the main scraped sfbay directory, to contain just these cleaned 'old' scraped data--ie, scraped via an older version of the webcrawler (namely: prior to the bug fix on Jan 1, 2022)
    direc_to_export = r"D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\scraped_data\\sfbay\\old_scraped_data"

    ## export
    df_to_csv(df, direc_to_export, 'all_sfbay_subregions_Oct_27_to_Dec_31_2021.csv')


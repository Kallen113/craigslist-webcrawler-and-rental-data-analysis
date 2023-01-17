import numpy as np
import pandas as pd
import os

## Perform data cleaning directly on specific lists before transforming the lists into a dictionary of lists:

# cities (ie, city names) data cleaning:
def clean_scraped_cities_data(dict_scraped_lists, cities_list):
    # transform 1st char of each word of each str element to upper-case
    dict_scraped_lists[cities_list] = [name_str.title() for name_str in dict_scraped_lists[cities_list]] # clean data by using.title() to transform the first char of each word of each list element to upper-case
    # remove parantheses markings from each element
    return [name_str.replace('(','').replace(')','') for name_str in dict_scraped_lists[cities_list]] # Remove all parantheses markings from each list element


def clean_listing_ids(dict_scraped_lists, ids):
    return [i.lstrip('post id: ') if 'post id: ' in i else i for i in dict_scraped_lists[ids]]


## parse kitchen data (ie, any type of kitchen)
def parse_kitchen_data(dict_scraped_lists, listing_descrip):
    # specify substring to look up in listing description to determine whether listing includes a kitchen
    kitchen_substr = 'kitchen'  
    # make sure we account for listings that explicitly specify that they do not have a kitchen  
    no_kitchen_substr = 'no kitchen'  
    # Transform all of the listing_descrip text data to lowercase (for ease of searching for substrings)
    dict_scraped_lists[listing_descrip] = [el.lower() for el in dict_scraped_lists[listing_descrip]]  # transform each element to lowercase using .lower() method
    # parse whether listing mentions that it includes a kitchen, and return as replacement for the (*currently empty*) kitchen list within the dict of list:
    return [1 if kitchen_substr in el else 0 if no_kitchen_substr in el else 0 for el in dict_scraped_lists[listing_descrip]]
    
## Perform data cleaning on specific lists within the dictionary of lists containing the scraped data:

## sqft data cleaning
def clean_scraped_sqft_data(dict_scraped_lists):
    """Clean data *after* all data has been scraped and contained within a *dictionary of lists*, not the initial lists! """
    sqf_substr = 'ft'
    return [val.split(sqf_substr)[0].split(' ')[-1] if sqf_substr in val else 'nan' for val in dict_scraped_lists['sqft']]  # parse the sqft data, and ensure it's sqft data by checking if given listing element contains the substring 'ft' 


# bedrooms data cleaning
def clean_scraped_bedroom_data(dict_scraped_lists):
    bed_substr = 'BR'
    # return [val.split(bed_substr)[0].split(' ')[-1] if bed_substr in val else 'nan' for val in bedroom_list]  # parse the bedrooms data, and ensure it's bedroom data by checking if given listing element contains the substring 'br' 
    return [val.strip().split('/')[0].strip().rsplit(bed_substr,1)[0] if bed_substr in val else 'nan' for val in dict_scraped_lists['bedrooms']]  # remove whitespace, then split based on backslash delimiter, index to 1st element, remove whitespace, and remove bed_substr from list


# bathrooms data cleaning
def clean_scraped_bathroom_data(dict_scraped_lists):
    bath_substr = 'Ba'
    # return [val[:-2] if bath_substr in val else 'nan' for val in bathroom_list]  
    return [val.strip().split('/')[1].strip().rsplit(bath_substr,1)[0] if bath_substr in val else 'nan' for val in dict_scraped_lists['bathrooms']]  # remove whitespace, then split based on backslash delimiter, index to 2nd element, remove whitespace, and remove bath_substr from list

def clean_scraped_date_posted_data(dict_scraped_lists):
    """ Clean datetime data (given we are no longer clicking to get the date): Namely: delete the "T" char that separates the year-month part of the datetime from the hour-minute-seconds datetime,  and replace the 'T' char with an empty space."""
    return [val.replace('T', ' ') for val in dict_scraped_lists['date_posted']]


## Create indicator variables using numpy and Pandas' str.contains() based on scraped rental listing attributes and descriptions  
def indicator_vars_from_scraped_data(df, col_to_parse, attr_substr):
    """ Parse scraped attribute data by parsing to indicator variable."""
    return np.where(df[col_to_parse].str.contains(attr_substr), 1, 0)


## Create indicator variable, but use 2 Pandas' str.contains() methods--including a str does *not* contain-- as arguments to avoid parsing home types that contain another as a substring--e.g., when we parse single_fam homes, we need to do a str.contains() on 'house', but simultaneously do a str does not contain on 'townhouse' since the substr house is contained within townhouse!
def indicator_vars_compound_str_contains(df, col_to_parse, attr_substr, attr_does_not_contain):
    """Parse attribute data to account for home types that have substrings that overlap with other ones.  For ex: single family homes are denoted on listings merely as 'house', which means this would overlap as a substring with townhouse home type listings.  So we need to account for this substring overlapping by using Pandas' logical not operator of '~' in tandem with a regular Pandas' str.contains() method as the arguments for a numpy.where() clause. 
    NB: attr_does_not_contain refers to the substring we want to do a Pandas' does not (ie, ~) contain, while attr_substr refers to the substring we want to do a Pandas' str.contains(), and the """
    return np.where((df[col_to_parse].str.contains(attr_substr)==True) & ~(df[col_to_parse].str.contains(attr_does_not_contain)==True), 1, 0)


# Parse the specific attributes and add to dataframe of scraped data--ie, use the create_indicator...() function above
def parse_attrs(df_from_dict):
    """Parse specific attributes from the rental listings' descriptions, and create indicator variables that we will add to the dataframe containing the scraped rental listings data. To do this, we will make calls to the above indicator_vars_from_scraped_data() function. """
    ## data wrangling-- parse specific attributes (e.g., 'cats_OK') from the attr_vars and listing_descrip cols:

    ## cats_OK & dogs_OK--ie, are cats or dogs allowed on given rental property:
    df_from_dict['cats_OK'], df_from_dict['dogs_OK'] = indicator_vars_from_scraped_data(df_from_dict,'attr_vars', 'cats are OK'), indicator_vars_from_scraped_data(df_from_dict,'attr_vars', 'dogs are OK')
    
    ## wheelchair accessible
    df_from_dict['wheelchair_accessible'] = indicator_vars_from_scraped_data(df_from_dict,'attr_vars', 'wheelchair accessible')
    
    ## Parse laundry and washer+dryer data:
    # laundry in building
    df_from_dict['laundry_in_bldg'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'laundry in bldg')
    # no laundry available on site
    df_from_dict['no_laundry'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'no laundry on site' )  # no laundry on site
    # washer and dryer appliances included
    df_from_dict['washer_and_dryer'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'w/d in unit' ) # parse w_d data-- ie, washer and dryer included
    # washer and dryer hookup (but no appliances)
    df_from_dict['washer_and_dryer_hookup'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'w/d hookups' ) # washer and dryer hookup  
    # laundry services available
    df_from_dict['laundry_on_site'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'laundry on site' ) # laundry_on_site

    ## Kitchen and household appliances data:
    # full kitchen data
    df_from_dict['full_kitchen'] = indicator_vars_from_scraped_data(df_from_dict, 'listing_descrip', 'full kitchen') 
    # dishwasher included
    df_from_dict['dishwasher'] = indicator_vars_from_scraped_data(df_from_dict, 'listing_descrip', 'dishwasher') 
    # refrigerator included
    df_from_dict['refrigerator'] = indicator_vars_from_scraped_data(df_from_dict, 'listing_descrip', 'refrigerator') 
    # oven included
    df_from_dict['oven'] = indicator_vars_from_scraped_data(df_from_dict, 'listing_descrip', 'oven') 
    
    ## Flooring attributes: 
    # carpet flooring
    df_from_dict['flooring_carpet'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flooring: carpet')
    # wood flooring
    df_from_dict['flooring_wood'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flooring: wood')
    # tile flooring
    df_from_dict['flooring_tile'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flooring: tile')
    # hardwood flooring
    df_from_dict['flooring_hardwood'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flooring: hardwood')
    # other/unclassified flooring
    df_from_dict['flooring_other'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flooring: other')

    ## Parse rental type data-- NB: At least for the most part, each rental listing on craigslist will always explicitly state what type of home is up for rent.
    # apartments
    df_from_dict['apt'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'apartment')  # apt data:
    # in law 
    df_from_dict['in_law_apt'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'in-law') # in-law apt--NB: in-law apartments are formally called "Accessory Dwelling Units (ADUs)"". A more detailed description  is available at CA's HCD department: <https://www.hcd.ca.gov/policy-research/accessorydwellingunits.shtml>
    # condo properties
    df_from_dict['condo'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'condo') # condo rental type
    # townhouses
    df_from_dict['townhouse'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'townhouse')  # townhouse rental type
    # cottage or cabin
    df_from_dict['cottage_or_cabin'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'cottage/cabin')  # cottage or cabin
    # single family homes
    df_from_dict['single_fam'] = indicator_vars_compound_str_contains(df_from_dict, 'attr_vars', 'house', 'townhouse')  # parse single-family home type listings while also ensuring we also filter out any townhouse listings!    df_from_dict['duplex'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'duplex')  # duplex rental type
    # duplex
    df_from_dict['duplex'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'duplex')  # duplex rental type
    # flat property type
    df_from_dict['flat'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flat') # flat (ie, large apartment-like) rental type
    # land-- e.g., RV lot
    df_from_dict['land'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'land') # land rental type--e.g., RV parking

    ## furnished rental unit
    df_from_dict['is_furnished'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'furnished')

    ## Parse garage & parking data: 
    # attahced garage
    df_from_dict['attached_garage'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'attached garage') #attached_garage 
    # detached garage
    df_from_dict['detached_garage'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'detached garage') # detached_garage
    # carport
    df_from_dict['carport'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'carport')  # carport
    # off street parking
    df_from_dict['off_street_parking'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'off-street parking') # off_street_parking
    # no parking options available on site
    df_from_dict['no_parking'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'no parking')  # no parking 

    # Electrical vehicle charging
    df_from_dict['EV_charging'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'EV charging') 

    ## air conditioning amenity data
    df_from_dict['air_condition'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'air conditioning') 

    ## Parse no smoking allowed data
    df_from_dict['no_smoking'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'no smoking') 

def clean_bedroom_studio_apt_data(df, col_to_parse, col_to_assign):
    """Clean bedrooms data for rental listings that comprise studio apartments and have 'nan' values, indicating ."""
    # look up whether given rental listing record comprises a studio apt
    substr_studio_apt_lookup = 'studio'
    # change bedrooms data from 'nan' to 0 (ie, 0 bedrooms) for studio apt rental listings that currently have bedrooms val of 'nan':
    conditions = [
        (df[col_to_parse].str.contains(substr_studio_apt_lookup, case=False))\
            & (df[col_to_assign].str.contains('nan')) # joint condition will be true only if: a) rental listing comprises a studio apt (based on case-insensitive search for 'studio' substr ) & b) current val for record in bedrooms col is 'nan'     
        ]
    # assign val of 0 to bedrooms col if joint condition is true
    choices = [0]  
    # replace bedrooms data with val of 0 if conditions are true, else leave val of bedrooms unchanged 
    return np.select(conditions, choices, default = df[col_to_assign])  

def clean_listing_ids_and_remove_nan_substr(df, col_to_clean, substr_to_filter_out):
    return df[df[col_to_clean].str.contains(substr_to_filter_out)==False]

def print_scraped_sanity_checks(df):
    print("\n\nSanity check on scraped data from Dataframe:\n\n")
    print(f"Listing ids: {df['ids']}\n")
    print(f"Listing urls: {df['listing_urls']}\n")
    print(f"\nPrices: {df['prices']}\n\n")
    

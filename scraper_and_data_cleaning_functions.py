import numpy as np
import pandas as pd
import os

def clean_scraped_sqft_data(sqft_list):
    sqf_substr = 'ft'
    return [val.split(sqf_substr)[0].split(' ')[-1] if sqf_substr in val else 'nan' for val in sqft_list]  # parse the sqft data, and ensure it's sqft data by checking if given listing element contains the substring 'ft' 


# bedrooms data cleaning
def clean_scraped_bedroom_data(bedroom_list):
    bed_substr = 'br'
    return [val.split(bed_substr)[0].split(' ')[-1] if bed_substr in val else 'nan' for val in bedroom_list]  # parse the bedrooms data, and ensure it's bedroom data by checking if given listing element contains the substring 'br' 


# bathrooms data cleaning
def clean_scraped_bathroom_data(bathroom_list):
    bath_substr = 'Ba'
    return [val[:-2] if bath_substr in val else 'nan' for val in bathroom_list]  


# cities (ie, city names) data cleaning:
def clean_scraped_cities_data(cities_list):
    # transform 1st char of each word of each str element to upper-case
    cities_list = [name_str.title() for name_str in cities_list] # clean data by using.title() to transform the first char of each word of each list element to upper-case
    # remove parantheses markings from each element
    return [name_str.replace('(','').replace(')','') for name_str in cities_list] # Remove all parantheses markings from each list element


## parse kitchen data (ie, any type of kitchen)
def parse_kitchen_data(kitchen_list, listing_descrip):
    # specify substring to look up in listing description to determine whether listing includes a kitchen
    kitchen_substr = 'kitchen'  
    # make sure we account for listings that explicitly specify that they do not have a kitchen  
    no_kitchen_substr = 'no kitchen'  
    # Transform all of the listing_descrip text data to lowercase (for ease of searching for substrings)
    listing_descrip = [el.lower() for el in listing_descrip]  # transform each element to lowercase using .lower() method
    # parse whether listing mentions that it includes a kitchen
    kitchen_list =  [1 if kitchen_substr in el else 0 if no_kitchen_substr in el else 0 for el in listing_descrip]
    return kitchen_list

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
    df_from_dict['laundry_in_bldg'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'laundry in bldg')
    df_from_dict['no_laundry'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'no laundry on site' )  # no laundry on site
    df_from_dict['washer_and_dryer'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'w/d in unit' ) # parse w_d data-- ie, washer and dryer included
    df_from_dict['washer_and_dryer_hookup'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'w/d hookups' ) # washer and dryer hookup  
    df_from_dict['laundry_on_site'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'laundry on site' ) # laundry_on_site

    ## Kitchen and household appliances data:
    df_from_dict['full_kitchen'] = indicator_vars_from_scraped_data(df_from_dict, 'listing_descrip', 'full kitchen') # full kitchen data
    df_from_dict['dishwasher'] = indicator_vars_from_scraped_data(df_from_dict, 'listing_descrip', 'dishwasher') # dishwasher included
    df_from_dict['refrigerator'] = indicator_vars_from_scraped_data(df_from_dict, 'listing_descrip', 'refrigerator') # refrigerator included
    df_from_dict['oven'] = indicator_vars_from_scraped_data(df_from_dict, 'listing_descrip', 'oven') # oven included
    
    ## Flooring attributes: 
    df_from_dict['flooring_carpet'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flooring: carpet')
    df_from_dict['flooring_wood'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flooring: wood')
    df_from_dict['flooring_tile'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flooring: tile')
    df_from_dict['flooring_hardwood'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flooring: hardwood')
    df_from_dict['flooring_other'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flooring: other')

    ## Parse rental type data-- NB: At least for the most part, each rental listing on craigslist will always explicitly state what type of home is up for rent.
    df_from_dict['apt'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'apartment')  # apt data:
    df_from_dict['in_law_apt'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'in-law') # in-law apt--NB: in-law apartments are formally called "Accessory Dwelling Units (ADUs)"". A more detailed description  is available at CA's HCD department: <https://www.hcd.ca.gov/policy-research/accessorydwellingunits.shtml>
    df_from_dict['condo'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'condo') # condo rental type
    df_from_dict['townhouse'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'townhouse')  # townhouse rental type
    df_from_dict['cottage_or_cabin'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'cottage/cabin')  # cottage or cabin
    df_from_dict['single_fam'] = indicator_vars_compound_str_contains(df_from_dict, 'attr_vars', 'house', 'townhouse')  # parse single-family home type listings while also ensuring we also filter out any townhouse listings!    df_from_dict['duplex'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'duplex')  # duplex rental type
    df_from_dict['duplex'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'duplex')  # duplex rental type
    df_from_dict['flat'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'flat') # flat (ie, large apartment-like) rental type
    df_from_dict['land'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'land') # land rental type--e.g., RV parking

    ## furnished rental unit
    df_from_dict['is_furnished'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'furnished')

    ## Parse garage & parking data: 
    df_from_dict['attached_garage'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'attached garage') #attached_garage 
    df_from_dict['detached_garage'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'detached garage') # detached_garage
    df_from_dict['carport'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'carport')  # carport
    df_from_dict['off_street_parking'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'off-street parking') # off_street_parking
    df_from_dict['no_parking'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'no parking')  # no parking 

    # Electrical vehicle charging
    df_from_dict['EV_charging'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'EV charging') 

    ## air conditioning amenity data
    df_from_dict['air_condition'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'air conditioning') 

    ## Parse no smoking allowed data
    df_from_dict['no_smoking'] = indicator_vars_from_scraped_data(df_from_dict, 'attr_vars', 'no smoking') 


def print_scraped_sanity_checks(df):
    print("\n\nSanity check on scraped data from Dataframe:\n\n")
    print(f"Listing ids: {df['ids']}\n")
    print(f"Listing urls: {df['listing_urls']}\n")
    print(f"\nPrices: {df['prices']}\n\n")  
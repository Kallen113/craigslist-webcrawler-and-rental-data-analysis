# data analysis libraries 
import numpy as np
import pandas as pd

# filter Santa Cruz data if city is mislabelled as being within the county
def clean_mislabelled_santa_cruz_data(santa_cruz_cities: list, df):
    """Some of the craigslist rental listings are mislabelled as being in Santa Cruz.
    This function will look up data labelled as a.) subregion=='scz', but also 
    b.) check if the given city (ie, based on city name in cities col) actually resides within Santa Cruz county."""
    filered_df = df.dropna(subset = ['cities'], how='any') # remove any records without city names (ie, null for cities column)
    filered_df = filered_df[(filered_df['sub_region'].str.contains('scz')) \
        & (filered_df['cities'].str.contains('|'.join(san_cruz_cities), case=False))] # check that sub_region is scz, and then do str contains filters to look up each santa cruz city  
    return filered_df 

# specify list of all santa cruz county cities
san_cruz_cities = [
    'Santa Cruz', 'Capitola' 'Scotts Valley', 'Watsonville', 'Amesti', 'Larkin Valley',
    'Aptos', 'Bonny Doon', 'Ben Lomond', 'Boulder Creek',
    'Brookdale',
    'Bonny Doon',
    'Corralitos',
    'Davenport',
    'Felton',
    'Day Valley',
    'Freedom',
    'Interlaken',
    'La Selva Beach',
    'Live Oak',
    'Lompico',
    'Mount Hermon',
    'Pajaro Dunes',
    'Paradise Park',
    'Pasatiempo',
    'Rio del Mar',
    'Pleasure Point',
    'Seacliff',
    'Soquel',
    'Twin Lakes',
    'Zayante'
    ]



# ## *apply func to clean data by removing all records that are mislabelled as being within Santa Cruz county

# df = clean_mislabelled_santa_cruz_data(san_cruz_cities, df) # clean Santa Cruz data




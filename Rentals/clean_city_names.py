# imports-- file processing
import datetime
import os
import glob

import datetime

# data analysis libraries & SQL libraries
import numpy as np
import pandas as pd


# clean SJ or other city name data
def clean_given_city_names_data(city_name, list_of_neighborhood_names, df):
    """In the craigslist listings, the name of the 'small' span HTML object
    --which contains the city names--shows various names for regions of 
    cities such as San Jose, such as 'San Jose downtown', 'San Jose South', etc.

    We will use str contains to look up the given city substring (e.g., 'San Jose'),
    and replace these with simply the name of the city itself: ie, 'San Jose'."""
    # 1.) remove records that are missing city names from dataset
    filtered_df = df.dropna(subset = ['cities'], how='any') # remove any records that are missing city names
    #2.) split cities that are listed as having multiple city names with a slash delimiter (ie, '/'), and parse the first city name of each such row
    filtered_df['cities'] = filtered_df['cities'].str.split('/', expand = False).str[0]   # split cities based on presence of the forward-slash delimiter (ie: '/'), and then parse only the 1st such element. This way, we will have only the primary (first) city listed for each 'split' city name. 

    # 3.) use str.contains() to look up city names with given neighborhood names. Replace these with simply the city name of 'San Jose'
    filtered_df['cities'] =  np.where(filtered_df['cities'].str.contains('|'.join(list_of_neighborhood_names), case=False), city_name, filtered_df['cities']) # assign city name for any rows containing given city neighborhood names, else simply leave row unchanged.     
    return filtered_df


# specify list of neighborhoods for San Jose, Oakland, and other cities that use neighborhood names on craigslist instead of the main city name by default

# South Bay cities: 
sj_neighborhoods = ['San Jose', 'Cambrian' 'East Foothills', 'Evergreen']

santa_clara_neighborhoods = ['Santa Clara', 'Willow Glen']

# Easy Bay cities:
oakland_neighborhoods = ['Oakland', 'Lake Merritt']

alameda_neighborhoods = ['Alameda']

hayward_neighborhoods = ['Hayward']

richmond_neighborhoods = ['Richmond']


# clean SF data--change neighborhood names to simply SF city name
def clean_city_names_for_sf(list_of_sf_neighborhoods, df):
    """In sfbay craiglist listings,
    the name of the 'small' span HTML object
    --which contains the city names--shows the 
    names of SF neighborhoods instead of the city itself.
    
    Since we are only interested in city-level data,
    not within-city data such as city neighborhoods,
    we will replace any SF neighborhood names
    with simply the name of the city (ie, San Francisco).
    
    Make a case-insensitive search, since we only care 
    about basic spellings of neighborhood names. Denote
    any non-SF data as empty strings, and then remove 
    these records from dataset since we only want SF data."""

    sf_neighborhoods = list_of_sf_neighborhoods # input list of all neighborhoods in SF
    # 1.) remove records that are missing city names from dataset
    filtered_df = df.dropna(subset = ['cities'], how='any') # remove any records that are missing city names
    #2.) split cities that are listed as having multiple city names with a slash delimiter (ie, '/'), and parse the first city name of each such row
    filtered_df['cities'] = filtered_df['cities'].str.split('/', expand = False).str[0]   # split cities based on presence of the forward-slash delimiter (ie: '/'), and then parse only the 1st such element. This way, we will have only the primary (first) city listed for each 'split' city name. 
    
    # 3.) use str.contains() to look up any neighborhoods that are located within SF, and use np.where() to replace the neighborhood names with simply the city name (ie, 'San Francisco'). NB: if no SF neighborhoods are found, then impute row as null using np.null.  
    filtered_df['cities'] = np.where(filtered_df['cities'].str.contains('|'.join(sf_neighborhoods), case=False), "San Francisco", '') # assign city name for any rows that contain sf neighborhood names for the cities col
    # 4.) Remove all of the rows with cities imputed as empty strings--ie, because they are not actually located within San Francisco
    filtered_df_final = filtered_df[filtered_df['cities'].str.strip().astype(bool)]
    return filtered_df_final


# specify list of all sf neighborhoods
sf_neighborhoods = [
    'Anza Vista', 'Ashbury Heights', 'Ashbury Hts', 'Alamo Square'
    'Balboa Hollow', 'Balboa Terrace', 'Bayview', 'Belden Place', 'Bernal Heights',
    'Lower Pac Hts', 'Mission District', 'Lower Nob Hill', 'Downtown',
    'Buena Vista', 'Butchertown (Old and New)','Castro', 'Cathedral Hill', 'Cayuga Terrace',
    'China Basin','Chinatown', 'Civic Center','Clarendon Heights', 'Cole Valley',
    'Corona Heights', 'Cow Hollow','Crocker-Amazon','Design District','Diamond Heights', 'Diamond Hts', 'Dogpatch',
    'Dolores Heights', 'Duboce Triangle',' Embarcadero', 'Eureka Valley',
    'Excelsior', 'Fillmore', 'Financial District', "Fisherman's Wharf", 'Forest Hill', 'Forest Knolls', 'Glen Park', 'Golden Gate Heights', 
    'Haight', 'Hayes Valley', 'Hunters Point', 'India Basin', 'Ingleside', 'Inner Sunset', 'Jackson Square', 'Japantown',
    'Jordan Park', 'Laguna Honda', 'Lake Street', 'Lakeside', 'Lakeshore', 'Laurel Heights', 'Lincoln Manor', 'Little Hollywood', 'Little Russia',
    'Little Saigon', 'Lone Mountain', ' Lower Haight', 'Lower Pacific Heights', 'Lower Pac Hts', 'Lower Nob Hill', ' Marina', 'Merced Heights', 'Merced Manor', 'Midtown Terrace',
    'Mid-Market', 'Miraloma Park', 'Mission Bay', 'Mission', 'Mission Dolores', 'Mission Terrace', 'Monterey Heights', 'Mount Davidson',
    'nob hill', 'Noe Valley', 'nopa', 'North Beach', 'Panhandle', 'Oceanview','Outer Mission', ' Outer Sunset', 'Pacific Heights', 'Parkmerced',
    'Parkside', 'Parnassus', 'Polk Gulch', 'Portola', 'Portola Place', 'portola district'
    'Potrero Hill', 'Presidio', 'Presidio Heights', 'Richmond', 'Richmond District', 'Rincon Hill', 'Russian Hill', 'Saint Francis Wood', 'Sea Cliff', 
    'Sherwood Forest', 'South Beach', 'Silver Terrace', 'South End', 'South of Market', 'soma', 'Sunnydale', 'Sunnyside', 'Sunset', 
    'Telegraph Hill', 'Tenderloin', 'Treasure Island', 'Twin Peaks','Union Square', 'University Mound',
    'USF', 'Upper Market', 'Visitacion Valley', 'Vista del Mar', 'West Portal', 'Western Addition',
    'Westwood Highlands', 'Westwood Park', 'Yerba Buena', 'SFSU', 'CCSF', 'Fort Mason', 'Laurel Hts', 'UCSF', 'San Francisco'
    'Turk St', 'Showplace Square'
    ]






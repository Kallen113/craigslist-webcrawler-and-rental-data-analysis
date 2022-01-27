def clean_split_city_names(df, address_critera: list, neighborhood_criteria:list, split_city_delimiters: list, incorrect_city_names:dict, cities_not_in_region:dict, cities_that_need_extra_cleaning:dict):
    """Clean city names data in several ways:
    a.) Remove extraneous address & neighborhood data placed in the city names HTML object, such as 'Rd', 'Blvd', or 'Downtown'.
    b.) Unsplit city names data that are split via ',' & '/' delimiters.
    c.) Replace abbreviated or mispelled city names, and remove city names that do not exist within the SF Bay Area (e.g., 'Redding').
    d.) Remove any digits/integers within the city names data--ie, by using a '\d+' regex as the argument of str.replace() and replace it with empty strings.
    e.) Remove any city names records thast are left with merely empty strings (ie, the other steps removed all data for that given cities record).
    f.) Remove any whitespace to avoid the same city names from being treated as different entities by Pandas, Python, or SQL. 
    g.) Use str.capwords() to capitalize words (ie, excluding apostrophes).
    h.) Replace city names that are mispelled after having removed various street and neighborhood substrings such as 'St' or 'Ca'--e.g., '. Helena' should be 'St. Helena'. """
    # specify extraneous street & address data (e.g., 'Rd') that we want to remove from the city names column:
    addr_criteria = '|'.join(address_critera) # Join pipe ('|') symbols to address list so we can str.split() on any one of these criteria (ie, 'or' condition splitting on each element separated by pipes):
    # specify extraneous neighborhood criteria we should also remove from col
    nbhood_criteria = '|'.join(neighborhood_criteria) # remove neighborhood names as well as state abbreviation (shown on website as 'Ca') that is shown without the usual comma delimiter!
    # b.) specify delimiters we need to refer to un-split city names:
    split_city_delimiters = '|'.join(split_city_delimiters) # join pipes to delimiters so we can use str.split() based on multiple 'or' criteria simultaneously
    # clean city names data by removing extraneous address & neighborhood data, and unsplitting city names based on ',' & '\' delimiters
    df['cities'] =  df['cities'].str.split(addr_criteria).str[-1].str.replace(nbhood_criteria, '', case=True).str.lstrip()
    df['cities'] = df['cities'].str.split(split_city_delimiters).str[0] #unsplit city names based on comma or forward-slash delimiters
    # c.) replace specific abbreviated or mispelled city names, and remove cities that are not actually located in the sfbay region:
    df = df.replace({'cities':incorrect_city_names}) # replace mispelled & abbreviated city names
    df = df.replace({'cities':cities_not_in_region})  # remove (via empty string) cities that are not actually located in the sfbay region
    # d.) Remove digits/integer-like data from cities column:
    df['cities'] = df['cities'].str.replace('\d+', '')  # remove any digits by using '/d+' regex to look up digits, and then replace with empty string
    # e.) Remove any rows that have empty strings or null values for cities col (having performed the various data filtering and cleaning above)
    df = df[df['cities'].str.strip().astype(bool)] # remove rows with empty strings (ie, '') for cities col 
    df = df.dropna(subset=['cities']) # remove any remaining 'cities' null records
    # f.) Remove whitespace
    df['cities'] = df['cities'].str.strip() 
    # g.) capitalize the city names using str.capwords() 
    df['cities'] = df['cities'].str.split().apply(lambda x: [val.capitalize() for val in x]).str.join(' ')
    # h) Replace city names that are mispelled after having removed various street and neighborhood substrings such as 'St' or 'Ca'--e.g., '. Helena' should be 'St. Helena' & 'San los' should be 'San Carlos'. Also, remove any non-Bay Area cities such as Redding:
    # df['cities'] = df['cities'].str.lower() # transform all records to lower-case, for ease of cleaning the data
    df = df.replace({'cities':cities_that_need_extra_cleaning})
    return df

# specify various address and street name that we need to remove from the city names 
address_criteria = ['Boulevard', 'Blvd', 'Road', 'Rd', 'Avenue', 'Ave', 'Street', 'St', 'Drive', 'Dr', 'Real', 'E Hillsdale Blvd'] 
# specify various extraneous neighborhood names such as 'Downtown' 
neighborhood_criteria = ['Downtown', 'Central/Downtown', 'North', 'California', 'Ca.', 'Bay Area', 'St. Helena', 'St', 'nyon', 
'Jack London Square', 'Walking Distance To', 'El Camino', 'Mendocino County', 'San Mateo County', 'Alameda County', 'Rio Nido Nr', 'Mission Elementary', 
'Napa County', 'Golden Gate', 'Jennings', 'South Lake Tahoe', 'Tahoe Paradise', 'Kingswood Estates', 'South Bay', 'Skyline', 'San Antonio Tx', 
'East Bay', 'Morton Dr'] 

# specify what delimiters we want to search for to unsplit the split city names data:
split_city_delimiters =  [',', '/']
# specify dictionary of abbreviated & mispelled cities:
incorrect_city_names = {'Rohnert Pk':'Rohnert Park', 'Hillsborough Ca': 'Hillsborough', 'South Sf': 'South San Francisco', 'Ca':'', 'East San Jose':'San Jose', 'Vallejo Ca':'Vallejo', 'Westgate On Saratoga .':'San Jose', 'Bodega':'Bodega Bay', 'Briarwood At Central Park':'Fremont', 'Campbell Ca':'Campbell', 'Almaden':'San Jose', '.':'', 'East Foothills':'San Jose', 'Lake County':'', 'Redwood Shores':'Redwood City'}

# specify dictionary of cities that are not located in sfbay (ie, not located in the region):
cities_not_in_region = {'Ketchum':'', 'Baypoinr':'', 'Quito': '', 'Redding':'', 'Bend' :''}

# specify dictionary of city names that are mispelled after having removed various street and neighborhood substrings:
cities_that_need_extra_cleaning = {'. Helena': 'St. Helena', '. Helena Deer Park': 'St. Helena', 'San Los':'San Carlos', 'Tro Valley':'Castro Valley', 'Rohnert Pk':'Rohnert Park',
'Pbell':'Campbell', 'Pbell Ca':'Campbell', 'American Yon':'American Canyon'}

# clean city names data:
clist_rental = clean_split_city_names(clist_rental, address_criteria, neighborhood_criteria, split_city_delimiters, incorrect_city_names, cities_not_in_region, cities_that_need_extra_cleaning)
# sanity check
print(f"Sanity check--after cleaning the city names, let's examine some of the cleaned data: {clist_rental.cities.value_counts().tail(10)}")
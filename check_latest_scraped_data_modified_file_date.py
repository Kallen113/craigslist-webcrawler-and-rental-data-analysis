import os
import glob
import inquirer
import time


"""NB!:
This script checks for the latest file dates among the webcrawler program's scraped data.

Namely: this script shows the latest CSV files that were outputted by the webcrawler,
by looking up saved file dates within the scraped_data subdirectory.

Why use this script?:
To check which subregion--for a given craigslist region--you might want
to run the webcrawler for next. 

For example: If the last modified file for a given
subregion is older, then you should probably run the webcrawler
sooner than for subregions with more recent data."""


def get_current_direc():
    return os.getcwd()

def get_subdirectory_as_full_path(current_direc, subdirectory_folder):
    full_path_to_subdirectory = os.path.join(current_direc, subdirectory_folder)
    return full_path_to_subdirectory

# 1a) prompt user--via terminal-- to specify which region to update database via newest scraped data 
def prompt_user_to_specify_region_to_update(region_codes):
    regions_lis = [
        inquirer.List('clist_region',
        message="What craigslist region would you like to use to update the database--NB: please select from the dropdown values?",
        choices= region_codes,  # in put the various subregions as the elements for the user to select from this list.
        carousel=True  # allow user to scroll through list of values more seamlessly
        ),
        ]
    region = inquirer.prompt(regions_lis) # prompt user to select one of the regions in command line, from the dropdown list defined above
    region = region["clist_region"]

    # print the region code that was selected
    print(f'The region you selected is:\n{region}\n')

    # return the region name & the URL corresponding to the selected region:
    return region   # NB: we need to return the region, but we also need the URL--ie, the dict value-- of the given region name (ie, key) instead!

def return_hompeage_URL_for_given_region(region_vals:dict, region_name: str):
    """Given the region the user selects via terminal, return the corresponding region's hompeage URL for craigslist."""
    # return the value of the corresponding key--ie, return the URL for the given region
    return region_vals.get(region_name)  # return URL for given region

# Parse region code from user's region selection
def parse_region_code_from_craigslist_URL(region_URL):
    """From the region_URL--which is given by the user's selection of the region_name, use .split() method to parse the region code for the given URL, which we will supply as an arg to the Craigslist_Rentals class's init() method, from the selenium_webcrawler.py (ie, the main webcrawler script!!)."""
    return region_URL.split('//')[1].split('.')[0]



# def latest_modified_date_for_all_subdirectories_of_path(path):
#     file_list = []
#     for (root, dirs, files) in os.walk(path):
#         for file in files:
#             a = os.stat(os.path.join(root, file))
#             file_list.append([file, time.ctime(a.st_atime)])
#     print(file_list)



# def latest_modified_date_for_all_subdirectories_of_path(path):
#     N_MOST_RECENT = 2
#     for entry in os.listdir(path):
#         subpath = os.path.join(path, entry)
#         if os.path.isdir(subpath):
#             for subentry in os.listdir(subpath):
#                 subentrypath = os.path.abspath(os.path.join(subpath, subentry))
#                 if os.path.isdir(subentrypath):
#                     csv_files = glob.iglob(os.path.join(subentrypath, '*.csv'))
#                     sorted_filenames = sorted(csv_files, key=os.path.getmtime)
#                     # Create list of filenames of the N most recent files.
#                     most_recent = [os.path.split(name)[-1] # Extract filename from path.
#                                         for name in sorted_filenames[-N_MOST_RECENT:]]
#                     print(f'{N_MOST_RECENT} most recent CSV files in "{subentrypath}":\n'
#                         f'  {most_recent}')

def latest_modified_date_for_all_subdirectories_of_path(path):
    N_MOST_RECENT = 1
    for entry in os.listdir(path):
        subpath = os.path.join(path, entry)
        if os.path.isdir(subpath):
            for subentry in os.listdir(subpath):
                subentrypath = os.path.abspath(os.path.join(subpath, subentry))
                if os.path.isdir(subentrypath):
                    csv_files = glob.iglob(os.path.join(subentrypath, '*.csv'))
                    sorted_filenames = sorted(csv_files, key=os.path.getmtime)
                    # Create list of filenames of the N most recent files.
                    most_recent = [os.path.split(name)[-1] # Extract filename from path.
                                        for name in sorted_filenames[-N_MOST_RECENT:]]
                    
                    print(f'{N_MOST_RECENT} most recent CSV files in "{subentrypath}":\n'
                        f'  {most_recent}\n') 

def main():
    # get current path
    current_direc = get_current_direc()

    # sanity check
    print(f"Current directory (ie, the webcrawler's root directory):\n{current_direc}")

    # name of scraped_data folder
    scraped_data_folder_name = 'scraped_data' 

    # get full path to scraped_data subdirectory
    scraped_data_path = get_subdirectory_as_full_path(current_direc, scraped_data_folder_name)

    # sanity check
    print(f"Full path to webcrawler's scraped data:\n{scraped_data_path}")

    ## Next, select specific region:
    # specify names of metropolitan craigslist region names and their corresponding craigslist urls, store in dict
    clist_region_and_urls = {
        'SF Bay Area, CA':'https://sfbay.craigslist.org/',
        'San Diego, CA':'https://sandiego.craigslist.org/',
        'Chicago, IL':'https://chicago.craigslist.org/',
        'Seattle, WA':'https://seattle.craigslist.org/',
        'Los Angeles, CA':'https://losangeles.craigslist.org/',
        'Phoenix, AZ':'https://phoenix.craigslist.org/',
        'Portland, OR':'https://portland.craigslist.org/',
        'Dallas/Fort Worth, TX':'https://dallas.craigslist.org/',
        'Minneapolis/St. Paul, MN':'https://minneapolis.craigslist.org/',
        'Boston, MA':'https://boston.craigslist.org/',
        'Washington, D.C.':'https://washingtondc.craigslist.org/',
        'Atlanta, GA':'https://atlanta.craigslist.org/',
        'Miami, FL':'https://miami.craigslist.org/',
        'Hawaii (subregions by island)':'https://honolulu.craigslist.org/',
        'Detroit, MI':'https://detroit.craigslist.org/',
        'New York City, NY':'https://newyork.craigslist.org/',
        'Vancouver, Canada':'https://vancouver.craigslist.org/',
        'Toronto, Canada':'https://toronto.craigslist.org/'
        }
 
    # prompt user to select which region for updating the database:
    region_name = prompt_user_to_specify_region_to_update(clist_region_and_urls)

    region_URL = return_hompeage_URL_for_given_region(clist_region_and_urls, region_name)

    # parse region code from homepage url of selected region:
    region_code = parse_region_code_from_craigslist_URL(region_URL)

    # get full path to scraped_data subdirectory for given region, by joining the region_code subdirectory to the full scraped_data_path directory:
    scraped_data_and_region_path = get_subdirectory_as_full_path(scraped_data_path, region_code)

    # sanity check
    print(f"Full path to webcrawler's scraped data for {region_code} region:\n{scraped_data_and_region_path}\n")

    # # print latest modified date for each subdirectory (ie, regions and subregions in this case) of scraped_data
    latest_modified_date_for_all_subdirectories_of_path(scraped_data_path)
    # latest_modified_date_for_all_subdirectories_of_path(scraped_data_and_region_path)





if __name__ == "__main__":
    main()

    
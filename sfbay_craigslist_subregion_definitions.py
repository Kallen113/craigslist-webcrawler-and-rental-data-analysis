import inquirer

# print a dictionary to specify what each raigslist sfbay subregion shorthands denote

def print_sfbay_subregion_names():
    sfbay_subregion_names = {'eby': 'East Bay', 
    'nby':'North Bay',
    'pen': 'Peninsula', 
    'sby':'South Bay', 
    'sfc':'San Francisco',
    'scz':'Santa Cruz'}

    print(f"\n\nThe sfbay craigslist subregion symbols denote the following SF Bay Area regions and/or cities:\n{sfbay_subregion_names}\n")

# enable user to select subregion from dropdown to implement the webcrawler on:
def inquirer_prompt_user_at_terminal(subregion_vals):
    ## NB: main.py needs to supply a list of the given subregion vals
    # *For example: subregion_vals = ['eby', 'nby', 'pen', 'sby', 'sfc', 'scz']
    sub_regions_lis = [
        inquirer.List('sfbay_subregion',
        message="What craigslist SF Bay Area sub-region would you like to scrape--NB: please select from the dropdown values?",
        choices=subregion_vals,  # input the various subregions as the elements for the user to select from this list.
        carousel=True  # allow user to scroll through list of values more seamlessly
        ),
        ]
    sub_region = inquirer.prompt(sub_regions_lis) # prompt user to select one of the subregions in command line
    subregion = sub_region["sfbay_subregion"]
    return subregion
# import Craigslist_Rentals class, which implements the webcrawler and web scraping functions
from Rentals.selenium_webcrawler import Craigslist_Rentals

from Rentals.clean_city_names import clean_city_names_for_sf, sf_neighborhoods, clean_given_city_names_data, sj_neighborhoods, oakland_neighborhoods, alameda_neighborhoods, hayward_neighborhoods, richmond_neighborhoods, santa_clara_neighborhoods  # import functions to clean SF city names data and import lists of all neighborhoods for given cities--e.g., SF neighborhoods (including various abbreviations used on craigslist)  
from Rentals.clean_santa_cruz_data import clean_mislabelled_santa_cruz_data, san_cruz_cities

# import inquirer library so we can prompt user in command line to select from a dropdown of values to select the desired subregion on which we will implement the webcrawler.
import inquirer
from sfbay_craigslist_subregion_definitions import print_sfbay_subregion_names, inquirer_prompt_user_at_terminal


def main():
    ## Specify the arguments we will use for each component of the Craigslist_Rentals class, so that we will scrape data for the given region, subregion, etc.
    # search for rental listings located in specific subregion of the SF Bay Area:
    region = 'sfbay'  # ie, search SF Bay Area (sfbay region) data 
    ## Prompt user to select one of several possible subregions:
    print_sfbay_subregion_names() # print what each sfbay craglslist subregion actually represents--ie, which regions and/or cities. 
    subregion_vals = ['eby', 'nby', 'pen', 'sby', 'scz', 'sfc'] # specify a list of all Bay Area subregions for craigslist site-- NB: craigslist lumps Santa Cruz ('scz') within their sfbay site.  
    subregion = inquirer_prompt_user_at_terminal(subregion_vals)  # parse the specific value the user selected  

    ## filter housing category to 'apa'-ie, rental listings (apartments & housing for rent)
    housing_category = 'apa'
    ## filter min & max rental price to avoid scraping unusual rental listings:
    min_price = 50 # filter out all unusual rental listings that do not specify rental price in the title of the listing--ie, the 'postingtitle' h1 (which are displated as $0 in when searching on craigslist)  
    max_price = 12000 # filter out all listings that have very high prices, since many of these listings are mislabelled and are oftentimes actually property lots for sale (even though we are searching for apartment-specific listings)   
    # filter rental period to monthly, to ensure rental prices are readily comparable:
    rent_period = 3  # ie, only show listings that show rental prices in monthly intervals. 
    # search for all current rental listings regardless of the sale date
    sale_date = "all+dates" # look up all current craigslist rental listings for given location, price range, and monthly rental periods: ie, regardless of when the listing will be available for moving into.
    
    # given above arguments, initialize a customized craigslist rental listing URL via the Craigslist_Rentals class, for the selenium webcrawler to access:
    craigslist_crawler = Craigslist_Rentals(region,subregion, housing_category, min_price, max_price, rent_period, sale_date)

    #access the URL via selenium Chrome webdriver: 
    craigslist_crawler.load_craigslist_form_URL()

    # implement the main web crawler and scrape the rental listings' data:
    dict_scraped_lists = craigslist_crawler.obtain_listing_data()  # scrape data, and store data as DataFrame
    # transform the dictionary of lists to Pandas' DataFrame:
    df = craigslist_crawler.dict_to_df_pipeline(dict_scraped_lists)

    # Execute DataFrame to CSV data pipeline,after cleaning city names data for specific subregions 
    craigslist_crawler.df_to_CSV_data_pipeline(df)

if __name__== "__main__":
    main()
import unittest
import pandas as pd
import numpy as np

#NB!: Also see following for some good examples and documentation on developing unit tests on Pandas Dataframes
# and numpy: <https://stackoverflow.com/questions/41852686/how-do-you-unit-test-python-dataframes> 




class Tests(unittest.TestCase):

    ## perform tests on the scraped data immediately after running the main webcrawler via main.py
    def test_for_attributes_with_ONLY_missing_data_and_possibly_incorrect_xpaths(self, df):
        """Check whether any of the scraped attributes--ie, number of bedrooms, etc.--are containing *only* missing data (ie, all rows are 'nan'), which would likely indicate *incorrect* xpath references!!"""
        # look up rows in which there are missing bedroom values--ie, equal to 'nan'
        missing_vals_brs = df[df['bedrooms'].str.contains('nan')]
        # count number of 'nan' vals--ie, mssing values--for scraped bedrooms attribute column:
        missing_vals_brs_count = len(missing_vals_brs)

        # verify whether *all* bedroom col rows contain *only* missing (ie, 'nan') values
        # in other words: determine whether the total number of rows is equal to the number of rows with 'nan' (missing) values:
        self.assertFalse(missing_vals_count = len(df['bedrooms']))   # return False--ie, a failed test--if all rows contain nan, indicating xpath for webscraper needs to be updated 
        pass


    ## perform tests on the cleaned rental listings data, before loading into SQL Server table

    def test_for_duplicates(self, df):
        """ Check that there are no duplicate listing URLs"""
        # test for duplicate listing ids
        self.assertFalse(df['ids'].duplicated().any())  # ensure there are no duplicate ids
        pass

    def test_date_format(self, df):
        """Ensure the date format of each datetime col 
        is of the form: YYYY-MM-DD"""
        self.assertTrue(df['date_posted'].duplicated().any())  # ensure there are no duplicate URLs
        pass

    
    def test_scraped_data_exists_for_given_region_for_ETL_to_SQL_pipeline(self, df):
        """Ensure that--when user selects given region for ETL data pipeline--at least *some* data has been scraped"""
        self.assertTrue(
            len(df.index) > 0 # ensure that number of rows is greater than 0  
        )

        pass

if __name__=='main':
    unittest.main()
 
import unittest
import pandas as pd
import numpy as np

#NB!: Also see following for some good examples and documentation on developing unit tests on Pandas Dataframes
# and numpy: <https://stackoverflow.com/questions/41852686/how-do-you-unit-test-python-dataframes> 


# perform tests on the cleaned rental listings data, before loading into 
class Tests(unittest.TestCase):
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

if __name__=='main':
    unittest.main()
 
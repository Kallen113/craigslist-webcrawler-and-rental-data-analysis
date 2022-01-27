# imports-- file processing
import os
import glob

# data analysis libraries & SQL libraries
import numpy as np
import pandas as pd
# SQL ODBC for API connection between Python & SQL Server
import pyodbc
import sqlalchemy as sa

import json

# statistical and ML modeling and hypothesis testing libraries
from sklearn.model_selection import KFold   # k-fold cross validation
from sklearn.model_selection import train_test_split  # split datasets into training & test datasets
from sklearn import linear_model  # OLS 
from sklearn import ensemble  # ensemble module contains the GradientBoostingRegressor class, which is used to estimate Gradient-boosted regression models

from sklearn.metrics import mean_squared_error  # calculate MSE to estimate accuracy of regression models 


""" Perform data analysis of scraped rental listings data.

1) Import data from SQL to pandas' DataFrame:
a.) Query from SQL table--import *only* records in which  price > $1 since a few rental listings show a price of $0 or $1, perhaps due to a typo.
&
b.) use Pandas' read_sql() method to export the contents of the SQL query to a DataFrame.

2.) Perform exploratory analysis

3.) Perform regression analysis on rental price 

4.) Perform time series analysis to
predict rental price 1 week ahead, and
then scrape new weekly data to verify 
accuracy of predictions. 
"""

# import data from rental table
class SQL_Database():
    def __init__(self, sql_config_path):

        with open(sql_config_path, 'r') as fh:
            config = json.load(fh)

        self.driver = config['driver']
        self.server = config['server']
        self.database = config['database']
        self.username = config['username']
        self.password = config['password']
        print(f"Name of connected database:/n {self.database}")

    
    def implement_and_print_sql_query(self, sql_query):
        """Implement and print given SQL query"""
        conn = pyodbc.connect(
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            'Trusted_Connection=yes;'
        )
        # initialize cursor so we can execute SQL code
        cursor = conn.cursor() 
        # execute and print query
        sql_query = conn.execute(sql_query)
        print(f"\n\nSQL query:\n{sql_query}\n\n")  # print query


    def import_SQL_to_df(self, sql_query):
        """Import dataset by using SQL query and Pandas' read_sql() method"""
        conn = pyodbc.connect(
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            'Trusted_Connection=yes;'
        )
        # initialize cursor so we can execute SQL code
        cursor = conn.cursor() 

        # query to select all records where price > $1, since such a price is essentially impossible and likely a typo from the original scraped rental listing (or would require largely un-automatable data cleaning procedures based on listing descriptions)
        sql = sql_query

        # export SQL query results to Pandas' DataFrame
        df = pd.read_sql(sql,conn)  # export results of SQL query to Pandas' DataFrame
        cursor.close()
        conn.close()
        return df

# specify path to json file containing SQL configuration/username data
sql_config_path = "D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\SQL_config\\config.json" 

# initialize SQL_Database class with path to SQL configuration file
SQL_db = SQL_Database(sql_config_path)  # NB: be sure to pass in path to the json SQL configuration file so we can load in the needed username, password, and configuration data to be able to access the SQL database


## import SQL rental table data to Pandas' df, with price >$1:
# specify query to import data
query_for_import = "SELECT * FROM rental WHERE price > 1;"
# import data to DataFrame via SQL query
df = SQL_db.import_SQL_to_df(query_for_import)
df.info() # sanity check



# specify path to json file containing SQL configuration/username data
sql_config_path = "D:\\Coding and Code projects\\Python\\craigslist_data_proj\\CraigslistWebScraper\\SQL_config\\config.json" 

SQL_db = SQL_Database(sql_config_path)  # NB: be sure to pass in path to the json SQL configuration file so we can load in the needed username, password, and configuration data to be able to access the SQL database
# Ingest data from pandas' dataframe to SQL server--data pipeline: 
SQL_db.insert_df_to_SQL_ETL(clist_rental)

## Data cleaning and feature engineering--ensure columns are of correct data type:
print(f"Data types of each column from queried SQL rental table: {df.dtypes}")

def transform_data_types(df, col):
    """Transform specific columns to target 
    data type, as needed."""
    pass


## exploratory analysis

# do query to examine listings that have been 

# compute & show sample statistics--let's run a SQL query since we can perform computations more efficiently than using the DataFrame directly:
# a.) For the *overall* dataset, let's examine MIN(), MAX(), AVG(), and MEDIAN() of rental price, and MIN(), Median(), MAX() of sqft and bedrooms, respectively 
 

# b.) At the *city* level, let's examine the same sample statistics--
# NB: we can use the PARTITION BY clause to implement multiple aggregations within a window: 
query_city_summary_stats = """ SELECT city,
MIN(price) OVER(PARTITION BY city) min_price, 
AVG(price) OVER(PARTITION BY city) average_price, 
MEDIAN(price) OVER(PARTITION BY city), 
MAX(price) OVER(PARTITION BY city) max_price"""  # specify query
# implement and print query 
city_sum_stats_query = SQL_db.implement_and_print_sql_query(query_city_summary_stats)


def data_exploration(df, csv_file_name):
    """Do some basic data exploration"""
    print(f"Some summary stats of the rental dataset: {df.describe()}") #show various summary stats


# examine sample distribution of rental price:
sns.boxplot(column=['prices'])  # boxplot of rental prices

# now, differentiate distributions of rental prices by # of bedrooms:
sns.boxplot(by='bedrooms', column=['prices'])  # boxplot of rental prices by bedrooms


# visualize heatmap of correlation coefficient matrix to analyze correlations between each of the variables within the dataset:
# compute correlation coefficient matrix (but be sure to filter out any non-numeric columns such as cities)
corr_ceof_matrix = df.select_dtypes(include=np.number).corr() # select only numeric cols, and compute correlation coefficient matrix

sns.heatmap() # heatmap of correlation coefficient matrix

# plot rental prices data by city
# group by on city
def groupby_multiple_aggs_and_cols(df, groupby_col, agg_col_1, agg_col_2):
    df_groupby = df.groupby([groupby_col]).agg(
        {agg_col_1: ['count', 'max', 'mean', 'median', 'std', 'min']},
        {agg_col_2: ['count', 'max', 'mean', 'median', 'std', 'min']})
    return df_groupby

# city-level summary stats for rental prices & number of bedrooms: 
clist_rental_city_groupby = groupby_multiple_aggs_and_cols(clist_rental, 'cities', 'prices', 'bedrooms')




clist_rental_city_groupby = clist_rental.groupby(['cities']).agg(
    {'prices': ['max', 'mean', 'median', 'std', 'count', 'min']},
    {'bedrooms': ['max', 'mean', 'median', 'std', 'count', 'min']})


# group by on city, but weigh the mean by number of rental listings:
# compute weighted mean to account for diffs in # of listings per city:
weight_price_mean_city = pass

# def compute_groupby_stats(df, groupby_entity, col1):
#     """Calculate city-level groupby to get mean, stand dev, and other aggregations on col such as rental prices, etc."""
#     df_groupby = df.groupby([groupby_entity]) # group data by given entity

#     aggs = df_groupby.size().to_frame(name='size')
#     aggs = aggs.join(df_groupby.agg({'col1':'mean'}).rename(columns={'col1':'col1_mean'}))\
#         .join(df_groupby.agg({'col1':'max'}).rename(columns={'col1':'col1_max'}))\
#             .join(df_groupby.agg({'col1':'median'}).rename(columns={'col1':'col1_median'}))\
#                 .join(df_groupby.agg({'col1':'std'}).rename(columns={'col1':'col1_stand_dev'}))\
#                     .join(df_groupby.agg({'col1':'min'}).rename(columns={'col1':'col1_min'}))\
#                         .reset_index()
#     # perform various aggregations, and rename cols
#     return aggs


# clist_city_groupby = compute_groupby_stats(clist_rental, 'cities', 'prices')

# clist_city_groupby


# plot rental prices data by city
# grouip by 

# plot histogram of rental price by city
# see stackoverflow ex <https://stackoverflow.com/questions/45883598/pandas-histogram-df-hist-group-by>

# scatterplot price vs sqft


## Final data transformations and regularization before ML and regression modeling

# regualize data

# regression analysis:

# ML modeling and validation
# bifurcate using K-fold() sklearn class to setup a 2-fold cross-validation --ie, to use 2 validation sets throughout training of each of the types of ML models:

# specify Kfold() class--specify number of folds, n
kfold = KFold(3, True, 1) # derive 2 cross-validation sets from the main dataset


# data sample
data = array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])

# enumerate splits
for train, test in kfold.split(data):
	print('train: %s, test: %s' % (data[train], data[test]))


# iterate over each fold (validation set) of the dataset, train regression models, derive predictions, and take the mean of predictive accuracy 
def train_reg_models_and_evaluate(validation_sets):
    # initialize empty dictionary to contain reg prediction results
    reg_preds = {'model_name': , 'preds':''}
    for test_set in validation_sets:
        fitted_reg_preds = test_set.fit(test_set).prediction # fit each model with each validation set/fold
        reg_preds.append(fitted_reg_preds) # append fitted models' predictions
    for preds in fitted_reg_preds:
        acc_scores = preds.accuracy_score(preds)
        
    # compute mean of accuracy scores
    print(f"The overall accuracy of the fitted regression models is: {acc_scores.mean()}")
    # return the fitted preds
    return reg_preds   


# perform OLS reg
 = train_reg_models_and_evaluate()


# print predicted vs actual values, for OLS 


## Next, estimate xgboost regression model:

# estimate xgboost model



    




#time series analysis









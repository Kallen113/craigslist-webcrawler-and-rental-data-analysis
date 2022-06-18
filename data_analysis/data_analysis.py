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
import statsmodels.formula.api as smf  # OLS module using R-like OLS formula syntax-- e.g., formula = "y ~ var1 + var2"

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

        # query to select all records where price > $100, since such a price is essentially impossible and possibly a typo from the original scraped rental listing or would require largely un-automatable data cleaning procedures based on idiosyncratic price data specified in the listing descriptions
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


## import SQL rental table data to Pandas' df, with price >$100, and select *only*  SF Bay data:
# specify query to import data
query_for_import = "SELECT * FROM rental WHERE price > 100 AND region = 'sfbay';"
# import data to DataFrame via SQL query
df = SQL_db.import_SQL_to_df(query_for_import)
print(f"Rental data imported from SQL table:\n{df.info()}") # sanity check


## Data cleaning and feature engineering--ensure columns are of correct data type:

# Remove any null rows (*few, if any, should be present in SQL table due to the earlier CSV to SQL  Server data pipeline & data cleaning steps)
def remove_null_rows(df):
    return df.dropna(axis=0, how='any')  # drop any rows with nulls

df = remove_null_rows(df)

print(f"Data types of each column from queried SQL rental table:\n{df.dtypes}")

def transform_data_types(df, col):
    """Transform specific columns to target data type, as needed."""
    pass

# # transform data types
# df = transform_data_types(df)

## exploratory analysis

# basic summary stats of overall dataset


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
#show heatmap plot of correlation (sort of a heatmap of a correlation matrix)
#calculate the correlations of each variable to price
def corr_heatmap(df, outcome_var):
    # for purposes of finding correlations with price, create a new Index object and convert to list with all numeric (int64 & float) columns from the  dataframe
    # we will exclude all indicator variables (ie, data type of 'uint8') since some have so many groups
    numeric_RHS = df.select_dtypes(include=['int64','float64']).columns  #exclude indicator variables
    #drop the outcome var from this df since we should only include RHS variables for this
    numeric_RHS = numeric_RHS.drop([outcome_var]) 
    #also, convert numeric_RHS to list:
    numeric_RHS_lis  = list(numeric_RHS)
    #calculate correlation of each RHS column with respect to the dependent variable
    corr = df[[outcome_var] + numeric_RHS_lis].corr()
    #Initialize the heatmap plot
    f, ax = plt.subplots(figsize=(40,24))
    #Create a mask to generate an upper triangular shape
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    #Set up a color map with a diverging palette of 3 colors
    cmap= sns.diverging_palette(220,10, as_cmap = True)
    #Notice the plot has a triangular shape, and the levels and intensity of positive and negative correlations are shown with 2 diverging colors.
    sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0, square=True, linewidths=.5, cbar_kws ={"shrink": .5})

#heatmap of correlation coefficient matrix:
corr_heatmap(df, 'price') #NB: For this heatmap, note that a darker red color conveys higher positive correlation, white indicates no correlation, and blue indicates higher negative correlation)


corr_coef_matrix = df.select_dtypes(include=np.number).corr() # select only numeric cols, and compute correlation coefficient matrix

sns.heatmap() # heatmap of correlation coefficient matrix


## Time series & testing for autocorrelation:

## Since we have a panel dataset with a fairly large number of time periods T, we should evaluate whether autocorrelation is present in the dataset

import statsmodels.api as sm

# create new df as an explicity time series
def transform_to_time_series(df, time_series_col):
    df_ts = df.set_index(time_series_col)
    return df_ts

# dataset as time series
df_ts = transform_to_time_series(df, 'date_posted')

# show auto & partial auto correlation plots:
def auto_corr_plot(df_ts, col):
    sm.graphics.tsa.plot_acf(df_ts[col], lags=40)
    plt.show()

# show  autocorrelation (ACF) plot wrt rental prices over time
auto_corr_plot(df_ts, 'price')


# perform Durbin-Watson test to more rigorously identify or reject autocorrelation


## Next, examine whether prices differ significantly by Bay Area sub region or city:

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


## Final data transformations and 

## col transformations:

# convert several categorical-like oibject cols to indicators: 
def transform_to_indicator_vars(df, col_to_transform):
    indicator_vars = pd.get_dummies(df[col_to_transform], \
        drop_first:True, sparsebool:True )  # return dummies in a sparse array format
    # concatenate indicator_vars  to original df:
    df = pd.concat([df,indicator_vars],axis=1).head()
    df = df.drop(cols=[col_to_transform])   # remove original col
    return df


# cities col to indicators
df = transform_to_indicator_vars(df, "cities")

#sub_region to dummies
df = transform_to_indicator_vars(df, "sub_region")


## regularization and bifurcate dataset into kfold train & validation datasets before ML and regression modeling

# regularize data
def regularize_data(df):
    pass

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


# define outcome var & RHS covariates:
def obtain_LHS_and_RHS_vars(df, outcome_var, non_RHS_cols_list ):
    """After splitting dataset into training & test data, obtain outcome var & RHS covariates for each"""
    LHS = df[outcome_var]  # specify outcome var
    non_RHS_cols_list = non_RHS_cols_list  # we will drop these cols to obtain *just* the RHS cols 
    RHS = df[df.drop(columns=non_RHS_cols_list)]  # drop any non-RHS cols


## specify outcome var name
outcome_var = "price"



## Remove cols that we will *not* use for regression analysis:

# specify cols we will *not* use in the ression models:
non_OLS_cols = ["ids", "listing_descrip", "attr_vars"] 

# remove these cols from dataset
def remove_non_OLS_cols(df, list_of_non_OLS_cols):
    return df.drop(columns=[list_of_non_OLS_cols])

df = remove_non_OLS_cols(df, non_OLS_cols)

## Specify RHS col names
def return_RHS_col_names(df, outcome_var):
    """Return a list of each of the covariate column names (*supply this list of RHS cols to the OLS function)"""
    return df.drop(columns=[outcome_var]).to_list()   # NB!: we assume that we want *all* variables from the dataset aside from the outcome variable


RHS = return_RHS_col_names(df, outcome_var)




# ##  run OLS regression, and show output of model via statsmodels library
## fit OLS model (*with robust standard errors to deal w/ heteroskedasticity) and print output
def fit_OLS_robust_SE(df, outcome_var, *categoric_vars):
    # compute total number of all RHS variables   
    num_cols = df.drop(columns=[outcome_var]).shape[1]   # obtain number of  RHS cols
    # get a list of all RHS covariates *excluding* categorical variables 
    RHS_vars_sans_categorical = df.drop(columns=[outcome_var, categoric_vars]) 
    # Estimate OLS model using R-like OLS formula syntax
    OLS_model =  smf.OLS(
        formula= f'{outcome_var} ~ {" + ".join(str(el) for el in RHS_vars_sans_categorical)} + C({categoric_vars})', 
        data =df
        )   # NB: intercept term is automatically included by this smf.ols statsmodels module (unlike for sm.OLS)
    # Fit OLS model using HC3 robust standard errors: 
    reg_res = OLS_model.fit(cov_type='HC3')   #fit the OLS regression model with hetereoskedastic-robust standard errors (ie, HC3), and thereby derive the parameter estimates
    # use cov_type='HC3' to estimate standard errors that are robust to heteroskedastic (ie, non-constant) variance, to estimate more accurate standard errors. 
    print(f"Number of covariates (ie, regressor columns):\n {num_cols}.\n\nThis OLS model specification has the following columns:\n{RHS_vars_sans_categorical.columns, categ_var1, categ_var2}.\n\n\nThe regression model's results are as follows:\n{reg_res.summary()}")   #  print regression results  
    return reg_res  # return fitted model results so we can store it 



categorical_vars = ("city", "sub_region")



 = fit_OLS_robust_SE(df, )


# def fit_OLS_model_sm_robust_stand_errors(df, RHS_vars, outcome_var):
#     # obtain data for outcome variable (ie, from df dataset)
#     y = df[outcome_var]   # obtain outcome var data
#     # obtain data for RHS variables 
#     X = df[RHS_vars]   # RHS col data
#     X = sm.add_constant(X) #add intercept term to model  
#     num_cols = X.shape[1] # get number of cols from RHS data
#     # Estimate OLS model
#     OLS_model = sm.OLS(exog=X, endog=y)   
#     # Fit OLS model using HC3 robust standard errors: 
#     reg_res = OLS_model.fit(cov_type='HC3')   #fit the OLS regression model with hetereoskedastic-robust standard errors (ie, HC3), and thereby derive the parameter estimates
#     # use cov_type='HC3' to estimate standard errors that are robust to heteroskedastic (ie, non-constant) variance, to estimate more accurate standard errors. 
#     print(f"Number of covariates (ie, regressor columns):\n {num_cols}.\n\nThis OLS model specification has the following columns:\n{RHS_vars.columns}.\n\n\nThe regression model's results are as follows:\n{reg_res.summary()}")   #  print regression results  
#     return reg_res  # return fitted model results so we can store it 

## train and fit OLS with ALL available RHS columns:
# Thus, use X_train with no additional wrangling:
#linear OLS specification:
OLS_all_RHS_linear = fit_OLS_model_sm_robust_stand_errors(X_train, Y_train)


## NB: show regression output *only* for non-indicator variables:
def print_reg_output_non_indicators_only():
    all_regressors = sorted(list(set(res1.exog_names) | set(res2.exog_names)))
    # Drop the dummies using some logic on their names.
    all_regressors_no_fe = [var_name for var_name in all_regressors if not var_name.startswith('C(')]

    print (summary_col([res,res2],stars=True,float_format='%0.3f',
                    model_names=['one\n(0)','two\n(1)'],
                    info_dict={'N':lambda x: "{0:d}".format(int(x.nobs)),
                                'R2':lambda x: "{:.2f}".format(x.rsquared)},
                    regressor_order=all_regressors_no_fe,
                    drop_omitted=True))


from statsmodels.tools.eval_measures import rmse

###  derive a prediction from the OLS model using the validation (ie, X_test, Y_test) data
## then, calculate RMSE -ie, root mean squared error--to estimate how accurate the OLS model's predictions are
def derive_prediction_and_calc_RMSE(trained_OLS, X_test_data,  Y_test_data):
    X_test_data = sm.add_constant(X_test_data)  # add intercept term to test data
    OLS_predictions = trained_OLS.predict(X_test_data)  # derive prediction based on test data, Y_test_dataset
    print(f"Trained OLS model predictions (from test dataset): \n {OLS_predictions} \n") 
    RMSE =  rmse(Y_test_data, OLS_predictions) # calculate RMSE elative to test data (ie, actual vs predicted via test data)
    return OLS_predictions, RMSE

#apply function to derive predictions using test data:
OLS_all_linear_preds, OLS_all_linear_RMSE = derive_prediction_and_calc_RMSE(OLS_all_RHS_linear, X_test, Y_test)

#print RMSE:
print(f"RMSE of Trained OLS model: \n {OLS_all_linear_RMSE}") 



# Now, let's take some ML approaches and fit different regression models:

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









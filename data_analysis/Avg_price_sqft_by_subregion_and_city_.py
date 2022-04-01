## Part 3 of analysis

## import data

from itertools import groupby


df = ...

## Develop a standardized measure (a KPI if you will) in which we can compare cities and subregions by rental prices, but account for differences in rental home/property size:

### Ie: calculate price per sq feet
df['price_per_sqft'] = df.price/df.sqft

## distribution (boxplot) of price per sqft by subregion hue


## group data by mean of price per sqft by subregion

## barchart of ppsqft by subregion




### NB: filter the data to a 'restricted' dataset
### in which we *remove* cities that have rental listings data 
### on fewer than 60  days.
### This way, we will include only cities that have listings on at least 1/3
### of the total time period of the sample we're using--ie, Oct 2021-March 2022.

### Why restrict the dataset like this?
### B/c we can help curate a more *balanced* panel dataset,
### thereby reducing the bias of the panel regression results.

### In other words, by including all cities and all subregions,
### as in Part 1 and Part 2, the results of the panel regression
### model were biased since the panel dataset was heavily imbalanced.
### Large cities such as SF, Oakland, and San Jose would likely be 
### heavily , biasing the rental data to be more heavily impacted
### by these cities, and making less accurate predictions
### of smaller cities with less frequent data, such as Sebastopol or Boulder Creek.
 

### then perform regression analysis on the restricted dataset 



## filter data

#  get len() of groupby on city & day of date_posted
df['city_by_day_counts'] = df.groupby([df['date_posted'].dt.day, 'city']).transform('size')


# # concat results back to original dataset
#  = .map()

## Filter data if city by day counts > 60:
def filter_data_by_city_day_counts(df, col_for_filter):
    return df.loc[df[col_for_filter]>60]  

 = filter_data_by_city_day_counts(df, 'city_by_day_counts')
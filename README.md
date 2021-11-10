# craigslist-webcrawler
## Python selenium webcrawler of craigslist: 

Python web crawler of craigslist using selenium library to scrape criagslist rental listings data, and a Python Pandas and SQL Server ETL of scraped data. 


### Caveats and Bugs:

While the data that the selenium webcrawler is scraping are accurate and complete for almost every variable, some of the records do not line up with 2 columns: namely, the 1) listing_urls & 2) the listing ids. I could not pinpoint any specific cause of this sort of "bug" in the webcrawler script. However, this is not an especially prompinent shortcoming or flaw. Ultimately, the listing URLs are only useful for enabling the webcrawler script to reference the listings and scrape the data. As for the listing_id, the only important aspect to this column for a webscraping and especially data analysis project is that the listing ids are each unique. NB: in short, given that the rest of the data lines up properly for each record nad have been scraped, it does not really matter once the webcrawler has been implemented. In addition, all of the other 44 of the 46 columns are accurate and line up properly to each record. Nevertheless, this is a bit of a caveat and bug to take note.  


"""This script will parse the names of the subregions within a
given craiglist region (ie, sfbay, chicago, new york, etc.).

NB: We need to a priori know the URL to the craigslist homepage
of the given region. 
For ex: <https://newyork.craigslist.org/> is the homepage for craglist new york city."""

def parse_subregion_via_xpath(craigslist_url_homepage, xpath_arg, list_to_append: list):
    """ Scrape data from HTML element by looking up xpath (via selenium find_elements_by_xpath() method).
    a.) Wait until given HTML element has loaded on page using WebDriverWait() method.
    b.) Then, scrape the HTML element and extract the element's text data, and append to list."""
    # access craigslist homepage for given region:
    craigslist_homepage_selenium = web_driver.get(craigslist_url_homepage) # do get request to access the homepage of the given craiglist region
    # a.) wait until given HTML element has loaded
    wait_until = WebDriverWait(craigslist_homepage_selenium, 10)  # wait up to 15 seconds to let HTML element load on given rental listing webpage
    wait_until.until(EC.presence_of_element_located((By.XPATH, xpath_arg))) # a.) wait until given HTML element has loaded, or up to 15 seconds
    # b.) scrape the HTML element, extract text, and append to given list
    for scraped_html in self.web_driver.find_elements_by_xpath(xpath_arg):
        list_to_append.append(scraped_html.text)  # parse text data from scraped html element


# initialize empty list to contain the names of subregions
craigslist_subregions = []

# specify xpath argument  
ul_subregions = find_xpath('//*[@id="topban"]/div[1]/ul') 

# iterate over each li element in this ul element
for li in ul_subregions:
    # then, parse the text from the href element of each a and href element within the li's 
    li.text 

    # sanity check
    print(f'{li.text}')



def main():
    # NB: look up subregions for craigslist San Diego:
    SD_homepage = 'https://sandiego.craigslist.org/'

    parse_subregion_via_xpath(SD_homepage, ul_subregions, craigslist_subregions)


if __name__=="__main__":
    main()
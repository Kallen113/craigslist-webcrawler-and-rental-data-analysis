# activate virtual env for craigslist webcrawler project:
activate () {
  . ../.craigslist_venv/bin/activate
}
# alias activate= ". ../.craigslist_venv/bin/activate" 
# run the webcrawler script (main.py) as a Python module
python3 -m "main"
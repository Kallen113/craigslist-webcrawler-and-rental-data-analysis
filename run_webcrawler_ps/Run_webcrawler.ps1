# specify webcrawler program's root path
cd  "D:\Coding and Code projects\Python\craigslist_data_proj\CraigslistWebScraper>"

# activate Python virtual env (corresponding to webcrawler project)
craigslist_venv\Scripts\activate.ps1

$path =  "D:\Coding and Code projects\Python\craigslist_data_proj\CraigslistWebScraper>"

# specify file name of main webcrawler script
$filename = "main.py"

# specify full path and Python file name
$PythonExecutable = $path + $filename

# run webcrawler program by exuecting main.py as a Python module
pyton - m $PythonExecutable
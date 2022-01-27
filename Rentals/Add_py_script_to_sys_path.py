import os
import sys
from pathlib import Path

## NB: If a ModuleNotFoundError occurs when we run the webcrawler
# then we need to add these 2 scripts to the Python sys path to ensure they are imported properly:

# obtain script's parent directory and add to sys.path using Path() and .parents[1] method from pathlib library:
def parse_parent_direc_and_add_to_sys_path(py_script_to_check):
    """Obtain this script's parent directory as a str, 
    and add the parent direc to the Python sys path if it does not (yet) exist."""
    current_script_dir = str(Path(py_script_to_check).resolve().parents[0])  # get a string version of the parent directory (ie, 1 directory up from script) of this script
    # add path to parent directory to our Python's system path so we can import script from this parent direc
    if current_script_dir not in sys.path: ## NB: do NOT add direc to sys.path if it already exists
        sys.path.insert(0, current_script_dir)  # insert given direc, if not exists
    print("The paths in our Python sys path are:\n")  # sanity check on Python sys path--ensure parent direc has been added
    for p in sys.path:
        print(f"{p}\n")

## Examples:
# parse_parent_direc_and_add_to_sys_path('clean_city_names.py')
# parse_parent_direc_and_add_to_sys_path('clean_santa_cruz_data.py')
## add parent directory of this script to python sys.path:
#  parse_parent_direc_and_add_to_sys_path('selenium_webcrawler.py')

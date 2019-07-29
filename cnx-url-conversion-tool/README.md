# Url Conversion Tool
## Description
  The url conversion tool allows for easy conversion from any of the three formats we have for module and collection IDs to the other two formats. The tool is a python 2.7 script that runs on command line.

## Before Using the Tool
  This script uses the libraries Requests and Openpyxl.
  Check which version of Python is your default by running `python --version`
  The URL COnversion Tool uses Python version 2.7.X. If you have Python 3.X as your default, use the alternate pip2 commands below.
  
  Before using the tool, run the following two lines on the command line.

  `pip install requests`
  
  `pip install openpyxl==2.5.0`

  If Python 3.X is your default python, run this instead

  `pip2 install requests`

  `pip2 install openpyxl==2.5.0`

  If you get "Successfully installed requests-2.10.0" and "Successfully installed et-xmlfile-1.0.1 jdcal-1.2 openpyxl-2.3.5" or something along those lines, you're good to go.

  If you get "error: [Errno 13] Permission denied: ... ," then try running the command in sudo, i.e. `sudo pip install  openpyxl`.


  If you get "-bash: pip: command not found," then you need to install pip first.
  Pip is a preffered installer program for python.
  On a mac, you can install it by typing the command `sudo easy_install pip`.
  If you're on windows, you can follow the directions to install it [here](https://pip.pypa.io/en/stable/installing/).

  After installing pip, run the two pip install commands above again, and they should be installed successfully.

## Uses
  - Convert many module IDs at once to the other formats.
  - Convert a collection ID to other formats.
  - Convert a collection ID, and also get all of the IDs of the modules in that collection in all three formats.

## Inputs
  The module IDs can come from an excel sheet (with .xlsx extention) or the command line.

  Note that the excel sheet must be in the same directory as the conversion tool. The column names must be the first row in the spreadsheet.

## Outputs
  The output can be shown in command line or exported as a csv or an excel sheet.

## Directions
  Download the tool by going to https://github.com/Rhaptos/cnx-tools and clicking on "clone or download."
  From there, click on "download zip." This will download all of the tools included in this repository, so you might have to delete the tools you don't need.
  Run the script by typing `python conversion-tool.py` and then follow the prompts.

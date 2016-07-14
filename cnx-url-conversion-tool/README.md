# Url Conversion Tool
## Description
  The url conversion tool allows for easy conversion from any of the three formats we have for module and collection IDs to the other two formats. The tool is a python 2.7 script that runs on command line. 
  
## Before Using the Tool
  Make sure to install Requests and Openpyxl before running the script.
  
  `pip install requests`
  
  `pip isntall openpyxl`

## Uses
  - Convert many module IDs at once to the other formats.
  - Convert a collection ID to other formats.
  - Convert a collection ID, and also get all of the IDs of the modules in that collection in all three formats.

## Inputs
  The module IDs can come from an excel sheet (with .xlsx extention) or the command line. 
  
  Note that the excel sheet must be in the same directory as the conversion tool.

## Outputs
  The output can be shown in command line or exported as a csv or an excel sheet. 
  
## Directions
  Run the script by typing `python conversion-tool.py` and then follow the prompts.

# xpath-book-search

## Description

Searches for the existence of a given xpath across all modules on a server.
Returns a table of book titles, book uuids, module uuids where the instance was found, and the authors of that module.

## Setup

Clone the repo to your local machine, cd into the directory, and make the script executable.

`git clone https://github.com/caderitter/xpath-book-search`

`cd xpath-book-search`

`sudo chmod +X search_db_xpath.sh`

This script requires some custom SQL functions to be created in the database. If they haven't been created yet, run the script as follows: 

`./search_db_xpath.sh setup [user] [server]`

Soon, the scripts will be merged into `cnx-db`, so the above will not be necessary.

## Usage

In a terminal window, enter the following command:

`./search_db_xpath.sh [user] [server] ["xpath"] [filename] [output-file]`

The arguments are as follows:

* `[user]` - your username on the server

* `[server]` - the server to SSH to (qa, dev, tea... whichever string comes before `.cnx.org`)

* `["xpath"]` - a double-quote-wrapped valid xpath. All interior quotes must be single quotes and must be escaped with backslashes (as in `"//*[local-name()=\'definition\']"`)

* `[filename]` - the filename to search in each module (`index.cnxml`, `index.cnxml.html`...)

* `[output-file]` - the output file name, i.e. `results.csv`

This will SSH in to the specified server, prompt you for your password, and execute the search. If you end the script for whatever reason, the search query *will not end with it.* Wait until the process is finished before trying again. Use the `top` or `ps x` commands to see if the `postgres` process is done.

After the search is done, you will be prompted for your server password again to `scp` the output file to your local machine. The file will be available in the directory the script was run from.

## Examples

Documentation for xpath is available online through many tutorials and specifications. 

* Search for all definitions in CNXML.

	`./search_db_xpath.sh cade qa "//*[local-name()=\'definition\']" index.cnxml results.csv`

* Search for all unnumbered figures in CNXML.

	`./search_db_xpath.sh cade qa "//*[local-name()=\'figure\' and @class=\'unnumbered\']" index.cnxml results.csv`

* Search for all tags that have a class of 'review-challenge' in CNXML.

	`./search_db_xpath.sh cade qa "//*[@class=\'review-challenge\']]" index.cnxml results.csv`

* Search for all lists in HTML not containing `ul` or `ol` elements.
	
	`./search_db_xpath.sh cade qa "//*[local-name()=\'div\' and @data-type=\'list\'][not(ul) and not(ol)]" index.cnxml.html results.csv`

## Issues

* Namespacing is currently not sorted out, so `//*[local-name()=\'example\']` must be used to select non-root elements.



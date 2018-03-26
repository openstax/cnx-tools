#!/bin/bash

if [ "$1" == "setup" ]; then
	if [ $# -ne 3 ]; then
		echo $0: usage: search_db_xpath setup [username] [servername]
	fi
username=$2
servername=$3

connectionstring=$username@$servername.cnx.org
echo "Copying SQL file to server..."
scp search_db_xpath.sql $connectionstring:~/. || exit 1
echo "...done."
echo "Creating functions on server..."
ssh $connectionstring <<EOSSH || exit 1
psql -U rhaptos -h /var/run/postgresql -d repository <<EOSQL
\i search_db_xpath.sql
\q
EOSQL
exit
EOSSH
echo "...done."
exit
fi


if [ $# -ne 5 ]; then
    echo $0: usage: search_db_xpath [username] [servername] [xpath] [filename] [output-filename]
    exit 1
fi

username=$1
servername=$2
xpath=$3
filename=$4
outputfile=$5

connectionstring=$username@$servername.cnx.org

echo "SSH to server..."
ssh $connectionstring <<EOSSH || exit 1
psql -U rhaptos -h /var/run/postgresql -d repository <<EOSQL
\o $outputfile;
SELECT * FROM search_db_xpath(e'$xpath', '$filename');
\q
EOSQL
echo "...done."
exit
EOSSH
echo "Copying file to this machine..."
scp $connectionstring:~/$outputfile .
echo "...done"





#!/bin/bash

if [ -z "$1" ]
then
      echo "No parameter given. Please indicate which database to copy"
      psql -l
      exit
fi
if [ -z "$2" ]
then
      echo "No target given. Please indicate what database name to copy to"
      exit
fi
DBNAME=$(basename $1)
DBNAME_BAK=$(basename $2)
DBUSER='robert'
#echo $DBNAME $DBNAME_BAK

echo "********************************************"
echo $(basename $0) "creates a local database backup from a local database"
echo "from:" $(basename $1) "to:" $(basename $2)
echo "from:" $basename $DBNAME "to:" $DBNAME_BAK
echo "********************************************"

# check if db exists
# wc -l count lines
EXISTS=$(psql -l | grep "$DBNAME "  -w | wc -l)
EXISTS_BAK=$(psql -l | grep "$DBNAME_BAK " -w | wc -l)
PLEASE_COPY=0

# drop existing database
# only do it, when there is a backup
if [ "$EXISTS" -gt 0 ]; then
    if [ "$EXISTS_BAK" -gt 0 ]; then
        dropdb $DBNAME_BAK
        if [ "$?" = "0" ]
        then
            echo "Droped $DBNAME_BAK successfully"
            # set flag to copy the database
            PLEASE_COPY=1
        else
            echo "Cannot drop $DBNAME_BAK"
        fi
    else
        echo "$DBNAME_BAK does not exist, so not dropped"
        # nevertheless set flag to copy the database
        PLEASE_COPY=1
    fi
    # do the copy
    if [ "$PLEASE_COPY" -gt 0 ]; then
        $(createdb -O $DBUSER -T $DBNAME $DBNAME_BAK)
    fi
    if [ "$?" = "0" ]; then
        echo "copied $DBNAME to $DBNAME_BAK"
    else
        echo "FAILED to copy $DBNAME to $DBNAME_BAK"
    fi
else
    echo $DBNAME "does not exist. Bailing out"
    exit 0
fi

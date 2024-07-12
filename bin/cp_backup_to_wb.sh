#!/bin/bash
# cp_backup_to_wb.sh is used to copy an odoo backup into a workbench strukture
if [ "$#" -ne  "2" ]
then
    echo "You need to provide a path to the data and the name of an existing site"
    echo "use cp_backup_to_wb.sh ARG1 ARG2 to copy data found at ARG1 to site ARG2"
    exit
fi
if  [ ! -f $1/dump.sql ]; then
    echo $1/dump.sql does not exist
    exit
elif  [ ! -d $1/filestore ]; then
    echo $1/filestore does not exist
    exit
elif  [ ! -d $2 ]; then
    echo $2 seems not to be a created site
    exit
fi
# now do the actual copy
# first mv old filestore out of the way
# but only if it does not exist from a former run
if  [ ! -d $2/filestore/$2_$(date +%F) ]; then
    mv $2/filestore/$2 $2/filestore/$2_$(date +%F)
fi
# it is not sure, that a a dump exist, so simulate a try catch
{ # try

    mv $2/dump/$2.dmp $2/dump/$2.dmp_$(date +%F)

} || { # catch
    echo $2/dump/$2.dmp not found
}
# do the copy
cp $1/dump.sql $2/dump/$2.dmp
rsync -a $1/filestore  $2/filestore/$2
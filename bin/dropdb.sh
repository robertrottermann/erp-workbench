#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
# ckeck wheter $1 ends in /
LAST="${1: -1}"
echo '...' $LAST, $1
P1=$1
if [ $LAST == '/' ]; then
    P1="${1::-1}"
fi
if [ $P1 ]; then
    if [ $P1 = '-h' ]
    then
        echo 'Drop database in db docker container'
        echo '-h for help'
        echo '-hh for help on dumper'
        echo '-l for list on databases in the docker container'
    elif [ $P1 = '-hh' ]
    then
        echo 'List help on dumper'
        docker run -v $DIR/:/mnt/sites --rm=true --link db:db -it dbdumper -h
    elif [ $P1 = '-l' ]
    then
        echo 'List existing databases in db container'
        docker run -v $DIR/:/mnt/sites --rm=true --link db:db -it dbdumper -ldb
    else
        echo "Drop database $P1 in db docker container"
        docker run -v $DIR/:/mnt/sites --rm=true --link db:db -it dbdumper -dd $@
    fi
else
    echo 'You must provide a database name to drop'
    echo '-h / -hh for help'
fi


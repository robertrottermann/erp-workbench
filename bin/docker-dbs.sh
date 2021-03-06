#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"

if [ $1 ]; then
    # ckeck whether $1 ends in /
    LAST="${1: -1}"
    P1=$1
    if [ $LAST == '/' ]; then
        P1="${1::-1}"
    fi
    if [ $P1 = '-h' ]
    then
        echo 'Drop database in from db docker container'
        echo '-h for help'
        echo '-hh for help on dumper'
        echo '-l for a list of databases from the docker container'
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
        docker stop $P1
        docker run -v $DIR/:/mnt/sites --rm=true --link db:db -it dbdumper -dd $@
    fi
else
    echo 'You must provide a database name to drop'
    echo '-h / -hh for help'
fi


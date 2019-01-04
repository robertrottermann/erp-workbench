#!/bin/bash
if [ $1 ]; then
    if [ $1 = '-h' ]
    then
        echo 'Drop database in db docker container'
        echo '-h for help'
        echo '-hh for help on dumper'
        echo '-l for list on databases in the docker container'
    elif [ $1 = '-hh' ]
    then
        echo 'List help on dumper'
        docker run -v $HOME/workbench/:/mnt/sites --rm=true --link db:db -it dbdumper -h
    elif [ $1 = '-l' ]
    then
        echo 'List existing databases in db container'
        docker run -v $HOME/workbench/:/mnt/sites --rm=true --link db:db -it dbdumper -ldb
    else
        echo 'Drop database in db docker container'
        docker run -v $HOME/workbench/:/mnt/sites --rm=true --link db:db -it dbdumper -dd $@
    fi
else
    echo 'You must provide a database name to drop'
    echo '-h / -hh for help'
fi


#/bin/bash
for x in $(ls -d */) ; do echo $x; (cd $x; git pull); done 
for x in $(ls -d */) ; do echo $x; (cd $x; git status); done 

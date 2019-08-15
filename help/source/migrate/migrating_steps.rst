-----------------------------
Steps to migrate an odoo site
-----------------------------


Backup database
---------------
::

    CREATE DATABASE newdb WITH TEMPLATE originaldb OWNER dbuser;

    # Still, you may get:

    # ERROR:  source database "originaldb" is being accessed by other users
    # To fix it you can use this query

    SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity 
    WHERE pg_stat_activity.datname = 'originaldb' AND pid <> pg_backend_pid();

Preparation
-----------

- make sure the target site environment has been created
    if not create it::
    
        bin/s --add-site target_site -V target-version 
        bin/c -c target_site
        # create a running target target odoo, without anything installed yet
        # in a new shell
        target_sitew # <- mind the w
        bin/build_odoo.py

        # make sure any errors like the following are fixed, so you COULD run your site
        # ERROR: Could not find a version that satisfies the requirement pdfconv (from -r install/requirements.txt (line 7)) (from # versions: none)
        #ERROR: No matching distribution found for pdfconv (from -r install/requirements.txt (line 7))

        # test your new, empty, nothing installed site
        bin/odoo
        


- install OpenUpgrade ::

    wb
    git clone https://github.com/OCA/OpenUpgrade.git
    cd OpenUpgrade
    python setup.py install


do migration
------------
You do the migration version by version:

like bin/s --upgrade actual+1 actual

Upgrade site to a new erp version. Please indicate the
name of the new site. The target version will be
read from its site description
::

    # make sure openmigrate is installed
    # then do the upgrade
    bin/s --upgrade redo2oo12 redo2oo11


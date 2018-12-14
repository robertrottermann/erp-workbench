Life-cycle of a site description
--------------------------------

create
******

::
        
    bin/s --add-site NEWSITE

or::
    
    bin/s --add-site-local NEWSITE

Build or update local project
*****************************

::

    bin/c -c NEWSITE

or just ubpdate modules::

    bin/c -m NEWSITE
 
or just ubpdate singel modules::

    bin/c -M moule1,module2 NEWSITE
 
Create local site
*****************

::

    NEWSITEw # command is name of the site with a w attached
    bin/build_odoo.py # to download odoo and build the site
    bin/odoo # to run the site

Delete local site-description but keep project
**********************************************

    bin/s --drop-site NEWSITE

Delete all project data but keep site-description
*************************************************

Delete the following:

    - files in ~/projects/NEWSITE
    - data-folder in ~/erp-workbench/NEWSITE
    - virtual environment for NEWSITE

::

    bin/c --DELETELOCAL
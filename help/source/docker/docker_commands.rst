----------------------------
Commands dealing with docker
----------------------------

Accessing site running in container
-----------------------------------

Install odoo-Apps
=================

    ::

        bin/d -dI SITENAME [-v]

Install OCA and own Apps&Modules
================================

    ::

        bin/d -dio [all][m1,m2,..] SITENAME [-v]


Update OCA and own Apps&Modules
===============================

    ::

        bin/d -duo [all][m1,m2,..] SITENAME [-v]

Dump site to file system
========================

    ::

        bin/d -ddump  SITENAME [-v]

Restore site from dump
======================

    ::

        # fetch the sites content from its life server and recreate it locally
        # -N if you just want reload the site from its local (to the container) data
        bin/d -dud [-N] SITENAME [-v]


Maintaining containers
----------------------

Create container
================

    ::

        bin/d -dc SITENAME [-v]

Recreate container
==================

    ::

        bin/d -dr SITENAME [-v]

Rename container
=================

    ::

        # the container is renamed with the actual date appended to the name
        # The container will then be recreated
        bin/d -dR SITENAME [-v]

Drop container
==============

    ::

        bin/d -dd SITENAME [-v]
        
Start container
===============

    ::

        bin/d -ds SITENAME [-v]

Stop container
==============

    ::

        bin/d -dS SITENAME [-v]
        
Inspect container
=================

    ::

        # only important info
        bin/d -dshow SITENAME [-v]
        # show all info
        bin/d -dshowa SITENAME [-v]


Maintaining images
------------------

Create Image
============

    ::

        bin/d -dbi SITENAME [-v]


Pull (refresh) Image
====================

    ::

        bin/d -dp SITENAME [-v]

Push (upload to docker hub) Image
=================================

    ::

        bin/d -dpi SITENAME [-v]



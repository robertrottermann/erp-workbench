-------------------------------------
A quick walk trough the erp-workbench
-------------------------------------

erp-workbench lets you create erp-sites locally and remotely with ease. It tries to blur the distinction of a site running locally or in a remote docker context.

In this walktrough you learn: 

- Explanation of terms used
- Define what type of erp you handle
- Change editor to use
- How to define/edit a remote server
- Create a new erp site
- Add existing modules to this new site
- Create a local erp project running this site
- Create a docker container running this site
- Backing up data from to the container from to the local site

Explanation of terms used
-------------------------
There are a number of terms used in erp-workbench you should understand the meaning of:

- $WB

This is the erp-workbench's home folder. Often ~/erp-workbench


- Site / Site-Description

An erp-workbench site is defined within a site description file.
There are global sites, of which the site descriptions are shared using git repositories, and
local sites, that are only used on the actual pc.

- $Site

The name of the site

For each site a folder-structure is defined the first time it is created. 
The topfolder of this structure is named identically as the site.
Normally this folders are constructed in the erp-workbench's home foler ($WB) but
can be configured to be elsewhere:

- $WB-DATA

- Project 

A project is a local structure, where a site is constructed and can be run locally.

- $PROJECT

This is a projects home folder. Often ~/projects/$SITE/$SITE

- Remote Server

A remote server is a server accessible trough the internet, where $SITE is deployed to a docker container.


Defining what erp type you handle by default:
---------------------------------------------

For the time being (sept. 2018) there are two types of erp system erp-workbench is capable of handling:

    - odoo
    - flectra

Flectra is an odoo fork that has many things with odoo in common.

Selecting the default erp system only defines, what setting will be used when creating a new site. 
By default odoo sites will be generated. To change this, do as follows:

in $WB/config/config.yaml change the line::

  # site_editor:
  # define what editor to use when editing site description
  site_editor: 'code' # <----- name the editor here. 
                      # It must be callable in a bash shell

Change editor to use:
---------------------

When ever any of the workbenches config files are to be edited, they will be presented using an editor.

By default this is *pico*.

to change the editor used to an other one issue the following command::

  bin/e -c

  

How to define/edit a remote server:
-----------------------------------

A remote server definition contains information on a server where a supported erp-system is running.

To edit existing local servers issue::

  bin/e -s

All existing server definitions are presented using the configured editor.

To create a new server definition issue::

  bin/s -a USERNAME@IP_ADDRESS

here USERNAME is the user as which you want to access the server running at address IP_ADDRESS.




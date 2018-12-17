============================
Introduction and first steps
============================

ERP Workbench (WB) is a set of tools that are used to create and maintain local and remote
erp (odoo, flectra, ..) sites.

erp-workbench's goal is to support you trough all steps in the life cycle of an erp-site.
This starts from the very first steps of defining a project for a new site, to develop it,
to deploy it, to maintain it, handle backups and upgrade to newer versions of the erp-software.


First steps you need to work trough
***********************************

Please start with working trough these documents.
They will give you a basic understanding what are the aims of erp-workbench.

    - Install.txt_
    - `What is a site description file`_
    - `Quick Walk Trough`_
    
    .. _Install.txt: INSTALL.txt.html
    .. _What is a site description file: sitedescription.txt.html
    .. _Quick Walk Trough: walktrough/index.html

Do base configurations
**********************

Before erp-workspace can do anything sensible for you, you have to go trough
its base configuration_

    .. _configuration: config.html

Create repository to maintain the site descriptions
***************************************************

You probably want ot share the site descriptions with your team.
Have a look on how to setup a repo for them siteslist_repo_

    .. _siteslist_repo: configuration/siteslist_repo.html

Locations where WB maintains objects
************************************

Objects that are maintained by erp-workbench are at three different locations:

    If you have installed erp-workbench as proposed in the INSTALL.txt these locations are as follows:

    - ~/erp_workbench  ($WB in this documentation)
        that is where WB is installed and site-descriptions are maintained

    - ~/projects ($PROJECT in this documentation, or $SITE when the site description is meant)
        This is where for each local site a folder structure is maintained

    - remote servers (anywhere out there ..)
        This is where docker containers running the sites are hosted

Command categories
******************

Commands are grouped in several categories:

    - create / update 
        These are commands that create or update objects
        like projects or folder structures on the local host.
    - docker
        These commands handle docker object like images and containers
        and objects running in a container like an erp site
    - support
        These are commands to add and remove erp-workbench projects
        and servers to which erp sites are deployed
    - remote
        These are commands that typically are run on the remote servers
        like maintaining the Nginx/Apache virtual sites and their certificates.

Global Sites and Local Sites
****************************

There can be any number of sites-list WB manages.
Global Sites are sites-descriptions that are managed using git and can be shared with your team.
Normally when you create a new sites-description WB asks in what sites-list you want to store it.

::

    bin/s --add-site NEWSITE

But sometimes you want to create a "throw away" site to experiment with. For this you create a local site::

    bin/s --add-site-local NEWLOCALSITE



Create objects:
***************
    bin/c *COMMAND*

    where *COMMAND* could be:

    Commands normally run locally:

    - **-ls**
        list all projects
    - **-c** *project_name* 
        | generate local project *project_name* in the project folder
        |   generate the needed folder structure
        |   download or upgrade all addons as mentioned in the *project_name*'s site-descriptions
        |   generate all aliases
    - **-lo** *project_name* 
        | list own modules mentioned in the *project_name*'s site-descriptions
    - **-I** *project_name* 
        | install all odoo modules (like CRM) as mentioned in the *project_name*'s site-descriptions
    - **-uo** [modules-list]|all *project_name* 
        | install/update own modules as found in the *project_name*'s site-descriptions
        | [modules-list] is a comma separated list of module names
        | if all is used as modules list, then all modules found in the sites description are installed

    Commands normally run remotely:
    
    - **m**
        like -c but do not create project
        |   generate the needed folder structure
        |   download or upgrade all addons as mentioned in the *project_name*'s site-descriptions
        |   generate all aliases

    - **M** addons-list 
        download or upgrade addons-list addons they must be mentioned in the sites descriptions

Docker handling
***************
    bin/d *COMMAND*

Support commands 
****************
    bin/s *COMMAND*
    bin/e [$SITE]

    Commands to add or remove site descriptions

    **--add--site** [--docker-port][--remote-server]
        add global site to the 

Remote commands
***************
    bin/r *COMMAND*

    Commands that make only sense remotely

    **--add-apache**
        build an apache entry for the site

    **--add-nginx**
        build an nginx entry for the site

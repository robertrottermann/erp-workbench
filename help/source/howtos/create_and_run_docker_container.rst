Create and run a docker-container
---------------------------------

In the following explanation we will create and use a site called coobytech.

You should have executed the following beforehand::

    bin/c -m coobytech

Define what database version to use:
************************************

    in config/docker.yaml set the database version::

        # use_postgres_version
        # is used when creating the db image to define what postgres version to use
        use_postgres_version: '10.0'

Create a contained for the databases
************************************
    execute::

        bin/d -dcdb

Check whether the container is running:
***************************************

    execute::

        docker ps

    the exepected output is simmilar to::

        CONTAINER ID        IMAGE                                   COMMAND                  CREATED             STATUS              PORTS                                                 NAMES
        5a7ac08a5948        robertredcor/odoo-project:11.0-latest   "docker-entrypoint.s…"   41 minutes ago      Up 19 minutes       127.0.0.1:9000->8069/tcp, 127.0.0.1:19000->8072/tcp   coobytech
        26e3bcd8e14e        postgres:10.0                           "docker-entrypoint.s…"   4 hours ago         Up 4 hours          0.0.0.0:55432->5432/tcp                               db

Creating the container for coobytech
************************************

    ::

        bin/d - coobytech


Install all odoo main-modules
*****************************

    execute:

        bin/d -dI coobytech
        
   parser_docker.add_argument(
        "-dcu", "--create_update_container",
        action="store_true", dest="docker_create_update_container", default=False,
        help='create a docker container that runs the etc/runodoo.sh script at startup. Name must be provided',
        need_name=True,
        name_valid=True,
    )
 
Troubleshhoting
----------------

There are a number of things that can run amiss:

Container is constanly restarting
*********************************

When you run *docker ps* the staus of a container is Restarting::

    CONTAINER ID        IMAGE                              COMMAND                  CREATED              STATUS                        PORTS                     NAMES
    67f8d32ebd39        coobyhq/odoo-project:11.0-latest   "docker-entrypoint.s…"   45 seconds ago       Restarting (1) 1 second ago                             coobytech
    26e3bcd8e14e        postgres:10.0                      "docker-entrypoint.s…"   About a minute ago   Up About a minute             0.0.0.0:55432->5432/tcp   db

Some of the possible reasons are:

    - Container has no permissions to its data
    - One (or several) module(s) can not be loaded

To find out what the reason of the problem is, you should check the logs

If using the docker command::
    
    docker logs -f coobytech

Produces output similar to the following::

    Starting with UID : 1000
    Running without demo data
    /odoo/src/odoo.egg-info is missing, probably because the directory is a volume.
    Running pip install -e /odoo/src to restore odoo.egg-info
    /odoo/src should either be a path to a local project or a VCS url beginning with svn+, git+, hg+, or bzr+

The reason could be, that the running odoo container has now access to its data files.
This is because within the container the user "odoo" gets assigned a user ID 1000.
This guest-UID is mapped to an arbitrary host-UID. You should therfore grant access rigths to this host-UID

The easiest (ut hacky) way to this is to execute::

    # assuming we are running site coobytech
    chmod 777 coobytech
    chmod 777 coobytech/* -R


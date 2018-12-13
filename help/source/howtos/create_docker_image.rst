Create Docker Image
-------------------

Creating a docker image consist of several steps:

    - collect all apt modules we need next to the one odoo is providing
    - collect all pip libraries we need next to the one odoo is providing
        This information we find in the site description files in a ::
        
            'extra_libs': {
                'pip' : [
                    'xmlsec',
                    'scrapy',
                    'html2text',
                ],
                'apt' : [
                    'python-dev',
                    'pkg-config',
                    'libxml2-dev',
                    'libxslt1-dev',
                    'libxmlsec1-dev',
                    'libffi-dev',
                ]
            },

        section
    - we neet to be able to log into docker hub to be able to push the image
    - downloading the actuall odoo source
    - creating a number of folders that will be copied into the image

This process is done semiautomatically by running the following command::

    wwb
    bin/d -dbi SITENAME -dbiC # where SITENAME could be afbstest


Create DB Image
---------------
before changing anything with an existing container, please check wher its data is by running::

    docker inspect db


docker_db_template::

    docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo \
    -v %(erp_server_data_path)s/database/data:/var/lib/postgresql/data --name db --restart always \
    -p 55432:5432 postgres:%(postgres_version)s



sample configuration created with https://pgtune.leopard.in.ua::

    # DB Version: 10
    # OS Type: linux
    # DB Type: web
    # Total Memory (RAM): 1 GB
    # Connections num: 500
    # Data Storage: hdd

    max_connections = 500
    shared_buffers = 256MB
    effective_cache_size = 768MB
    maintenance_work_mem = 64MB
    checkpoint_completion_target = 0.7
    wal_buffers = 7864kB
    default_statistics_target = 100
    random_page_cost = 4
    effective_io_concurrency = 2
    work_mem = 524kB
    min_wal_size = 1GB
    max_wal_size = 2GB


query settings::

    SELECT * FROM pg_settings;

    SELECT *
    FROM   pg_settings
    WHERE  name = 'max_connections';

Troubleshooting
***************
    ::

        ...

        Requirement already satisfied: chardet<3.1.0,>=3.0.2 in /usr/local/lib/python3.5/dist-packages 
            (from requests>=2.0.0; python_version >= "3.0"->twilio) (3.0.4)
        Requirement already satisfied: urllib3<1.25,>=1.21.1 in /usr/local/lib/python3.5/dist-packages 
            (from requests>=2.0.0; python_version >= "3.0"->twilio) (1.23)

        Exception:
        Traceback (most recent call last):
        File "/usr/local/lib/python3.5/dist-packages/pip/_internal/cli/base_command.py", line 154, in main
            status = self.run(options, args)
        File "/usr/local/lib/python3.5/dist-packages/pip/_internal/commands/install.py", line 346, in run
            session=session, autobuilding=True
        File "/usr/local/lib/python3.5/dist-packages/pip/_internal/wheel.py", line 788, in build
            assert building_is_possible
        AssertionError


        --------------------------------------------
        a new image coobytech for container coobytech could not be created
        ERROR: {'code': 2, 'message': "The command '/bin/sh -c set -x;             apt install default-libmysqlclient-dev         libffi-dev         libxslt1-dev         zlib1g-dev         libssl-dev         build-essential         libxml2-dev         python3-dev         python-dev ;    pip install xlrd email_validator mysql-connector sqlalchemy twilio phonenumbers validate_email' returned a non-zero code: 2"}
        To better understand what is the reason please inspect the generated
        Dockerfile: /home/robert/erp-workbench/coobytech/docker/Dockerfile
        You can try to build it like so:
        cd /home/robert/erp-workbench/coobytech/docker/
        docker build .
        ---------------------------------------------

In the above error message we see, that the build process failed while pip installing twilio.
So we edit the Dockerfile by removing twilio. If that helps, we try to find out why it could not be installed
and add the missing elements to the dockerfiles.

When we have the Dockerfile building, we must make sure to add the elements that we added to the Dockerfile to the
site-description from which the Dockerfile was generated. 
# --------------------------------------------------
# -------------------- logout ------------------------
# --------------------------------------------------
logout_template = """
%(docker_command)s logout
"""

# --------------------------------------------------
# -------------------- odoo ------------------------
# --------------------------------------------------
# docker run -p 8069:8069 --name odoo --link db:db -t odoo -- --db-filter=odoo_db_.*
# docker run -v /path/to/addons:/mnt/extra-addons -p 8069:8069 --name odoo --link db:db -t odoo
docker_template_odoo_base = """
%(docker_command)s run -p 127.0.0.1:%(erp_port)s:8069 -p 127.0.0.1:%(erp_longpoll)s:8072 --restart always \\
    -v %(erp_server_data_path)s/%(site_name)s/etc:/etc/odoo \\
    -v %(erp_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons \\
    -v %(erp_server_data_path)s/%(site_name)s/dump:/mnt/dump \\
    -v %(erp_server_data_path)s/%(site_name)s/filestore:/var/lib/odoo/filestore \\
    -v %(erp_server_data_path)s/%(site_name)s/:/var/lib/odoo/ \\
    -v %(erp_server_data_path)s/%(site_name)s/log:/var/log/odoo \\
    -e ODOO_BASE_URL='%(base_url)s' \\
    -e ODOO_REPORT_URL='%(base_url)s' \\
    %(docker_common)s \\
    --name %(container_name)s -d --link db:db -t %(erp_image_version)s
"""
docker_template = """
%(docker_command)s run -p 127.0.0.1:%(erp_port)s:8069 -p 127.0.0.1:%(erp_longpoll)s:8072 --restart always \\
    -v %(erp_server_data_path)s/%(site_name)s/etc:/etc/odoo \\
    -v %(erp_server_data_path)s/%(site_name)s/start-entrypoint.d:/opt/odoo/start-entrypoint.d \\
    -v %(erp_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons \\
    -v %(erp_server_data_path)s/%(site_name)s/dump:/mnt/dump \\
    -v %(erp_server_data_path)s/%(site_name)s/filestore:/var/lib/odoo/filestore \\
    -v %(erp_server_data_path)s/%(site_name)s/:/var/lib/odoo/ \\
    -v %(erp_server_data_path)s/%(site_name)s/log:/var/log/odoo \\
    -e ODOO_BASE_URL='%(base_url)s' \\
    -e ODOO_REPORT_URL='%(base_url)s' \\
    %(docker_common)s \\
    --name %(container_name)s -d --link db:db -t %(erp_image_version)s
"""
docker_delete_template = """
%(docker_command)s rm  %(container_name)s
"""
# for docker_template_update I changed:
# --restart always -> --rm
# -d -> ''
# -> --init /etc/odoo/runodoo.sh \
docker_template_update = """
%(docker_command)s run -p 127.0.0.1:%(erp_port)s:8069 -p 127.0.0.1:%(erp_longpoll)s:8072 --rm \
    --entrypoint /etc/odoo/runodoo.sh \
    -v %(erp_server_data_path)s/%(site_name)s/etc:/etc/odoo \
    -v %(erp_server_data_path)s/%(site_name)s/start-entrypoint.d:/opt/odoo/start-entrypoint.d \
    -v %(erp_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons \
    -v %(erp_server_data_path)s/%(site_name)s/dump:/mnt/dump \
    -v %(erp_server_data_path)s/%(site_name)s/filestore:/var/lib/odoo/filestore \
    -v %(erp_server_data_path)s/%(site_name)s/:/var/lib/odoo/ \
    -v %(erp_server_data_path)s/%(site_name)s/log:/var/log/odoo \
    %(docker_common)s \
    --name %(container_name)s_tmp --link db:db -t %(erp_image_version)s
"""

docker_db_template = """
    %(docker_command)s run -d -e  POSTGRES_USER=odoo -e  POSTGRES_PASSWORD=odoo \
    -v %(erp_server_data_path)s/database/data:/var/lib/postgresql/data --name db --restart always \
    -p 55432:5432 postgres:%(postgres_version)s
"""

docker_file_template = """
FROM %(erp_base_image)s

# Install dependencies
RUN apt-get update && apt-get install -y \

RUN add-apt-repository universe
RUN apt-get update && apt-get install -y \
    python-pip

RUN pip install %(pip_list)s
"""
docker_run_apt_template = """# Project's specifics packages
RUN set -x; \\
        apt-get update \\
        && apt-get install -y --no-install-recommends \\
        %(apt_list)s \\
        %(pip_install)s %(pip_list)s \\
        && apt-get remove -y \\
        %(apt_list)s \\
        && apt-get clean \\
        && rm -rf /var/lib/apt/lists/*
"""
docker_run_no_apt_template = """# Project's specifics packages
RUN set -x; \\
        %(pip_install)s %(pip_list)s \\
"""

docker_base_file_template = """
FROM debian:buster
#FROM debian:buster-slim
MAINTAINER robert@redo2oo.ch

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN set -x; \\
    apt-get update && \\
    apt-get install -y --no-install-recommends \\
        ca-certificates \\
        curl \\
        dirmngr \\
        fonts-noto-cjk \\
        gnupg \\
        libssl-dev \\
        node-less \\
        npm \\
        python3-num2words \\
        python3-pdfminer \\
        python3-pip \\
        python3-phonenumbers \\
        python3-pyldap \\
        python3-qrcode \\
        python3-renderpm \\
        python3-setuptools \\
        python3-slugify \\
        python3-vobject \\
        python3-watchdog \\
        python3-xlrd \\
        python3-xlwt \\
        xz-utils \\
            python-libxslt1 \\
            xfonts-75dpi \\
            xfonts-base \\
            # build packages to clean after the pip install
            build-essential \\
            libfreetype6-dev \\
            libpq-dev \\
            libxml2-dev \\
            libxslt1-dev \\
            libsasl2-dev \\
            libldap2-dev \\
            libssl-dev \\
            libjpeg-dev \\
            zlib1g-dev \\
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb \\
    && echo '7e35a63f9db14f93ec7feeb0fce76b30c08f2057 wkhtmltox.deb' | sha1sum -c - \\
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \\
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main' > /etc/apt/sources.list.d/pgdg.list \\
    && GNUPGHOME="$(mktemp -d)" \\
    && export GNUPGHOME \\
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \\
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \\
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \\
    && gpgconf --kill all \\
    && rm -rf "$GNUPGHOME" \\
    && apt-get update  \\
    && apt-get install --no-install-recommends -y postgresql-client \\
    && rm -f /etc/apt/sources.list.d/pgdg.list \\
    && rm -rf /var/lib/apt/lists/*

# Install rtlcss (on Debian buster)
RUN npm install -g rtlcss

# Install Odoo
ENV ODOO_VERSION=%(erp_version)s
#ENV ODOO_VERSION 14.0
#ARG ODOO_RELEASE=20201002
ARG ODOO_SHA=70917e1db8d100c791f31afbfcd782dd026bd4c9
#!!! we can not calculate the sha1sum since we do not really know the release ..
# RUN curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \\
#     && echo "${ODOO_SHA} odoo.deb" | sha1sum -c - \\
RUN curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.latest_all.deb  \\
    && apt-get update \\
    && apt-get -y install --no-install-recommends ./odoo.deb \\
    && rm -rf /var/lib/apt/lists/* odoo.deb

# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/

# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN chown odoo /etc/odoo/odoo.conf \\
    && mkdir -p /mnt/extra-addons \\
    && chown -R odoo /mnt/extra-addons
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]

"""

docker_base_file_templateX = """
FROM %(erp_image_version)s
MAINTAINER robert@redo2oo.ch

# create the working directory and a place to set the logs (if wanted)
RUN mkdir -p /opt/odoo /var/log/odoo

WORKDIR "/opt/odoo"

COPY ./base_requirements.txt ./

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN set -x; \\
        apt-get update \\
        && apt-get install -y --no-install-recommends \\
            antiword \\
            ca-certificates \\
            curl \\
            ghostscript \\
            graphviz \\
            less \\
            nano \\
            node-clean-css \\
            node-less \\
            poppler-utils \\
            postgresql-client \\
            dirmngr \\
            fonts-noto-cjk \\
            gnupg \\
            npm \\
            python3-setuptools \\
            python3-num2words \\
            python3-pdfminer \\
            python3-pip \\
            python3-dev \\
            python3-phonenumbers \\
            python3-pyldap \\
            python3-qrcode \\
            python3-renderpm \\
            python3-setuptools \\
            python3-slugify \\
            python3-vobject \\
            python3-watchdog \\
            python3-xlrd \\
            python3-xlwt \\
            xz-utils \\
            python-libxslt1 \\
            xfonts-75dpi \\
            xfonts-base \\
            # build packages to clean after the pip install
            build-essential \\
            libfreetype6-dev \\
            libpq-dev \\
            libxml2-dev \\
            libxslt1-dev \\
            libsasl2-dev \\
            libldap2-dev \\
            libssl-dev \\
            libjpeg-dev \\
            zlib1g-dev \\
        && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb \\
        && echo '7e35a63f9db14f93ec7feeb0fce76b30c08f2057 wkhtmltox.deb' | sha1sum -c - \\
        && apt-get install -y --no-install-recommends ./wkhtmltox.deb \\
        && pip3 install -U pip && pip3 install -r base_requirements.txt \\
        && apt-get remove -y build-essential python-dev libfreetype6-dev libpq-dev libxml2-dev libxslt1-dev \\
                             libsasl2-dev libldap2-dev libssl-dev libjpeg-dev zlib1g-dev libfreetype6-dev \\
        && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false -o APT::AutoRemove::SuggestsImportant=false npm \\
        && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# grab gosu for easy step-down from root
RUN gpg --keyserver pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \\
        && curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.2/gosu-$(dpkg --print-architecture)" \\
        && curl -o /usr/local/bin/gosu.asc -SL "https://github.com/tianon/gosu/releases/download/1.2/gosu-$(dpkg --print-architecture).asc" \\
        && gpg --verify /usr/local/bin/gosu.asc \\
        && rm /usr/local/bin/gosu.asc \\
        && chmod +x /usr/local/bin/gosu

# grab dockerize for generation of the configuration file and wait on postgres
RUN curl https://github.com/jwilder/dockerize/releases/download/v0.2.0/dockerize-linux-amd64-v0.2.0.tar.gz -L | tar xz -C /usr/local/bin

COPY ./src_requirements.txt ./
COPY ./bin bin
COPY ./etc etc
COPY ./MANIFEST.in ./

VOLUME ["/data/odoo", "/var/log/odoo"]

# Expose Odoo services
EXPOSE 8069 8071 8072

ENV ODOO_VERSION=s(erp_version)s \\
    PATH=/opt/odoo/bin:$PATH \\
    LANG=C.UTF-8 \\
    LC_ALL=C.UTF-8 \\
    DB_PORT=5432 \\
    DB_NAME=odoodb \\
    DB_USER=odoo \\
    DB_PASSWORD=odoo \\
    DEMO=False \\
    ADDONS_PATH=/opt/odoo/local-src,/opt/odoo/src/addons \\
    OPENERP_SERVER=/opt/odoo/etc/openerp.cfg

ENTRYPOINT ["./bin/docker-entrypoint.sh"]
CMD ["./src/odoo.py"]

# intermediate images should help speed up builds when only local-src, or only
# external-src changes
ONBUILD COPY ./src src
ONBUILD COPY ./external-src external-src
ONBUILD COPY ./local-src local-src
ONBUILD COPY ./data data
ONBUILD COPY ./songs songs
ONBUILD COPY ./setup.py ./
ONBUILD COPY ./VERSION ./
ONBUILD COPY ./migration.yml ./
# need to be called at the end, because it installs . and src
ONBUILD RUN pip install -r src_requirements.txt

%(run_block)s

COPY ./requirements.txt /odoo/
RUN cd /odoo && pip install --cache-dir=.pip -r requirements.txt

%(run_extra_run_block)s

# ENV ADDONS_PATH=/odoo/local-src,/odoo/src/addons
# ENV DB_NAME=xxxxxx
ENV MIGRATE=False
# Set the default config file
ENV OPENERP_SERVER /etc/odoo/openerp-server.conf
%(env_vars)s
"""

src_requirements = """# Requirements for the project itself and for Odoo.
# When we install Odoo with -e, odoo.py is available in the PATH and
# 'openerp' in the PYTHONPATH
#
# They are installed only after all the project's files have been copied
# into the image (with ONBUILD)
-e .
-e src

"""

XXXX = """
FROM %(erp_image_version)s
MAINTAINER robert@redo2oo.ch

# For installing odoo you have two possibility
# 1. either adding the whole root directory
#COPY . /odoo

# 2. or adding each directory, this solution will reduce the build and download
# time of the image on the server (layers are reused)
COPY ./src /odoo/src
COPY ./external-src /odoo/external-src
COPY ./local-src /odoo/local-src
COPY ./data /odoo/data
COPY ./songs /odoo/songs
COPY ./setup.py /odoo/
COPY ./VERSION /odoo/
COPY ./migration.yml /odoo/
RUN pip install --cache-dir=.pip -e  /odoo
RUN pip install --cache-dir=.pip -e  /odoo/src

%(run_block)s

COPY ./requirements.txt /odoo/
RUN cd /odoo && pip install --cache-dir=.pip -r requirements.txt

%(run_extra_run_block)s

# ENV ADDONS_PATH=/odoo/local-src,/odoo/src/addons
# ENV DB_NAME=xxxxxx
ENV MIGRATE=False
# Set the default config file
ENV OPENERP_SERVER /etc/odoo/openerp-server.conf
%(env_vars)s
"""
docker_erp_setup_version = """
%s.0
"""
docker_erp_setup_requirements = """
# project's packages, customize for your needs:
unidecode==0.4.14
"""

docker_erp_setup_script = """
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('VERSION') as fd:
    version = fd.read().strip()

setup(
    name="my-project-name",
    version=version,
    description="project description",
    license='GNU Affero General Public License v3 or later (AGPLv3+)',
    author="Author...",
    author_email="email...",
    url="url...",
    packages=['songs'] + ['songs.%s' % p for p in find_packages('./songs')],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved',
        'License :: OSI Approved :: '
        'GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
"""
# --------------------------------------------------
# -------------------- FLECTRA ---------------------
# --------------------------------------------------
flectra_docker_template = """
docker run -p 127.0.0.1:%(erp_port)s:7073 -p 127.0.0.1:%(erp_longpoll)s:7072 --restart always \
    -v %(erp_server_data_path)s/%(site_name)s/etc:/etc/flectra \
    -v %(erp_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons \
    -v %(erp_server_data_path)s/%(site_name)s/dump:/mnt/dump \
    -v %(erp_server_data_path)s/%(site_name)s/filestore:/var/lib/flectra/filestore \
    -v %(erp_server_data_path)s/%(site_name)s/:/var/lib/flectra/ \
    -v %(erp_server_data_path)s/%(site_name)s/log:/var/log/flectra \
    -e  LOCAL_USER_ID=1000 -e  DB_NAME=%(site_name)s \
    -e  PYTHONIOENCODING=utf-8 \
    --name %(container_name)s -d --link db:db -t %(erp_image_version)s
"""

dumper_docker_template = """
# dbdumper Dockerfile
FROM debian:buster

RUN apt update; apt install -y wget gnupg; \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - ; \
    sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
RUN apt-get update &&  apt-get install postgresql-client-%(postgres_version)s vim python -y --allow-unauthenticated

ENTRYPOINT ["/usr/bin/python", "/mnt/sites/dumper/dumper.py"]
"""

docker_common = """-e ADDONS_PATH=%(docker_site_addons_path)s\\
    -e LOCAL_USER_ID=1000 \\
    -e DB_NAME=%(site_name)s \\
    -e PYTHONIOENCODING=utf-8 \\
    -e PYTHONIOENCODING=utf-8 \\
    -e DB_HOST = %(db_host)s \\
    -e DB_NAME = %(db_name)s \\
    -e DB_USER = %(db_user)s \\
    -e DB_PASSWORD=%(db_password)s \\
    -e DB_SSLMODE=%(db_sslmode)s \\
    -e DBFILTER=%(dbfilter)s \\
    -e LIST_DB=%(list_db)s \\
    -e ADMIN_PASSWD='%(admin_passwd)s' \\
    -e DB_MAXCONN=%(db_maxconn)s \\
    -e LIMIT_MEMORY_SOFT=%(limit_memory_soft)s \\
    -e LIMIT_MEMORY_HARD=%(limit_memory_hard)s \\
    -e LIMIT_REQUEST=%(limit_request)s \\
    -e LIMIT_TIME_CPU=%(limit_time_cpu)s \\
    -e LIMIT_TIME_REAL=%(limit_time_real)s \\
    -e LIMIT_TIME_REAL_CRON=%(limit_time_real_cron)s \\
    -e LOG_HANDLER=%(log_handler)s \\
    -e LOG_LEVEL=%(log_level)s \\
    -e MAX_CRON_THREADS=%(max_cron_threads)s \\
    -e WORKERS=%(workers)s \\
    -e LOGFILE=%(logfile)s \\
    -e LOG_DB=%(log_db)s \\
    -e LOGROTATE=%(logrotate)s \\
    -e SYSLOG=%(syslog)s \\
    -e RUNNING_ENV=%(running_env)s \\
    -e WITHOUT_DEMO=%(without_demo)s \\
    -e SERVER_WIDE_MODULES=%(server_wide_modules)s"""


docker_base_requirements_9 = """
arrow==0.4.2
atomicwrites==1.4.0
attrs==19.3.0
Automat==20.2.0
Babel==1.3
backports.functools-lru-cache==1.6.1
bcrypt==3.1.7
beautifulsoup4==4.9.1
certifi==2020.6.20
cffi==1.14.2
chardet==3.0.4
configparser==4.0.2
constantly==15.1.0
contextlib2==0.6.0.post1
cryptography==3.0
cssselect==1.1.0
decorator==3.4.0
docutils==0.12
enum34==1.1.10
feedparser==5.1.3
fs==0.5.4
funcsigs==1.0.2
functools32==3.2.3.post2
gdata==2.0.18
gevent==1.0.2
greenlet==0.4.7
html2text==2019.8.11
htmllaundry==2.2
hyperlink==20.0.1
ics==0.4
idna==2.10
importlib-metadata==1.7.0
incremental==17.5.0
ipaddress==1.0.23
jcconv==0.2.3
Jinja2==2.8.1
lxml==3.4.1
Mako==1.0.1
MarkupSafe==0.23
mock==1.0.1
more-itertools==5.0.0
oauthlib==3.1.0
# Editable install with no version control (odoo==9.0rc20190424)
-e /home/robert/projects/afbschweiz/afbschweiz/downloads/odoo-9.0rc20190424
OdooRPC==0.7.0
ofxparse==0.14
packaging==20.4
paramiko==2.7.1
parsel==1.6.0
passlib==1.6.2
pathlib==1.0.1
pathlib2==2.3.5
phonenumbers==8.12.8
Pillow==3.3.2
pluggy==0.13.1
Protego==0.1.16
psutil==2.2.0
psycogreen==1.0
psycopg2==2.8.5
py==1.9.0
pyasn1==0.4.8
pyasn1-modules==0.2.8
pycparser==2.20
PyDispatcher==2.0.5
pydot==1.0.2
Pygments==2.5.2
PyHamcrest==1.10.1
PyNaCl==1.4.0
pyOpenSSL==19.1.0
pyparsing==2.0.3
pyPdf==1.13
pypng==0.0.20
PyQRCode==1.2.1
pyserial==2.7
pysftp==0.2.9
pytest==4.6.11
pytest-odoo==0.5.0
Python-Chart==1.39
python-dateutil==2.4.0
python-ldap==2.4.19
python-openid==2.2.5
python-stdnum==1.14
pytz==2014.10
pyusb==1.0.0b2
PyYAML==3.11
qrcode==5.1
queuelib==1.5.0
reportlab==3.1.44
requests==2.6.0
scandir==1.10.0
Scrapy==1.8.0
service-identity==18.1.0
six==1.9.0
soupsieve==1.9.6
suds-jurko==0.6
Twisted==20.3.0
typing==3.7.4.3
urllib3==1.25.10
vatnumber==1.2
vobject==0.6.6
w3lib==1.22.0
wcwidth==0.2.5
Werkzeug==0.15.2
xlrd==1.2.0
xlwt==0.7.5
zipp==1.2.0
zope.event==4.4
zope.interface==5.1.0
"""
docker_base_requirements_13 = """
ansible==2.9.13
appdirs==1.4.4
arrow==0.14.7
attrs==19.3.0
Automat==20.2.0
Babel==2.6.0
bcrypt==3.1.7
beautifulsoup4==4.9.1
cached-property==1.5.1
cachetools==4.1.1
certifi==2020.6.20
cffi==1.14.1
chardet==3.0.4
constantly==15.1.0
cryptography==3.0
cssselect==1.1.0
decorator==4.3.0
defusedxml==0.6.0
docopt==0.6.2
docutils==0.14
ebaysdk==2.1.5
feedparser==5.2.1
fs==2.4.11
gdata==2.0.18
gevent==1.3.7
greenlet==0.4.15
html2text==2018.1.9
htmllaundry==2.2
hyperlink==20.0.1
ics==0.7
idna==2.8
incremental==17.5.0
iniconfig==1.0.1
isodate==0.6.0
itemadapter==0.1.0
itemloaders==1.0.2
Jinja2==2.10.1
jmespath==0.10.0
libsass==0.17.0
lxml==4.3.2
Mako==1.0.7
MarkupSafe==1.1.0
mock==2.0.0
more-itertools==8.4.0
mt940==0.5.0
num2words==0.5.6
oauthlib==3.1.0
OdooRPC==0.7.0
ofxparse==0.19
packaging==20.4
paramiko==2.7.1
parsel==1.6.0
passlib==1.7.1
pathlib==1.0.1
pbr==5.4.5
phonenumbers==8.12.7
Pillow==5.4.1
pluggy==0.13.1
polib==1.1.0
Protego==0.1.16
psutil==5.6.6
psycopg2==2.8.3
psycopg2-binary==2.8.5
py==1.9.0
pyasn1==0.4.8
pyasn1-modules==0.2.8
pycparser==2.20
PyDispatcher==2.0.5
pydot==1.4.1
Pygments==2.6.1
PyHamcrest==2.0.2
PyNaCl==1.4.0
pyOpenSSL==19.1.0
pyparsing==2.2.0
PyPDF2==1.26.0
pypng==0.0.20
PyQRCode==1.2.1
pyserial==3.4
pysftp==0.2.9
pytest==6.0.1
pytest-odoo==0.5.0
python-dateutil==2.7.3
python-ldap==3.1.0
python-stdnum==1.14
pytz==2019.1
pyusb==1.0.2
PyYAML==5.3.1
qrcode==6.1
queuelib==1.5.0
reportlab==3.5.13
requests==2.21.0
requests-toolbelt==0.9.1
Scrapy==2.3.0
service-identity==18.1.0
six==1.15.0
soupsieve==2.0.1
TatSu==5.5.0
toml==0.10.1
Twisted==20.3.0
urllib3==1.24.3
urlparse3==1.1
vatnumber==1.2
vobject==0.9.6.1
w3lib==1.22.0
Werkzeug==0.14.1
xlrd==1.1.0
XlsxWriter==1.1.2
xlwt==1.3.0
zeep==3.2.0
zope.event==4.4
zope.interface==5.1.0
"""
docker_base_requirements_14 = """
appdirs==1.4.4
attrs==20.2.0
Babel==2.8.0
bcrypt==3.1.7 #3.2
beautifulsoup4==4.9.2
cached-property==1.5.2
certifi==2020.6.20
cffi==1.14.3
chardet==3.0.4
cryptography==3.1.1
decorator==4.4.2
defusedxml==0.6.0
docutils==0.16
feedparser #==5.2.1 #6.0.1
gdata==2.0.18
gevent==20.9.0
greenlet==0.4.17
html2text #==2020.1.16
idna==2.10
iniconfig==1.0.1
isodate==0.6.0
Jinja2==2.11.2
libsass==0.20.1
lxml==4.5.2
Mako==1.1.3
MarkupSafe==1.1.1
mock #==4.0.2
OdooRPC==0.7.0
ofxparse==0.20
packaging==20.4
paramiko==2.7.2
passlib==1.7.2
Pillow
pluggy==0.13.1
polib==1.1.0
psutil==5.7.2
psycopg2==2.8.6
py==1.9.0
pycparser==2.20
pydot==1.4.1
PyNaCl==1.4.0
pyparsing==2.4.7
PyPDF2==1.26.0
pyserial==3.4
pysftp==0.2.9
pytest==6.1.0
pytest-odoo==0.6.0
python-dateutil==2.8.1
python-stdnum==1.14
pytz==2020.1
pyusb==1.1.0
qrcode==6.1
reportlab==3.5.51
requests==2.24.0
requests-toolbelt==0.9.1
sgmllib3k==1.0.0
six==1.15.0
soupsieve==2.0.1
toml==0.10.1
urllib3==1.25.10
vobject==0.9.6.1
Werkzeug==1.0.1
XlsxWriter==1.3.6
xlwt==1.3.0
zeep==3.4.0
zope.event==4.5.0
zope.interface==5.1.0
"""

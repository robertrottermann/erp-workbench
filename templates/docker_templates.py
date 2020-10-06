# --------------------------------------------------
# -------------------- logout ------------------------
# --------------------------------------------------
logout_template = """
%(docker_command)s logout
"""

# --------------------------------------------------
# -------------------- odoo ------------------------
# --------------------------------------------------
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
            python \\
            python-libxslt1 \\
            python-pip \\
            xfonts-75dpi \\
            xfonts-base \\
            # build packages to clean after the pip install
            build-essential \\
            python-dev \\
            libfreetype6-dev \\
            libpq-dev \\
            libxml2-dev \\
            libxslt1-dev \\
            libsasl2-dev \\
            libldap2-dev \\
            libssl-dev \\
            libjpeg-dev \\
            zlib1g-dev \\
            libfreetype6-dev \\
        && curl -o wkhtmltox.deb -SL http://nightly.odoo.com/extra/wkhtmltox-0.12.1.2_linux-jessie-amd64.deb \\
        && dpkg --force-depends -i wkhtmltox.deb \\
        && apt-get -y install -f --no-install-recommends \\
        && pip install -U pip && pip install -r base_requirements.txt \\
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
EXPOSE 8069 8072

ENV ODOO_VERSION=9.0 \\
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

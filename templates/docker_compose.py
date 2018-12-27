composer_template = """
version: '3'
services:
  odoo:
    container_name: %(container_name)s
    image: %(erp_image_version)s
    depends_on:
      - %(docker_db_container_name)s
    ports:
      - "%(erp_port)s:8069"
      - "%(erp_longpoll)s:8069"
    volumes:
        - %(erp_server_data_path)s/%(site_name)s/etc:/etc/odoo
        - %(erp_server_data_path)s/%(site_name)s/start-entrypoint.d:/opt/odoo/start-entrypoint.d
        - %(erp_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons
        - %(erp_server_data_path)s/%(site_name)s/dump:/mnt/dump
        - %(erp_server_data_path)s/%(site_name)s/filestore:/var/lib/odoo/filestore
        - %(erp_server_data_path)s/%(site_name)s/:/var/lib/odoo/
        - %(erp_server_data_path)s/%(site_name)s/log:/var/log/odoo
    environment:
        - LOCAL_USER_ID=%(docker_local_user_id)s
        - DB_NAME=%(site_name)s
        - PYTHONIOENCODING=utf-8
        # from the camptocamp template
        - DB_HOST = %(db_host)s
        - DB_NAME = %(db_name)s
        - DB_USER = %(db_user)s
        - DB_PASSWORD=%(db_password)s
        - DB_SSLMODE=%(db_sslmode)s
        - DBFILTER=%(dbfilter)s
        - LIST_DB=%(list_db)s
        - ADMIN_PASSWD=%(admin_passwd)s
        - DB_MAXCONN=%(db_maxconn)s
        - LIMIT_MEMORY_SOFT=%(limit_memory_soft)s
        - LIMIT_MEMORY_HARD=%(limit_memory_hard)s
        - LIMIT_REQUEST=%(limit_request)s
        - LIMIT_TIME_CPU=%(limit_time_cpu)s
        - LIMIT_TIME_REAL=%(limit_time_real)s
        - LIMIT_TIME_REAL_CRON=%(limit_time_real_cron)s
        - LOG_HANDLER=%(log_handler)s
        - LOG_LEVEL=%(log_level)s
        - MAX_CRON_THREADS=%(max_cron_threads)s
        - WORKERS=%(workers)s
        - LOGFILE=%(logfile)s
        - LOG_DB=%(log_db)s
        - LOGROTATE=%(logrotate)s
        - SYSLOG=%(syslog)s
        - RUNNING_ENV=%(running_env)s
        - WITHOUT_DEMO=%(without_demo)s
        - SERVER_WIDE_MODULES=%(server_wide_modules)s

   %(docker_db_container_name)s:
        image: postgres: 10
        environment:
            - POSTGRES_PASSWORD = %(db_password)s
            - POSTGRES_USER = %(db_user)s
            - POSTGRES_DB = postgres

"""

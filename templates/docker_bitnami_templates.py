# --------------------------------------------------
# -------------------- bitnami ------------------------
# --------------------------------------------------
docker_bitnami_template = """
%(docker_command)s run -p 127.0.0.1:%(erp_port)s:8069 -p 127.0.0.1:%(erp_longpoll)s:8072 --restart always \\
    -v %(erp_server_data_path)s/%(site_name)s/etc:/etc/odoo \\
    -v %(erp_server_data_path)s/%(site_name)s/start-entrypoint.d:/opt/odoo/start-entrypoint.d \\
    -v %(erp_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons \\
    -v %(erp_server_data_path)s/%(site_name)s/dump:/mnt/dump \\
    -v %(erp_server_data_path)s/%(site_name)s/filestore:/var/lib/odoo/filestore \\
    -v %(erp_server_data_path)s/%(site_name)s/:/var/lib/odoo/ \\
    -v %(erp_server_data_path)s/%(site_name)s/log:/var/log/odoo \\
    %(docker_common)s \\
    --name %(container_name)s -d --link db:db -t %(erp_image_version)s
"""

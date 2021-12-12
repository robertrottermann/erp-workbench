# cat dump/afbs13.dmp | docker exec -i db psql -U odoo -d afbs13
import os,sys
data = {
    'erp_server_data_path' : os.getcwd(),
    'site_name' : 'afbs13',
    'erp_longpoll' : 19999,
    'erp_port' : 9999,
    'erp_image_version' : 'dienstag', # 'robertredcor/afbs13:latest',
    'base_url' : 'localhost:9999',
    'container_name' : 'afbs13loc',
    'docker_command' : 'docker',
}
docker_template = """
%(docker_command)s  stop %(container_name)s
%(docker_command)s  rm %(container_name)s
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
    -e DB_NAME='%(site_name)s' \\
    --name %(container_name)s -d --link db:db -t %(erp_image_version)s
"""

print( docker_template % data)
with open('mk_cont.sh', 'w') as f:
    f.write(docker_template % data)
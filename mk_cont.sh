
docker run -p 127.0.0.1:9999:8069 -p 127.0.0.1:19999:8072 --restart always \
    -v /home/robert/workbench/afbs13/etc:/etc/odoo \
    -v /home/robert/workbench/afbs13/start-entrypoint.d:/opt/odoo/start-entrypoint.d \
    -v /home/robert/workbench/afbs13/addons:/mnt/extra-addons \
    -v /home/robert/workbench/afbs13/dump:/mnt/dump \
    -v /home/robert/workbench/afbs13/filestore:/var/lib/odoo/filestore \
    -v /home/robert/workbench/afbs13/:/var/lib/odoo/ \
    -v /home/robert/workbench/afbs13/log:/var/log/odoo \
    -e ODOO_BASE_URL='localhost:9999' \
    -e ODOO_REPORT_URL='localhost:9999' \
    -e DB_NAME='afbs13' \
    --name afbs13loc -d --link db:db -t dienstag

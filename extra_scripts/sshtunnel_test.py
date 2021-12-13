from sshtunnel import SSHTunnelForwarder
import odoorpc

server = SSHTunnelForwarder(
     "localhost", # 'testmachines',
     ssh_username="root",
#    ssh_password="secret",
    remote_bind_address=('172.24.0.3', 8069)
)


server.start()
odoo = odoorpc.ODOO('localhost', port=server.local_bind_port, timeout=1200)
print(odoo.db.list())
odoo.login('red_backup', 'admin', 'admin')
module_obj = odoo.env["ir.module.module"]
mlist = module_obj.search([("application", "=", True)])
for m in mlist:
    print(m)
print(server.local_bind_port)  # show assigned local port
# work with `SECRET SERVICE` through `server.local_bind_port`.

server.stop()
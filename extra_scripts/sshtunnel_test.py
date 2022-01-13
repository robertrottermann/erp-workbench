from sshtunnel import SSHTunnelForwarder
import odoorpc
MACHINE = "chrissy"
server = SSHTunnelForwarder(
     MACHINE, # 'testmachines',
     ssh_username="robert",
#    ssh_password="secret",
    remote_bind_address=('172.17.0.6', 8100),
    local_bind_address = ('192.168.0.43', 8069)
)


server.start()
print('------------->', server.local_bind_address, server.local_bind_port)
odoo = odoorpc.ODOO(server.local_bind_address[0], port=server.local_bind_port, timeout=1200)
print(odoo.db.list())
odoo.login('breitsch15test', 'admin', 'admin')
module_obj = odoo.env["ir.module.module"]
mlist = module_obj.search([("application", "=", True)])
for m in mlist:
    print(m)
print(server.local_bind_port)  # show assigned local port
# work with `SECRET SERVICE` through `server.local_bind_port`.

server.stop()
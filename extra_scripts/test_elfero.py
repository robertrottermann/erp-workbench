import os
import sys
from argparse import ArgumentParser
from odoorpc import ODOO
import psycopg2

class OdooHandler(object):
    def __init__(self, opts, odoo=None):
        self.opts = opts
        if not odoo:
            print("host: %s, port: %s" % (opts.host, opts.port))
            conn = psycopg2.connect(host=opts.host, port=opts.port)
            print(
                "dbname: %s, user: %s, password : %s"
                % (opts.dbname, opts.user, opts.password)
            )
            odoo.login(db=opts.dbname, login=opts.user, password=opts.password)
        self.odoo = odoo
        #self.ail = odoo.env["account.invoice.line"]
        #self.pt = odoo.env["product.template"]
        #self.mprods = self.pt.browse(self.pt.search([("id", "in", (5, 6, 7))]))
        #self.ai = odoo.env["account.invoice"]


def main(opts):
    handler = OdooHandler(opts)


if __name__ == "__main__":
    usage = "create_memberhip_invoices.py -h for help on usage"
    parser = ArgumentParser(usage=usage)

    parser.add_argument(
        "-H",
        "--host",
        action="store",
        dest="host",
        default="localhost",
        help="define host default localhost",
    )
    parser.add_argument(
        "-p",
        "--port",
        action="store",
        dest="port",
        default=8069,
        help="define port default 8069",
    )
    parser.add_argument(
        "-d",
        "--dbname",
        action="store",
        dest="dbname",
        default="afbs13",
        help="define dbname default 'elfero'",
    )
    parser.add_argument(
        "-u",
        "--user",
        action="store",
        dest="user",
        default="admin",
        help="define user default 'admin'",
    )
    parser.add_argument(
        "-pw",
        "--password",
        action="store",
        dest="password",
        default="admin",
        help="define password default 'admin'",
    )
    opts = parser.parse_args()
    main(opts)

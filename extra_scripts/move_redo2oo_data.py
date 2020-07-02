# -*- encoding: utf-8 -*-
from odoorpc import ODOO
from argparse import ArgumentParser
import copy
from datetime import date, timedelta
from bs4 import BeautifulSoup
import re

class OdooHandler(object):
    parent_map = {}
    contact_category_map = {}
    
    def __init__(self, opts):
        self.opts = opts
        print("host: %s, port: %s" % (opts.host, opts.port))
        odoo = ODOO(host=opts.host, port=opts.port)
        print(
            "dbname: %s, user: %s, password : %s"
            % (opts.dbname, opts.user, opts.password)
        )
        odoo.login(db=opts.dbname, login=opts.user, password=opts.password)
        self.odoo = odoo
        
        print("host: %s, port: %s" % (opts.host, opts.port_2))
        odoo_2 = ODOO(host=opts.host, port=opts.port_2)
        print(
            "dbname: %s, user: %s, password : %s"
            % (opts.dbname_2, opts.user, opts.password)
        )
        odoo_2.login(db=opts.dbname_2, login=opts.user, password=opts.password)
        self.odoo_2 = odoo_2
        #self.ail = odoo.env["account.invoice.line"]
        #self.pt = odoo.env["product.template"]
        #self.mprods = self.pt.browse(self.pt.search([("id", "in", (5, 6, 7))]))
        #self.ai = odoo.env["account.invoice"]

    def create_and_map_contact_category(self):
        contact_category_ids = self.odoo.env['res.partner.category'].search([])
        contact_categories = self.odoo.env['res.partner.category'].browse(contact_category_ids)
        for contact_category in contact_categories:
            exist_new_ids = self.odoo_2.env['res.partner.category'].search([('name', '=', contact_category.name)])
            if exist_new_ids:
                self.contact_category_map[contact_category.id] = exist_new_ids[0]
            else:
                new_id = self.odoo_2.env['res.partner.category'].create({'name' : contact_category.name})
                self.contact_category_map[contact_category.id] = new_id
        
    def _create_contact(self, contact):
        # first look up if it exists
        cp_fields = [
            'city',
            'commercial_company_name',
            'company_type',
            'contact_address',
            #'create_date',
            'is_customer',
            'display_name',
            'email',
            #'fax',
            'invoice_warn',
            'is_company',
            'lang',
            'lastname',
            'name',
            #'notify_email',
            #'partner_share',
            'phone',
            'street',
            'type',
            'tz',
            'tz_offset',
            'website',
            'website_url',
            'zip',
            #'image_medium',
            #'image',
            #'image_small',  
        ]
        Contact_O = self.odoo_2.env['res.partner']
        if contact.email:
            found = Contact_O.search([('email', '=', contact.email)])
            if found:
                return found[0]
        else:
            # we look for lastname, firstname, city, zip
            domain = [
                ('lastname', '=', contact.lastname),
                ('firstname', '=', contact.firstname),
                ('city', '=', contact.city),
                ('zip', '=', contact.zip),
            ]
            found = Contact_O.search([('email', '=', domain)])
            if found:
                return found[0]
        # not found, we construct entry
        data = {}
        for col in contact._columns:
            if col not in cp_fields:
                continue
            if col in ['parent_id', 'category_id', 'write_uid', 'support_ticket_string']:
                pass #lookitup
            v = getattr(contact, col)
            if v:
                data[col] = v
        Contact_O.create(data)
        return new_id
    

    def create_and_map_company(self, parent):
        new_id = self._create_contact(parent)

    def move_parents(self):
        contact_ids = self.odoo.env['res.partner'].search([('parent_id','!=', False)])
        
        for contact_id in contact_ids:
            parent = self.odoo.env['res.partner'].browse([contact_id]).parent_id
            print(parent.name)
            self.create_and_map_company(parent)


def main(opts):
    handler = OdooHandler(opts)
    handler.create_and_map_contact_category()
    handler.move_parents()


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
        "-p2",
        "--port_2",
        action="store",
        dest="port_2",
        default=8070,
        help="define port default 8070",
    )

    parser.add_argument(
        "-d",
        "--dbname",
        action="store",
        dest="dbname",
        default="redo2oo",
        help="define dbname default 'redo2oo'",
    )

    parser.add_argument(
        "-d2",
        "--dbname2",
        action="store",
        dest="dbname_2",
        default="redo2oo13",
        help="define dbname default 'redo2oo13'",
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

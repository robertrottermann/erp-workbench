# -*- encoding: utf-8 -*-
from odoorpc import ODOO
from argparse import ArgumentParser
import copy
from datetime import date, timedelta
from bs4 import BeautifulSoup
import re

"""
Problems:
  how to write images
  we have to create non stadard groups beforehand
  create companies
  create users
  contact-types hierarchy ..
"""

class OdooHandler(object):
    _contact_id_map = {}
    _contact_category_map = {}
    _processed = {}
    _odoo = None
    _odoo_2 = None
    
    def __init__(self, opts):
        self.opts = opts
        
        # open and log in to source odoo
        print("host: %s, port: %s" % (opts.host, opts.port))
        try:
            odoo = ODOO(host=opts.host, port=opts.port)
        except Exception as e:
            print("odoo seems not to run:host: %s, port: %s" % (opts.host, opts.port))
            return
        print(
            "dbname: %s, user: %s, password : %s"
            % (opts.dbname, opts.user, opts.password)
        )
        try:
            odoo.login(db=opts.dbname, login=opts.user, password=opts.password)
        except Exception as e:
            print(
                "could not login to source: dbname: %s, user: %s, password : %s"
                % (opts.dbname, opts.user, opts.password)
            )
            return
        self._odoo = odoo

        # open and log in to target odoo
        print("host: %s, port: %s" % (opts.host, opts.port_2))
        try:            
            odoo_2 = ODOO(host=opts.host, port=opts.port_2)
        except Exception as e:
            print("target odoo seems not to run:host: %s, port: %s" % (opts.host, opts.port_2))
            return
            
        print(
            "dbname: %s, user: %s, password : %s"
            % (opts.dbname_2, opts.user, opts.password)
        )
        try:
            odoo_2.login(db=opts.dbname_2, login=opts.user, password=opts.password)
        except Exception as e:
            print(
                "could not login to target odoo: dbname: %s, user: %s, password : %s"
                % (opts.dbname_2, opts.user, opts.password)
            )
            return
            
        self._odoo_2 = odoo_2
        #self.ail = odoo.env["account.invoice.line"]
        #self.pt = odoo.env["product.template"]
        #self.mprods = self.pt.browse(self.pt.search([("id", "in", (5, 6, 7))]))
        #self.ai = odoo.env["account.invoice"]

    def create_and_map_contact_category(self):
        if not self._odoo:
            return
        contact_category_ids = self._odoo.env['res.partner.category'].search([])
        contact_categories = self._odoo.env['res.partner.category'].browse(contact_category_ids)
        for contact_category in contact_categories:
            exist_new_ids = self._odoo_2.env['res.partner.category'].search([('name', '=', contact_category.name)])
            if exist_new_ids:
                self._contact_category_map[contact_category.id] = exist_new_ids[0]
            else:
                new_id = self._odoo_2.env['res.partner.category'].create({'name' : contact_category.name})
                self._contact_category_map[contact_category.id] = new_id

    def _create_contact(self, contact):
        """ either create new contact on parent or return its id when allready processed

        Args:
            contact (v9 contact item): v9 contact item

        Returns:
            int: id of the v13 contact item
        """
        # if that contact has already been process, take short cut
        if self._processed.get(contact.id):
            return self._processed.get(contact.id)
        # first look up if it exists
        cp_fields = [
            'city',
            'commercial_company_name',
            'company_type',
            'contact_address',
            'create_date',
            'date',
            'write_date',
            'is_customer',
            'display_name',
            'email',
            #'fax',
            'invoice_warn',
            'is_company',
            'lang',
            'firstname',
            'lastname',
            'name',
            #'notify_email',
            #'partner_share',
            'phone',
            'parent_id',
            'street',
            'type',
            'tz',
            'tz_offset',
            'website',
            'website_url',
            'zip',
            #'image_medium',
            'image',
            #'image_small',
        ]
        Contact_O = self._odoo_2.env['res.partner']
        if contact.email:
            found = Contact_O.search([('email', '=', contact.email), ('is_company', '=', contact.is_company)])
            if found:
                ret_val = found[0]
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
                ret_val = found[0]
        if not found:
            # not found, we construct entry
            data = {}
            for col in contact._columns:
                if col not in cp_fields:
                    continue
                v = getattr(contact, col)
                if v: # dont bother for empty fields
                    new_col = col
                    if col in ['date', 'write_date', 'create_date']:
                        v = str(v) # should probably be a bit more elaborate
                    if col in ['parent_id', 'category_id', 'write_uid']:
                        # check if parent was already processed, if not call create_and_map_contact recursively
                        if not self._contact_id_map.get(v.id):
                            create_and_map_contact(v)
                        # now it must exist
                        v = self._contact_id_map[v.id]
                    if col in ['image']:
                        new_col = 'image_1920'
                    data[new_col] = v
            ret_val = Contact_O.create(data) # create new_id
        # remember that we processed this entry, so we do not process it again
        self._processed[contact.id] = ret_val
        return ret_val

    def create_and_map_contact(self, contact):
        """create a copy of contact on target, add new id to map

        Args:
            contact (v9 contact object): v9 contact object
        """
        if not contact:
            return
        new_id = self._create_contact(contact)
        self._contact_id_map[contact.id] = new_id

    def create_contacts_on_target(self):
        """copy contacts from v9 source to v13 target
        """
        if not self._odoo:
            return
        contact_ids = self._odoo.env['res.partner'].search([])

        for contact_id in contact_ids:
            partner = self._odoo.env['res.partner'].browse([contact_id])
            parent = partner.parent_id
            if parent:
                print(parent.name, partner.name)
                self.create_and_map_contact(parent)
            else:
                print('--', partner.name)
            self.create_and_map_contact(partner)

    def _link_tag(self, odoo, partner_ids, tag_id):
        """link a tag to a contact

        Arguments:
            odoo: {odoo object} -- the odoo to use to write to
            record {odoo record} -- the record we want to link to the tag
            tag_ids {list of integers} -- the id of the tag we want the contact to link to,
        """
        if not partner_ids:
            return
        model = odoo.env["res.partner.category"]
        domain = [("id", "=", tag_id)]
        records = model.search(domain)
        tag = model.browse(records)
        existing = [p.id for p in tag.partner_ids]
        tag.write({"partner_ids": [(6, 0, existing + partner_ids)]})


    def link_contact_to_contacts_types(self):
        """
        after we have created all contact categories and all contacts on the target
        we loop trough the old categories and get the contact ids that where linked to them
        company_id = fields.Many2one(
            string='Company',
            comodel_name='res.company',
            required=True,
            default=lambda self: self.env.user.company_id
        )
        If we find such ids, we find the new category id, and link mapped partner ids to it
        """
        if not self._odoo:
            return
        old_Cat = self._odoo.env['res.partner.category']
        new_Cat = self._odoo_2.env['res.partner.category']
        for old_cat_id, new_cat_id in self._contact_category_map.items():
            old_cat = old_Cat.browse([old_cat_id])
            partner_ids = old_cat.partner_ids
            if partner_ids:
                mapped = []
                for partner_id in partner_ids:
                    mapped.append(self._contact_id_map[partner_id.id]) # die it it is not there
                self._link_tag(self._odoo_2, mapped, new_cat_id)



def main(opts):
    handler = OdooHandler(opts)
    if handler and handler._odoo and handler._odoo_2:
        handler.create_and_map_contact_category()
        # make sure we have all parents before we create a contact, so we can link them
        # would we better do that recursively when we create a contact??
        #handler.create_contacts_on_target(get_parents=True)
        handler.create_contacts_on_target()
        handler.link_contact_to_contacts_types()


if __name__ == "__main__":
    usage = "move_data_to_new_odoo.py -h for help on usage"
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

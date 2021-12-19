# -*- encoding: utf-8 -*-
from odoorpc import ODOO
from argparse import ArgumentParser
import copy
from datetime import date, timedelta
from bs4 import BeautifulSoup
import re

"""
from sshtunnel import SSHTunnelForwarder
import odoorpc

server = SSHTunnelForwarder(
     'testmachines',
     ssh_username="root",
#    ssh_password="secret",
    remote_bind_address=('172.18.0.2', 8069)
)


server.start()
odoo = odoorpc.ODOO('localhost', port=server.local_bind_port, timeout=1200)
odoo.login('december_03', 'admin', 'admin')
module_obj = odoo.env["ir.module.module"]
mlist = module_obj.search([("application", "=", True)])
for m in mlist:
    print(m)
print(server.local_bind_port)  # show assigned local port
# work with `SECRET SERVICE` through `server.local_bind_port`.

server.stop()
"""

"""
Problems:
  how to write images
  we have to create non stadard groups beforehand
  create companies
  create users
  contact-types hierarchy ..


preparation:
switch to odoo14:
    redo2oo14w
    bin/odoo

switch to odoo15
    redodoo15w
    bin/odoo -p 8070

python move_data_to_new_odoo.py    -H2 localhost -p2 8070 -d redo2oo14 -d2 redodoo15 {-lb}
-H red14 -p 9060 -d redo2oo -pw XHYadKJA9ZGzZH3t -H2 localhost -p2 8069 -d2 redo2oo14 -pw2 admin -lb

-H red14 -p 9060 -d redo2oo -pw XHYadKJA9ZGzZH3t -H2 localhost -p2 8070 -d2 redodoo15 -pw2 admin -lb

-H alice2 -p 8100 -d breitschtraeff10 -pw BreitschTraeffOnFrieda -H2 breit15 -p2 9005 -d2 breitsch15test -pw2 admin -lb

-H localhost -p 8100 -d breitschtraeff10 -pw BreitschTraeffOnFrieda -H2 breit15 -p2 9005 -d2 breitsch15test -pw2 admin -st
-H localhost -p 8100 -d  red_backup -pw admin -H2 breit15 -p2 9005 -d2 breitsch15test -pw2 admin -st -IP 172.24.0.2
-H localhost -p 9060 -d red_backup -u admin -pw admin -H2 localhost -p2 9005 -d2 breitsch15test -pw2 admin -IP 172.24.0.2 -IP_2 172.21.0.3 -ussh root -st
python move_data_to_new_odoo.py \
    -H localhost \       # source host
    -p 9060 \            # source port ?? what for
    -d red_backup \      # source database
    -u admin \           # source user
    -pw admin \          # source password
    -H2 localhost \      # target host
    -p2 9005 \           # target port ?? what for
    -d2 breitsch15test \ # target db
    -pw2 admin \         # target user
    -IP 172.24.0.2 \     # IP to use on source docker
    -IP_2 172.21.0.3 \   # IP to use on target docker
    -ussh root \         # what ssh user to use to login on both source and target server
    -st                  # use ssh tunnel



1. install partner-firstname
2. install de_CH
3. install swiss book keeping

sale_management
account
crm
website
project
hr
base_accounting_kit
mail
contacts
calendar
website_blog
"""

class OdooHandler(object):
    _contact_id_map = {}
    _contact_category_map = {}
    _processed = {}
    _odoo = None
    _odoo_2 = None

    def _get_tunnel(self, url, username, pw, ipaddr, port=8069,):
        #'testmachines', # url
        #ssh_username="root", # username
    ##    ssh_password="secret", # pw
        #remote_bind_address=(
            #'172.18.0.2', # ipaddr
            #8069 # port
        #)
        try:
            from sshtunnel import SSHTunnelForwarder
        except ImportError:
            print(hlp_msg)
        server = SSHTunnelForwarder(
            url,
            ssh_username = username,
        #    ssh_password="secret", # pw
            remote_bind_address=(
                ipaddr,
                port
            )
        )
        server.start()
        return server

    def __init__(self, opts):
        self.opts = opts

        # open and log in to source odoo
        host = opts.host
        port = opts.port
        dbname = opts.dbname
        user = opts.user
        password = opts.password
        server = None
        if opts.sshtunnel:
            server = self._get_tunnel(host, opts.ssh_user, password, opts.ip_address)
            #server = self._get_tunnel(opts.host, 'root', opts.password, opts.ip_address)
            port = server.local_bind_port
            print("host: %s, port: %s" % (host, port))
        else:
            print("host: %s, port: %s" % (host, port))
        try:
            odoo = ODOO(host=opts.host, port=port)
        except Exception as e:
            print("odoo seems not to run:host: %s, port: %s" % (host, port))
            return
        print(
            "dbname: %s, user: %s, password : %s"
            % (dbname, user, password)
        )
        try:
            odoo.login(db=dbname, login=user, password=password)
        except Exception as e:
            print(
                "could not login to source: dbname: %s, user: %s, password : %s"
                % (dbname, user, password)
            )
            return
        self._odoo = odoo

        # open and log in to target odoo
        host_2 = opts.host_2
        port_2 = opts.port_2
        dbname_2 = opts.dbname_2
        user_2 = opts.user_2
        password_2 = opts.password_2
        server = None
        if opts.sshtunnel:
            server = self._get_tunnel(host_2, opts.ssh_user, password_2, opts.ip_address_2)
            #server = self._get_tunnel(opts.host, 'root', opts.password, opts.ip_address)
            port_2 = server.local_bind_port
        print("host: %s, port: %s" % (host_2, port_2))
        try:
            odoo_2 = ODOO(host=host_2, port=port_2)
        except Exception as e:
            print("target odoo seems not to run:host: %s, port: %s" % (host_2, port_2))
            return

        print(
            "dbname: %s, user: %s, password : %s"
            % (dbname_2, user_2, password_2)
        )
        try:
            odoo_2.login(db=dbname_2, login=user_2, password=password_2)
        except Exception as e:
            print(
                "could not login to target odoo: dbname: %s, user: %s, password : %s"
                % (dbname_2, user_2, password_2)
            )
            return

        self._odoo_2 = odoo_2
        #self.ail = odoo.env["account.invoice.line"]
        #self.pt = odoo.env["product.template"]
        #self.mprods = self.pt.browse(self.pt.search([("id", "in", (5, 6, 7))]))
        #self.ai = odoo.env["account.invoice"]

    def handle_companies(self):
        if not self._odoo:
            return
        COMPANY_FIELDS = [
            'name',
            #'parent_id',
            #'child_ids',
            #'partner_id',
            'logo',
            'logo_web',
            #'currency_id',
            #'user_ids',
            'street',
            'street2',
            'zip',
            'city',
            #'state_id',
            #'bank_ids',
            'email',
            'phone',
            'website',
            'favicon',
            'primary_color',
            'secondary_color',
            'qr_code',
        ]
        #companies on source odoo
        companys_os = self._odoo.env['res.company']
        company_ids = companys_os.search([])
        company_s = companys_os.browse(company_ids)

        #companies on source odoo
        companys_ot = self._odoo_2.env['res.company']
        company_idt = companys_ot.search([])
        company_t = companys_ot.browse(company_idt)
        # now we copy / create companies
        for company in company_s:
            cp_id = company.id
            cp_values = {}
            for k in COMPANY_FIELDS:
                v = company[k]
                if v:
                    cp_values[k] = v
            # does company exist on the target
            target_company = companys_ot.search([('id', '=', cp_id)])
            if target_company:
                res = companys_ot.browse(target_company).write(cp_values)
            else:
                res = target_company.create(cp_values)


    def install_odoo_modules(self):
        module_obj = self.get_module_obj()


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
            #'website_url',
            'zip',
            #'image_medium',
            'image',
            #'image_small',
        ]
        Contact_O = self._odoo_2.env['res.partner']
        # we do not deal with partner ids < 4
        if contact.id < 4:
            return
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
            found = Contact_O.search(domain)
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
        # we do not deal with partner ids < 4
        if contact.id < 4:
            return
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

    def list_bank_accounts(self):
        #bank mapper dic maps source bank_ids to target bank_ids
        self.bank_mapper_dic = {}
        #bankaccounts mapper dic maps source bankaccount_ids to target bankaccount_ids
        self.bankaccount_mapper_dic = {}

        #banks on source odoo
        banks_os = self._odoo.env['res.bank']
        b_ids_s = banks_os.search([])
        banks_s = banks_os.browse(b_ids_s)
        bankaccounts_os = self._odoo.env['res.partner.bank']
        bankacc_ids_s = bankaccounts_os.search([])
        bank_accs_s = bankaccounts_os.browse(bankacc_ids_s)

        #banks on target odoo
        banks_ot = self._odoo_2.env['res.bank']
        b_ids_t = banks_ot.search([])
        banks_t = banks_ot.browse(b_ids_t)
        bankaccounts_ot = self._odoo_2.env['res.partner.bank']
        bankacc_ids_t = bankaccounts_ot.search([])
        bank_accs_t = bankaccounts_ot.browse(bankacc_ids_t)

        # loop trough the source banks, make sure they are in the target, and map id
        # we assume that bic and zip is a unique key
        bank_values = [
            'name',
            'street',
            'street2',
            'zip',
            'city',
            'state',
            'country',
            'email',
            'phone',
            'active',
            'bic',
            'display_name',
            #'create_uid',
            #'create_date',
            #'write_uid',
            #'write_date',
        ]
        account_values = [
            'active',
            'acc_type',
            'acc_number',
            'sanitized_acc_number',
            'acc_holder_name',
            #'partner_id',
            'bank_id',
            'bank_name',
            'bank_bic',
            'sequence',
            #'currency_id',
            #'company_id',
            #'journal_id',
            'l10n_ch_postal',
            'l10n_ch_isr_subscription_chf',
            'l10n_ch_isr_subscription_eur',
            'l10n_ch_show_subscription',
            'l10n_ch_qr_iban',
            #'display_name',
            #'create_uid',
            #'create_date',
            #'write_uid',
            #'write_date',
        ]
        # make sure we have all the banks
        for bank in banks_s:
            b_id = bank.id
            b_name = bank.name
            b_bic = bank.bic
            b_zip = bank.zip
            # do we have the target bank?
            if not b_zip:
                found_t_b = banks_ot.search([('name', '=', b_name), ('bic', '=', b_bic)])
            else:
                found_t_b = banks_ot.search([('zip', '=', b_zip), ('bic', '=', b_bic)])
            if not found_t_b:
                # sourc bank does not exist on target
                vals = {}
                for k in bank_values:
                    v = bank[k]
                    if v:
                        vals[k] = str(v)
                new_id = banks_ot.create(vals)
                self.bank_mapper_dic[b_id] = (new_id, b_name)
            else:
                self.bank_mapper_dic[b_id] = (found_t_b[0], b_name)

        # now make sure we have all the accounts
        for account in bank_accs_s:
            acc_id = account.id
            b_id = account.bank_id.id
            b_name = account.bank_name
            b_bic = account.bank_bic
            qr_iban = account.l10n_ch_qr_iban
            acc_number = account.acc_number
            # do we have the target bank?
            #found_t_acc = bankaccounts_ot.search([('l10n_ch_qr_iban', '=', qr_iban)])
            found_t_acc = bankaccounts_ot.search([('acc_number', '=', acc_number)])
            if not found_t_acc:
                # sourc bank does not exist on target
                vals = {}
                for k in account_values:
                    v = account[k]
                    if v:
                        vals[k] = str(v)
                # map the acount bank to the correct bank
                vals['bank_id'] = self.bank_mapper_dic[b_id][0]
                vals['partner_id'] = 1
                new_id = bankaccounts_ot.create(vals)
                self.bankaccount_mapper_dic[acc_id] = (new_id, b_name)
            else:
                self.bankaccount_mapper_dic[acc_id] = (found_t_acc[0], b_name)





hlp_msg = """
    could not import sshtunnel
    please pip install sshtunnel
"""

def main(opts):
    if opts.sshtunnel:
        try:
            from sshtunnel import SSHTunnelForwarder
        except ImportError:
            print(hlp_msg)

    handler = OdooHandler(opts)
    if handler and handler._odoo and handler._odoo_2:
        if opts.listbanks:
            handler.list_bank_accounts()
        else:
            handler.handle_companies()
            # we need the bank-accounts to map them to the customers
            handler.list_bank_accounts()
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
        "-IP",
        "--ip_address",
        action="store",
        dest="ip_address",
        default="172.24.0.2",
        help="define source docker IP-Address default 172.24.0.2",
    )

    parser.add_argument(
        "-IP_2",
        "--ip_address_2",
        action="store",
        dest="ip_address_2",
        default="172.24.0.2",
        help="define target docker IP-Address default 172.24.0.2",
    )

    parser.add_argument(
        "-H2",
        "--host2",
        action="store",
        dest="host_2",
        default="159.69.211.196",
        help="define host default red14",
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
        default=9060,
        help="define port default 9060",
    )

    parser.add_argument(
        "-d",
        "--dbname",
        action="store",
        dest="dbname",
        default="redo2oo13",
        help="define dbname default 'redo2oo13'",
    )

    parser.add_argument(
        "-d2",
        "--dbname2",
        action="store",
        dest="dbname_2",
        default="redo2oo",
        help="define dbname default 'redo2oo'",
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
        "-ussh",
        "--ssh_user",
        action="store",
        dest="ssh_user",
        default="root",
        help="define sshuser (for both connections) default 'root'",
    )
    parser.add_argument(
        "-pw",
        "--password",
        action="store",
        dest="password",
        default="admin",
        help="define password default 'admin'",
    )
    parser.add_argument(
        "-u2",
        "--user2",
        action="store",
        dest="user_2",
        default="admin",
        help="define user default 'admin'",
    )
    parser.add_argument(
        "-pw2",
        "--password2",
        action="store",
        dest="password_2",
        default="admin",
        help="define password default 'admin'",
    )
    parser.add_argument(
        "-lb",
        "--list-banks",
        action="store_true",
        dest="listbanks",
        default=False,
        help="list bank accounts",
    )
    parser.add_argument(
        "-st",
        "--ssh-tunnel",
        action="store_true",
        dest="sshtunnel",
        default=False,
        help="use ssh-tunnel to access remote servers",
    )

    opts = parser.parse_args()
    main(opts)

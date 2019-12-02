# -*- encoding: utf-8 -*-
from odoorpc import ODOO
from argparse import ArgumentParser
import copy
from datetime import date, timedelta

# the following query is but a sample how to query the odoo database
# it could be called from pgamin or some other sql frontend
I_QUERY = """select pa.name, pt.name, pt.id, acl.price_unit, pa.* from account_invoice_line acl
	inner join product_product pp on pp.id = acl.product_id
	inner join product_template pt on pp.product_tmpl_id = pt.id
	inner join res_partner pa on pa.id = acl.partner_id
	where pt.id in (5,6,7)
	order by pt.id, pa.name
    """

# VALS represents a dictionary as it is passed by odoo
# when creating a new invoice
# just fill in values appropriately before passing it to the
# create method
VALS = {
    u"account_id": 6,
    u"comment": False,
    u"company_id": 1,
    u"currency_id": 6,
    u"date_due": u"2018-04-20",
    u"date_invoice": u"2018-04-05",
    u"fiscal_position_id": False,
    u"invoice_line_ids": [
        [
            0,
            False,
            {
                u"account_analytic_id": False,
                u"account_id": 103,
                u"analytic_tag_ids": [],
                u"discount": 0,
                u"invoice_line_tax_ids": [],
                u"layout_category_id": False,
                u"name": u"[familie] Familienmitglied",
                u"origin": False,
                u"price_unit": 60,
                u"product_id": 6,
                u"quantity": 1,
                u"sequence": 10,
                u"uom_id": 1,
            },
        ]
    ],
    u"journal_id": 1,
    u"message_follower_ids": False,
    u"message_ids": False,
    u"move_name": False,
    u"name": False,
    u"origin": False,
    u"partner_bank_id": 1,
    u"partner_id": 15,
    u"partner_shipping_id": 15,
    u"payment_mode_id": False,
    u"payment_term_id": 2,
    u"reference": False,
    u"reference_type": u"none",
    u"tax_line_ids": [],
    u"team_id": 1,
    u"transaction_id": False,
    u"user_id": 1,
}


class OdooHandler(object):
    def __init__(self, opts, odoo=None):
        self.opts = opts
        if not odoo:
            print("host: %s, port: %s" % (opts.host, opts.port))
            odoo = ODOO(host=opts.host, port=opts.port)
            print(
                "dbname: %s, user: %s, password : %s"
                % (opts.dbname, opts.user, opts.password)
            )
            odoo.login(db=opts.dbname, login=opts.user, password=opts.password)
        self.odoo = odoo
        self.ail = odoo.env["account.invoice.line"]
        self.pt = odoo.env["product.template"]
        self.mprods = self.pt.browse(self.pt.search([("id", "in", (5, 6, 7))]))
        self.ai = odoo.env["account.invoice"]

    def list_invoices(self):
        invoices = {}
        old_invoices = []
        for il in self.ail.browse(self.ail.search([])):
            # products with id's in (5,6,7) are the membership types I am interested in
            # they have been looked up manually
            if il.product_id.id in (5, 6, 7):
                ilist = invoices.get(il.name, set())
                ilist.update([il.partner_id])
                invoices[il.name] = ilist
                old_invoices.append(il)
        counter = 0
        for k, partners in invoices.items():
            for p in partners:
                counter += 1
                print("(%s) %s %s %s %s" % (counter, k, p.name, p.city, p.street))

        # today = date.today()
        processed = []
        for il in old_invoices:
            if il.partner_id.id in processed:
                continue
            processed.append(il.partner_id.id)
            # we want to create a new invoice
            v = copy.deepcopy(VALS)
            td = date.today().strftime("%Y-%m-%d")
            due = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
            v["date_invoice"] = td
            v["date_due"] = due
            v["partner_id"] = il.partner_id.id
            v["partner_shipping_id"] = il.partner_id.id
            _x, _y, invoice_line = v["invoice_line_ids"][0]
            invoice_line["name"] = il.name
            invoice_line["product_id"] = il.product_id.id
            invoice_line["price_unit"] = il.price_unit
            v["invoice_line_ids"] = [[_x, _y, invoice_line]]
            print("--->", self.ai.create(v))


def main(opts):
    handler = OdooHandler(opts)
    handler.list_invoices()


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
        default="breitschtraeff10",
        help="define dbname default 'breitschtraeff10'",
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

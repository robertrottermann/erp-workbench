# -*- encoding: utf-8 -*-
from odoorpc import ODOO
from argparse import ArgumentParser
import copy
from datetime import date, timedelta
from bs4 import BeautifulSoup
import re

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
        #self.ail = odoo.env["account.invoice.line"]
        #self.pt = odoo.env["product.template"]
        #self.mprods = self.pt.browse(self.pt.search([("id", "in", (5, 6, 7))]))
        #self.ai = odoo.env["account.invoice"]

    def action_execute(self):
        page_ids = self.odoo.env['cms.page'].search([('state','!=','draft')])
        
        for page_id in page_ids:
            page = self.odoo.env['cms.page'].browse(page_id)
            print(page)
            # if page:
            #     print(page.body)
            if page.body:
                html_data = page.body
                soup = BeautifulSoup(html_data,'lxml')
                for link in soup.findAll('a'):
                    print(link)
                    url = re.findall('/cms.media/',str(link))
                    if url:
                        orig_id = re.search('cms.media/(.+?)/', link['href'])
                        if orig_id:
                            print(orig_id.group(1))
                            if orig_id.group(1) != 'False':
                                media_id = self.odoo.env['cms.media'].search([('orig_id','=',int(orig_id.group(1)))])
                                media = self.odoo.env['cms.media'].browse(media_id)
                                old ='/'+str(orig_id.group(1))+'/'
                                new ='/'+str(media.id)+'/'

                                url_data1 = str(link['href']).replace(old,new,1)
                                link['href'] = url_data1
                                if 'data-mce-href' in link:
                                    url_data = str(link['data-mce-href']).replace(old, new, 1)
                                    link['data-mce-href'] = url_data
                    print(link)
                    html_data = str(soup)
                print(html_data)
                page.body = html_data


def main(opts):
    handler = OdooHandler(opts)
    handler.action_execute()


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
        help="define dbname default 'afbs13'",
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

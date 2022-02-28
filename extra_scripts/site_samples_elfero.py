# db into which to install site data
MY_DBNAME = "montag_nami"
# port to open
MY_PORT = "8069"
# host where to find odoo running
MY_HOST = "localhost"

# SITE_ADDONS are the modules that we get from odoo core
SITE_ADDONS = [
    "l10n_ch",
    "account",
    "hr_holidays",
    "industry_fsm",
    "mail",
    "documents",
    "purchase",
    "sign",
    "account_accountant",
    "calendar",
    "contacts",
    "helpdesk",
    "crm",
    "stock",
    "hr",
    "project",
    "sale_management",
    "timesheet_grid",
    "planning",
]
# OWN_ADDONS are the modules that we handle our selfs in some
# own (non odoo) repos
OWN_ADDONS = [
    # "contacts_enterprise",
]

USERS = {}
#     # "student": "Student",
#     # "student_re": "Student Reinscription",
#     # "tutor": "Mentor / Tutor",
#     # "dozent": "Assist / Dozent",
#     # "dekan": "Dekan",
#     # "mitarbeiter": "Mitarbeiter",
#     # "sekratariat": "Sekretariat Studieng.",
#     # "sk": "SK",
#     # "stzleiter": "STZ-Leiter",
#     # "manager": "Manager",
#     # "kstleiter": "KST-Leiter",
#     # "director": "Director",
#     # "facultymanager": "Faculty Manager",
#     # "group_fsch_kasse": "Barkasse",
# }

STAFF = {
    "alain-boss": {
        "login": "alain",
        "name": "Alain the Boss",
        # "groups": [
        #     # "odoobuild.group_odoobuild_administrator",
        #     "odoobuild.group_odoobuild_contract_manager",
        #     "odoobuild.group_odoobuild_location_manager",
        #     "base.group_system"
        # ],
    },
    "hugo-contract-manager": {
        "login": "contract-manager",
        "name": "Hugo ContractManager",
        # "groups": [
        #     "odoobuild.group_odoobuild_contract_manager"
        # ],
    },
    "barbara-location-manager": {
        "login": "location-manager",
        "name": "Barbara LocationManager",
        # "groups": [
        #     "odoobuild.group_odoobuild_location_manager"
        # ],
    },
    "susanne-the-worker": {
        "login": "susanne",
        "name": "Susanne The Worker",
        "groups": [
        ],
    },
    "bob-the-worker": {
        "login": "bob",
        "name": "Bob The Worker",
        "groups": [
        ],
    },
    "Fritz Supervisor": {
        "login": "fritz",
        "name": "Fritz Supervisor",
        "groups": [
        ],
    },
    "hans-servicetechniker": {
        "login": "hans",
        "name": "Hans Servicetechniker",
        "groups": [
        ],
    },
    "heidi-hvevengeneer": {
        "login": "heidi",
        "name": "Heidi HVECEngeneerr",
        "groups": [
        ],
    },
    "marc-demo": {
        "login": "demo",
        "name": "Marc Demo",
        "groups": [
        ],
    },
    "peter-zeichner": {
        "login": "peter",
        "name": "Peter Zeichner",
        "groups": [
        ],
    },
    "hanna-programmierin": {
        "login": "hanna",
        "name": "Hanna Programmierin",
        "groups": [
        ],
    },
}

GROUPS = {}
#     "Location Manager": "odoobuild.group_odoobuild_location_manager",
#     "Contract Manager": "odoobuild.group_odoobuild_contract_manager",
#     "Administrator": "odoobuild.group_odoobuild_administrator",
# }


CONTRACT_TYPE = """
ct = self.env['contract.type']
ct.search([])
contract.type(1,)
res = ct.search([])
res[0].name
'Heatinginstallation'
"""
CONTRACT_TYPES = [
    'Heatinginstallation-simple',
    'Electroinstallation-simple',
    'Energyoptimisation-simple',
    'Heatinginstallation',
    'Electroinstallation',
    'Energyoptimisation',
    'Kitchenrenovation-simple',
]
CONTRACTS = [
    {
        'contract_state': 'draft',
        'name': 'Kitchenrenovation',
        'partner_id': 12,
        'address_id': 9,
        'contract_name': 'Kitchenrenovation-simple',
        'user_id': 7,
        'date_deadline': '2021-11-16',
        'company_id': 1,
        'budget': 10000,
        'project_id': False,
        'location_ids': [],
        'notes': False,
        'documents': [[6, False, []]],
        'document_ids': [],
        'offer_template': False,
        'content': '<p><br></p>',
        'template_footer': False,
        'content_footer': '<p><br></p>',
        'message_follower_ids': [],
        'activity_ids': [],
        'message_ids': []
    },
    {
        'contract_state': 'draft',
        'name': 'Condominium-Mountainpark',
        'partner_id': 12,
        'address_id': 9,
        'contract_name': 1,
        'user_id': 7,
        'date_deadline': '2021-11-16',
        'company_id': 1,
        'budget': 10000,
        'project_id': False,
        'location_ids': [],
        'notes': False,
        'documents': [[6, False, []]],
        'document_ids': [],
        'offer_template': False,
        'content': '<p><br></p>',
        'template_footer': False,
        'content_footer': '<p><br></p>',
        'message_follower_ids': [],
        'activity_ids': [],
        'message_ids': []
    },
]
# companies [[id, [values]], ..]
COMPANIES = [
    [ 1,
{'name': 'Elfero AG',
 'street': 'Lindenmattstr. 9',
 'city': 'Meisterschwanden',
 'zip': '5616',
 'logo': 'iVBORw0KGgoAAAANSUhEUgAAAhcAAAB4CAYAAABB5NDuAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6MzIyNDREODYwMkQ4MTFFOTkzQ0JENEJEQjMwNDFEMDAiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6MzIyNDREODcwMkQ4MTFFOTkzQ0JENEJEQjMwNDFEMDAiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDozMjI0NEQ4NDAyRDgxMUU5OTNDQkQ0QkRCMzA0MUQwMCIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDozMjI0NEQ4NTAyRDgxMUU5OTNDQkQ0QkRCMzA0MUQwMCIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PryLu7QAABs5SURBVHja7J0HnFXV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',
 'phone': '056 667 11 44',
 'email': 'info@elfero.ch',
 'vat': 'UID: CHE-107.122.194',
 'website': 'www.elfero.ch'}
    ],
]
# contacts has valslist wit list of values
CONTACTS = [{'partner_gid': 0,
  'additional_info': False,
  'is_company': False,
  'active': True,
  'company_type': 'person',
  'name': 'Felix Kunde',
  'parent_id': False,
  'company_name': False,
  'type': 'contact',
  'street': 'Morgartenstr 3',
  'city': 'Luzern',
  'zip': '6003',
  'country_id': 43,
  'phone': '066 123 45 67',
  'email': 'felix@felix.ch',
  'website': False,
  'title': False,
#   'lang': 'de_CH',
  'child_ids': [],
  'property_stock_customer': 5,
  'property_stock_supplier': 4,
  'bank_ids': [],
  'property_account_receivable_id': 6,
  'property_account_payable_id': 70,
},
{'partner_gid': 0,
  'is_company': False,
  'active': True,
  'company_type': 'person',
  'name': 'Walter Käufer',
  'parent_id': False,
  'company_name': False,
  'type': 'contact',
  'street': 'Grubenweg 3',
  'street2': False,
  'city': 'Bern',
  'state_id': False,
  'zip': '3014',
  'country_id': 43,
  'vat': False,
  'function': False,
  'phone': '066 123 45 88',
  'mobile': False,
  'user_ids': [],
  'email': 'walter@@walter.ch',
#   'lang': 'de_CH',
  'category_id': [[6, False, []]],
  'child_ids': [],
  'property_account_receivable_id': 6,
  'property_account_payable_id': 70,
  'comment': '<p><br></p>',
  'message_ids': []},
]

LOCATIONS = [
    {'name': 'Kitchen',
      'user_id': 8,
      'date_deadline': '2021-11-16',
      'notes': 'Some Notes',
      'documents': [[6, False, []]],
      'color': 0,
      'related_contract_id': 'Kitchenrenovation' #3
    },
]
SUB_LOCATIONS = [
    {'name': 'SubKitchen',
      'date_deadline': '2021-11-09',
      'notes': False,
      'documents': [[6, False, []]],
      'color': 0,
      'state': 'draft',
      'related_location_id': 'Kitchen' #2
    }
]
TASK_TEMPLATE =  {
    'recurrence_id': False,
    'stage_id': 1, # whats that??
    'project_id': -1,
    'priority': '0',
    'name': 'New Task',
    'kanban_state': 'normal',
    'user_id': 2,
    'parent_id': False,
    'date_deadline': '2021-11-09',
    'recurring_task': False,
    'tag_ids': [[6, False, []]],
    'active': True,
    'contract_id': 4,
    'location_id': False,
    'sub_location_id': False,
    'sub_sub_location_id': False,
    'context_true_btn': True,
    'from_contract': True,
    'partner_email': 'alain-boss@test.ch',
    'partner_phone': False,
    'timesheet_product_id': 40,
    'non_allow_billable': False,
    'sale_order_id': False,
    'sale_line_id': False,
    'description': '<p>Das Muss gemacht werden</p>',
    'planned_hours': 0,
    # 'date_assign': datetime.datetime(2021, 11, 3, 11, 14, 38)
}
# TASKS
# a list of tasks an substask added to location Kitchen
TASKS = {
    'Preparation' : [
            'Selecting what kind of kitchen is desired',
            'Selecting possible suppliers',
            'Visiting the location',
            'Photos',
            'Recording the conditions on site',
            'Record demolition of old kitchen',
            'Discussion with customer',
            'What are the customers requirements for a solution',
            'What does the desired supplier have?',
            'Search supplier kitchen',
            'What services can be obtained from the supplier?'
        ],
    'Phase 1 Demolition' : [
            'Demolition team',
            'Demolition tools',
            'Removal of demolition material',
        ],
    'Phase 2 Preparation of kitchen area' : [
            'Team',
            'Work',
        ],
    'Phase 3 Delivery, installation kitchen' : [
            'Team',
            'Tools',
            'Resources'
        ],
    'Phase 4 Commissioning, testing' : [
            'Team',
            'Resources',
        ],
    'Phase 5 Final billing' : [],
    'Phase 6 Maintenance' : [],
}
# SUB_TASKS is not used
SUB_TASKS = [
    {'recurrence_id': False,
      'stage_id': False,
      'recurrence_update': 'this',
      'priority': '0',
      'name': 'New Task:Subtask',
      'kanban_state': 'normal',
      'project_id': 10,
      'user_id': 2,
      'parent_id': 34,
      'date_deadline': '2021-11-09',
      'recurring_task': False,
      'tag_ids': [[6, False, []]],
      'active': True,
      'partner_id': 45,
      'contract_id': False,
      'location_id': False,
      'sub_location_id': False,
      'sub_sub_location_id': False,
      'context_true_btn': False,
      'from_contract': True,
      'partner_email': 'alain-boss@test.ch',
      'partner_phone': False,
      'timesheet_product_id': 40,
      'non_allow_billable': False,
      'sale_order_id': False,
      'sale_line_id': False,
      'description': '<p>Neuer Subtask</p>',
      'planned_hours': 0,
      'timesheet_ids': [],
      'repeat_interval': 1,
      'repeat_unit': 'week',
      'repeat_on_month': 'date',
      'repeat_on_year': 'date',
      'repeat_day': False,
      'repeat_week': False,
      'repeat_weekday': False,
      'repeat_month': False,
      'mon': False,
      'tue': False,
      'wed': False,
      'thu': False,
      'fri': False,
      'sat': False,
      'sun': False,
      'repeat_type': 'forever',
      'repeat_until': '2021-11-10',
      'repeat_number': 1,
      'sequence': 10,
      'email_from': 'alain-boss@test.ch',
      'email_cc': False,
      'allowed_user_ids': [[6, False, []]],
      'child_ids': [],
      'company_id': 1,
      'displayed_image_id': False,
      'message_follower_ids': [],
      'activity_ids': [],
      'message_ids': [],
    #   'date_assign': datetime.datetime(2021, 11, 3, 11, 23, 28)
    }
]

BANK_ACOUNT = """
vals_list
[{'sequence': 10,
  'l10n_ch_show_subscription': True,
  'company_id': 1,
  'active': True,
  'acc_number': 'CH36 0630 0504 1158 1450 0',
  'bank_id': 4,
  'l10n_ch_isr_subscription_chf': False,
  'l10n_ch_postal': False,
  'l10n_ch_qr_iban': False,
  'partner_id': 1}]
"""
#account.account(170,)
A_LIST = [
1000,
2200,
2271,
2277,
3000,
5000,
5700,
5889,
9980 ,
]
ACCOUNT_ACCOUNT = [
    {
        'code': '1000',
        'name': 'Kasse A / Cash A',
        'currency_id': False,
        'deprecated': False,
        'user_type_id': 3,
        'reconcile': False,
        'tax_ids': [(6, 0, [])],
        'note': False,
        'company_id': 1,
        'tag_ids': [(6, 0, [])],
        'group_id': False,
        'asset_model': False,
        'create_asset': 'no'
    },
    {
        'code': '2200',
        'name': 'Umsatzsteuer / Sales tax',
        'currency_id': False,
        'deprecated': False,
        'user_type_id': 3,
        'reconcile': False,
        'tax_ids': [(6, 0, [])],
        'note': False,
        'company_id': 1,
        'tag_ids': [(6, 0, [])],
        'group_id': False,
        'asset_model': False,
        'create_asset': 'no'
    },
    {
        'code': '2271',
        'name': 'Kontokorrent AHV, IV, EO, ALV / Current account OASI, DI, EO (replacement of earnings), UI',
        'currency_id': False,
        'deprecated': False,
        'user_type_id': 3,
        'reconcile': False,
        'tax_ids': [(6, 0, [])],
        'note': False,
        'company_id': 1,
        'tag_ids': [(6, 0, [])],
        'group_id': False,
        'asset_model': False,
        'create_asset': 'no'
    },
    {
        'code': '2277',
        'name': 'Kontokorrent ander Steuern Vers. / Current account other',
        'currency_id': False,
        'deprecated': False,
        'user_type_id': 3,
        'reconcile': False,
        'tax_ids': [(6, 0, [])],
        'note': False,
        'company_id': 1,
        'tag_ids': [(6, 0, [])],
        'group_id': False,
        'asset_model': False,
        'create_asset': 'no'
    },
    {
        'code': '3000',
        'name': 'Bruttoerlöse Erzeugnis A / Gross revenues product A',
        'currency_id': False,
        'deprecated': False,
        'user_type_id': 3,
        'reconcile': False,
        'tax_ids': [(6, 0, [])],
        'note': False,
        'company_id': 1,
        'tag_ids': [(6, 0, [])],
        'group_id': False,
        'asset_model': False,
        'create_asset': 'no'
    },
    {
        'code': '5000',
        'name': 'Wages prod. / Löhne',
        'currency_id': False,
        'deprecated': False,
        'user_type_id': 3,
        'reconcile': False,
        'tax_ids': [(6, 0, [])],
        'note': False,
        'company_id': 1,
        'tag_ids': [(6, 0, [])],
        'group_id': False,
        'asset_model': False,
        'create_asset': 'no'
    },
    {
        'code': '5700',
        'name': 'AHV, IV, EO, ALV',
        'currency_id': False,
        'deprecated': False,
        'user_type_id': 3,
        'reconcile': False,
        'tax_ids': [(6, 0, [])],
        'note': False,
        'company_id': 1,
        'tag_ids': [(6, 0, [])],
        'group_id': False,
        'asset_model': False,
        'create_asset': 'no'
    },
    {
        'code': '5899',
        'name': 'Private shares Personnel expenses not found in kontenplan',
        'currency_id': False,
        'deprecated': False,
        'user_type_id': 3,
        'reconcile': False,
        'tax_ids': [(6, 0, [])],
        'note': False,
        'company_id': 1,
        'tag_ids': [(6, 0, [])],
        'group_id': False,
        'asset_model': False,
        'create_asset': 'no'
    },
    {
        'code': '9980',
        'name': 'Auxiliary account Durchlaufskonto Anlagen-Fibu',
        'currency_id': False,
        'deprecated': False,
        'user_type_id': 3,
        'reconcile': False,
        'tax_ids': [(6, 0, [])],
        'note': False,
        'company_id': 1,
        'tag_ids': [(6, 0, [])],
        'group_id': False,
        'asset_model': False,
        'create_asset': 'no'
    }
]
LANGUAGES = [] # like ["de_CH", "de_DE", "fr_CH"]
MAILHANDLERS = {
    'mail_outgoing' : {
        u"active": True,
        u"name": u"outgoing@test_site.ch",
        u"sequence": 10,
        u"smtp_debug": False,
        u"smtp_encryption": u"starttls",
        u"smtp_host": u"mail.redcor.ch",
        u"smtp_port": 25,
        u"smtp_user": u"tester@o2oo.ch",
    },
    'mail_incomming' : {
        u"active": True,
        u"attach": True,
        u"is_ssl": True,
        u"name": u"incomming@test_site",
        u"object_id": False,
        u"original": False,
        u"port": 993,
        u"priority": 5,
        # u'script': u'/mail/static/scripts/openerp_mailgate.py',
        u"server": u"mail.redcor.ch",
        u"state": "draft",
        u"server_type": u"imap",
        u"user": u"tester@o2oo.ch",
    }
}
LOCATIONS = []

X = """
        # make sure admin can create contracts
        #users_o = odoo.env["res.users"]
        #groups = [
            ## "odoobuild.group_odoobuild_administrator",
            #"odoobuild.group_odoobuild_contract_manager",
            #"odoobuild.group_odoobuild_location_manager",
        #]
        #for group_id in groups:
            #group = odoo.env.ref(group_id)
            #group.write({"users": [(4, 2)]}) # admin is userr 2 ??

        #ctypes = odoo.env['contract.type']
        #for ct in CONTRACT_TYPES:
            #if not ctypes.search([('name', '=', ct)]):
                #vals = {'name' : ct, 'hierarchy' : True}
                #if 'simple' in ct:
                    #vals['hierarchy'] = False
                #ctypes.create(vals)

        #projects = odoo.env['project.project']
        #contracts = odoo.env['contract.contract']
        #for cont in CONTRACTS:
            #if not contracts.search([('name', '=', cont['name'])]):
                ## check if contract_name (which is the contract type) should be looked up
                #ct = cont['contract_name']
                #if not isinstance(ct, int):
                    #found = ctypes.search([('name', '=', ct)])
                    #cont['contract_name'] = found[0]
                #contracts.create(cont)
        #locations = odoo.env['contract.location']
        #for loc in LOCATIONS:
            #if not locations.search([('name', '=', loc['name'])]):
                ## check if 'related_contract_id' is a string
                #cn = loc['related_contract_id']
                #if not isinstance(cn, int):
                    #found = contracts.search([('name', '=', cn)])
                    #loc['related_contract_id'] = found[0]
                #locations.create(loc)
        #project_id = projects.search([('name', '=', 'Kitchenrenovation')])[0]
        #tasks = odoo.env['project.task']
        #for task,subtasks in TASKS.items():
            ##
            ## If a task has a parent_id, it is a subtask
            ## if a task has any of
            ##   'location_id': 2,
            ##   'sub_location_id': False,
            ##   'sub_sub_location_id': False,
            ## it is assigned to such a location

            #
            ## get contractid of Kitchenrenovation
            #contract_id = contracts.search([('name', '=', 'Kitchenrenovation')])[0]
            #location_id = locations.search([('name', '=', 'Kitchen')])[0]
            #if not tasks.search([('name', '=', task)]):
                ## check if 'related_contract_id' is a string
                #task_dic = copy.deepcopy(TASK_TEMPLATE)
                #task_dic['name'] = task
                #task_dic['project_id'] = project_id
                #task_dic['contract_id'] = contract_id
                #task_dic['location_id'] = location_id
                #task_dic['date_deadline'] = str(datetime.datetime.now() + datetime.timedelta(days=30))
                #task_dic['date_assign'] = str(datetime.datetime.now())
                #result = tasks.create(task_dic)
                #task_dic['parent_id'] = result
                #for stask in subtasks:
                    #task_dic['name'] = stask
                    #result = tasks.create(task_dic)


"""
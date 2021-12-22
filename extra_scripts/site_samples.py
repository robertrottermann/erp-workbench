# db into which to install site data
MY_DBNAME = "odoo13"
# port to open
MY_PORT = "8069"
# host where to find odoo running
MY_HOST = "localhost"

# SITE_ADDONS are the modules that we get from odoo core
SITE_ADDONS = [
    "account_accountant",
    "account",
    "base",
    "board",
    "calendar    ",
    "contacts",
    "crm",
    "hr_attendance",
    "hr_expense",
    "hr_holidays",
    "hr_payroll",
    "hr",
    "l10n_ch",
    "mail",
    "mass_mailing",
    "mis_builder",
    "project",
    "stock",
    "survey",
    "website",
]
# OWN_ADDONS are the modules that we handle our selfs in some
# own (non odoo) repos
OWN_ADDONS = [
    "contacts_enterprise",
    "crm_sms",
    "fsch_accounting",
    "fsch_analytics",
    "fsch_customer",
    "fsch_execution",
    "fsch_mail",
    "fsch_sso",
    "fsch_survey_edudl",
    "fsch_visibility",
    "funid_accounting",
    "funid_budget",
    "funid_customer",
    "funid_evaluation",
    "funid_invoice_followup",
    "funid_mail",
    "funid_student",
    "funid_registration",
    "funid_report_base",
    "funid_reporting",
    "funid_teacher",
    "funid_ticketing",
    "funid_website",
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

STAFF = {}
#     "alain-boss": {
#         "login": "alain",
#         "name": "Alain the Boss",
#         "groups": [
#             # "odoobuild.group_odoobuild_administrator",
#             "odoobuild.group_odoobuild_contract_manager",
#             "odoobuild.group_odoobuild_location_manager",
#             "base.group_system"
#         ],
#     },
#     "hugo-contract-manager": {
#         "login": "contract-manager",
#         "name": "Hugo ContractManager",
#         "groups": [
#             "odoobuild.group_odoobuild_contract_manager"
#         ],
#     },
#     "barbara-location-manager": {
#         "login": "location-manager",
#         "name": "Barbara LocationManager",
#         "groups": [
#             "odoobuild.group_odoobuild_location_manager"
#         ],
#     },
#     "susanne-the-worker": {
#         "login": "susanne",
#         "name": "Susanne The Worker",
#         "groups": [
#         ],
#     },
#     "bob-the-worker": {
#         "login": "bob",
#         "name": "Bob The Worker",
#         "groups": [
#         ],
#     },
# }

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
    mail_outgoing : {
        u"active": True,
        u"name": u"mailhandler@afbs.ch",
        u"sequence": 10,
        u"smtp_debug": False,
        u"smtp_encryption": u"starttls",
        u"smtp_host": u"mail.redcor.ch",
        u"smtp_port": 25,
        u"smtp_user": u"mailhandler@o2oo.ch",
    },
    mail_incomming : {
        u"active": True,
        u"attach": True,
        u"is_ssl": True,
        u"name": u"mailhandler@afbs.ch",
        u"object_id": False,
        u"original": False,
        u"port": 993,
        u"priority": 5,
        # u'script': u'/mail/static/scripts/openerp_mailgate.py',
        u"server": u"mail.redcor.ch",
        u"state": "draft",
        u"server_type": u"imap",
        u"user": u"mailhandler@o2oo.ch",
    }
}
LOCATIONS = []

"""
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
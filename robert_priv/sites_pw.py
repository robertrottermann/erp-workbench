#!/usr/bin/python
# -*- encoding: utf-8 -*-
# global password: RedcorKmuOnFrieda$99

# Your personal key: ed9a644a89302a5367285c490c36d05f
# You can check the use of your key here: http://tel.search.ch/api/help.en.html

# Lisa : lwzVoEqsfb
SITES_PW = {
    'docker_hub' : {
        'docker_hub' : {
            'robertredcor' : {'docker_hub_pw' : 'Coco2Dil$DO'},
            'coobyhq' : {'docker_hub_pw' : 'CoobyIoAdmin?$83'},
        },
		"https://hub.docker.com/r/coobyhq/": {
			"auth": "CoobyIoAdmin?$83"
		},
		"https://hub.docker.com/r/robertredcor/": {
			"auth": "Coco2Dil$DO"
		}

    },
    
    "demo_global" : {
        'odoo_admin_pw' : 'demo_global$odoo_admin_pw',
        'email_pw_incomming' : 'demo_global$email_pw_incomming',
        'email_pw_outgoing' : 'demo_global$email_pw_outgoing',
    },
    "aerohrone" : {
        'odoo_admin_pw' : 'EpluspOnFrieda$99',
        'email_pw_incomming' : 'EpluspOnFrieda$99',
        'email_pw_outgoing' : '',
    },
    "afbs firebird" : {
        'explanation' : """
        Firebird has a special user named SYSDBA, which is the user that has
        access to all databases. SYSDBA can also create new databases and users.
        Because of this, it is necessary to secure SYSDBA with a password.              │
       │                                                                                                                                                                                                                               │
       │ The password is stored in /etc/firebird/2.5/SYSDBA.password
        (readable only by root). You may modify it there
        (don't forget to update the security database too, using the gsec utility),
         or you may use dpkg-reconfigure to   │
       │ update both.                                                                                                                                                                                                                  │
       │                                                                                                                                                                                                                               │
       │ If you don't enter a password, a random one will be used
        (and stored in SYSDBA.password).                                                                                                                                     │
       │                                                                                                                                                                                                                               │
       │ Password for SYSDBA:
        """,
        'pw' : 'coco2dil',
    },
    "afbs" : {
        'odoo_admin_pw' : 'AfbsDemo$77',
        'email_pw_incomming' : 'Mailhandler$99A',
        'email_pw_outgoing' : 'Mailhandler$99A',
        'info@afbs.ch' : 'Afbs$22',
        # kynesis
        'kinesys' : '195.48.80.83',
        'user'    : 'az',
        'pw'      : 'Welcome2016!',
        # elvis
        'dsn' : "'10.42.0.150:/Users/elvis/Documents/VAS.fdb', user='sysdba', password='masterkey'",
        # opensuse
        'az' : '3,14159',
        'root' : 'opensuse',
        'robert on susanne' : 'Coco2Dil$ROBI',
        'wuergler@afbs.ch' : 'RaoulW$21',
        "analytics" : {
            "type": "service_account",
            "project_id": "afbs-analytics",
            "private_key_id": "0f130c31c2b879cea42e23d4aeab5477ec66e696",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCZTo000czDzZqG\n3NVLiUJGp9LRifKiJIvk36ndRsARcZRsWVfPzdinGTbV7LUQADHwuVbTrnGVf5Kf\nDD0mgdOdTp5zoCAXMSk6B1lDHmjFAn+4XFfhjJCi+FQVhxkZobs5wT1HdyPrhIxs\nPaKIW/vizFX3xI6Ka05HgouIK0UyGzZOU4TTwA/CPPzJNgF58BQkD1Co4RDE+98h\nDgXS7jQai49iDXjJtJCm0cam0kgJiHuJFXoBA8Dr8E52ic9Psuh1DLrJhn6/0Y9f\nkybxJCEfSuvNXVRCs6DBGdti3NmUcu/YjnLcmrBw2614SrSYlHMAeRFRAd7g1tL+\nj/tNjgEZAgMBAAECggEAEOapCI6sjVWIWJ/V3+r05Icx5anYlumChqvltSBMol+s\nJjm/RYiC/wD3m6Pp3ia3WruEB/guS3Xx+xjFUQ50/t2g+ExJ3WStD9mpjI24rSd2\nXyPHCHWPqHfKBUmMidfbpSVZlRxcWGWXeYNd/LxvS3SNcbA4qqfjzFxm948VpM1R\nfqQ14yDAHdL2cAv9N46j2KN+Tcdkak4smI4ccMfSzpYycGV9qy2A7ojkv3LBk336\nZFSQrzM5KLgd0JluUz5OPieqQn/x52RIoScvL63vi+Ra0rTNpUOWfwkZSznIK4B3\nlU0eD2qFfDGaPyDV0Bbd/0OdCECfQK2AVvgL314qBQKBgQDMZcoYH0u6nuMCP0rM\nmfPNJQvtjFE8kntOdjtLT44YGWYPn4yMklPuErdviOgKsUcXwr9610UL9Q+EEeXp\nZAqRO/BbBgoeTEZoO91nDVAWjBX6KFMv3idEWVdAf9uQzGbKh/iDpTDfePpr8hb+\nMPeISuSAkzf+sfgmRt+PUWoPmwKBgQDAAsRvvXeVbYJKpr7oEsPs4aCslseFnl+U\nt1daSEO+GAAU1rzxb8erQhUxTFlj/iqTR2H4720g5NVKoi2FTr1w91nw7MHqoFLZ\nj+1v/pNVYRLC+lbFLuUp0i2rooPf5B90FumByCuHhtjXxIZg8bRw4zsxrj72WmzU\nUH72sEcvWwKBgQCGOwa4Rr015qhQTn5x1VzNyVmG/FJRRCVkRrLz51/6pZtoATCN\nFH+35mS/A5rXgsqcaRHUu1Cl5J727cYeOsvRyxoyvMmiUhce1sm0poKE/CRmr1rK\nIcuJ0F5DhnQMKKAMu7TRx4dMCyfyAf9lmYTF5eEgKw5n3jqH8J1agm3zpwKBgB6L\n0ihcofuZslKh+Fj/M0AqHN+YFSHCsj38dN8eA/jn5ItsJh7aw48RMkHnfYkU1D0d\n7A4oONo0zWHULx24Cxc/ooVbhPYIj2WhKgrZGyNIEC4ImWlBLp/amf1mG0ixB/f1\n9Sv6ZkJnR3P8BczCZwxWegJLUCTs+cdFDw27uXdlAoGAXlWcszJJQUXoQ+o9zbla\nKfbaQtgnnIaaFWfnX2+y7Ney7qwpy1GFFWYOQlAAYIo93cEFYYPLVegN5ZQ3Znwa\ndw9yLWs3Hn7r4Dj7UkepIbo6N/JpMXT5wV45VsiSZooK5FkmZSx/B75sCayK9Fj4\nHD6Rj5HXWtSPKOLBOsje3XU=\n-----END PRIVATE KEY-----\n",
            "client_email": "afbs-analytics@afbs-analytics.iam.gserviceaccount.com",
            "client_id": "115326092751413858325",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/afbs-analytics%40afbs-analytics.iam.gserviceaccount.com"
        },
        'api-key' : 'AIzaSyC2BdyV7d5AfHn5UT5jnhD1A-HTwdyvkvk',
        'afbs_analytics@redcor.ch' : 'AfbsAnalytics$99',
    },
    "afbsdemo" : {
        'odoo_admin_pw' : 'AfbsDemo$77',
        'email_pw_incomming' : 'AfbsDemo$77',
        'email_pw_outgoing' : 'AfbsDemo$77',
    },
    "afbstest" : {
        'odoo_admin_pw' : 'AfbsDemo$77',
        'email_pw_incomming' : 'Afbs$99Elsbeth16',
        'email_pw_outgoing' : 'Afbs$99Elsbeth16',
    },
    "afbschweiz" : {
        'odoo_admin_pw' : 'AfbsDemo$77',  # 'Afbs$99Elsbeth16',
        'email' : {
            '82.220.39.73' : { # elsbeth
                'email_pw_incomming' : 'Afbs$99Elsbeth16',
                'email_pw_outgoing' : 'Afbs$99Elsbeth16',
            },
            '195.48.80.84' : { # kinesys
                'email_pw_incomming' : '!Red$2017Cor',
                'email_pw_outgoing' : '',
            },

        }
    },
    'bahoum' : {
        'odoo_admin_pw' : 'BahoumOnLisa$99',
        'service@haushalt-electro.ch' : 'BaHouM$99',
        'bahoum@help2go.ch' : 'ElekTro$99',

    },
    'borg' : {
        'pw' : 'BorgHostname$99 -> hostname = hostname'
    },
    "breitschtraeff9" : {
        'odoo_admin_pw' : 'BreitschTraeffOnFrieda',
        'email_pw_incomming' : 'BreitschTraeffOnFrieda',
        'email_pw_outgoing' : 'BreitschTraeffOnFrieda',
        'robert@go2breitsch.ch' : 'robert$99',
        'ale site:Robert' : 'sept2017',
    },
    "breitschtraeff92" : {
        'odoo_admin_pw' : 'BreitschTraeffOnFrieda',
        'email_pw_incomming' : 'BreitschTraeffOnFrieda',
        'email_pw_outgoing' : 'BreitschTraeffOnFrieda',
        'robert@go2breitsch.ch' : 'robert$99',
    },
    "breitschtraeff10" : {
        'odoo_admin_pw' : 'BreitschTraeffOnFrieda',
        'email_pw_incomming' : 'BreitschTraeffOnFrieda',
        'email_pw_outgoing' : 'BreitschTraeffOnFrieda',
        'robert@go2breitsch.ch' : 'robert$99',
    },
    'brun-del-re' : {
        'host' : 'susanne',
        'port' : '8079/manage',
        'robert' : 'cocoalice'
    },
    'conrad' : {
        'robert@redcor.ch' : 'wie üblich',
    },
    'ccobysaas': {
        'odoo_admin_pw': 'HalloVelo%&2',
    },
    'docker': {
        'frieda' : """
            name:redcor
            email:docker@redcor.ch
            password on susanne: standard enhanced pw using Docker
            pw:schrecklise grünes tier alles klein $docker
        """,
    },
    "docmarolf" : {
        'odoo_admin_pw': 'DocMarolfOnFrieda$51',
        'email_pw_incomming' : '',
        'email_pw_outgoing' : '',
    },
    "dynadot" : {
        'username' : 'robert_redcor',
    },
    "ecassoc" : {
        'odoo_admin_pw' : 'EcAssocOnFrieda',
        'email_pw_incomming' : 'ecasincomming$99',
        'email_pw_outgoing' : 'ecassoc$99',
    },
    "eplusp" : {
        'odoo_admin_pw' : 'EpluspOnFrieda$99',
        'email_pw_incomming' : 'EpluspOnFrieda$99',
        'email_pw_outgoing' : '',
    },
    "eplusp11" : {
        'odoo_admin_pw' : 'EpluspOnFrieda$99',
        'email_settings': {
            'smtp_server'           : 'mail.redcor.ch',
            'email_server_incomming': 'bruno.cosandey@eplusp.ch',
            'email_user_incomming'  : 'managemail@eplusp.ch',
            'email_pw_incomming'    : 'EpluspOnFrieda$99',
            'email_userver_outgoing': 'mail.redcor.ch',
            'email_user_outgoing'   : 'managemail@eplusp.ch',
            'email_pw_outgoing'     : 'EpluspOnFrieda$99',
        },
    },
    "elfero" : {
        'odoo_admin_pw' : 'Br@1nt5c',
        'email_pw_incomming' : '',
        'email_pw_outgoing' : '',
        'elfero' : 'SiAG4E1f3r0!14',
        'linux root' : 'L1nux4E1f3r0!',
        'teamvier' : 'geeksscript17',
        'tv-id' : '677808247',
        'spezial' : 'MurDXrUAPbv3eDCLeLc1',
        'Das Windows-login ist W1llkommen, falls es ausloggen sollte.' : '',
    },
    'floodbridge' : {
        'floodbridge' : 'FlectaAtRedo2oo$21',
        # mail
        'support@floodbridge.org': 'SuperFlood$44',
    },
    'google' : {
        'redo2oo' : 'GoogleRedO2oo$99',
        'miciael@redcor.ch' : 'CRYE<2jb',
        'susanne@redcor.ch' : 'PaLoKa?2GO',
        'tatjana@redcor.ch' : '2MLyXj<R',
    },
    'hosttech' : {
        'login' : 'robert@redcor.ch',
        'pw' : 'wie üblich'
    },
    "harito" : {
        'odoo_admin_pw' : 'osho79Pune%Odoo',
        'email_pw_incomming' : 'osho79Pune%%',
        'email_pw_outgoing' : '',
    },
    'henriette' : {
        'hotmail' : 'Hotm450$99',
        '20N0076401' : 'Vali450$99' ,
        'klaymuehle@gmail.com' : 'klaymuehle$99',
        'skype (076 330 92 12)' : 'Skype450$99',
        'hk@redcor.ch' : 'Redcor450$99',
        'go2breitsch: hk@redcor.ch' : 'Brei450$99',
        'google-drive' : {'henrietteklay450@gmail.com: GoDr450$99'},
    },
    'hetzner' : {
        'Rottermann' : 'Red$NHetzPW$99',
    },
    'huawei' : {
        'pin1' : '8218',
        'pin2' : '9637',
        'puk1' : '61040116',
        'puk2' : '21205967',
        'pw' : '05959248',
        'admin' : 'wie üblich $HU',
        'ip' : '192.168.8.1',
    },
    'help2go' : {
         'admin' : 'tydd@Cohyp5'
    },
    'internic' : {
        'redcor' : 'standard mit IN usw usfort',
    },
    "kinesys" : {
        'ip' : '195.48.80.84',
        'root' : '$ub2017afbs!'
    },
    "leanbi" : {
        'email_pw_incomming' : 'Terry$99Brenda',
        'email_account_outconing' : 'leanbi@alice2.ch',
        'email_pw_outgoing' : 'NaduDuDelDu$99',
        'odoo_admin_pw' : 'Vw6FMVf2KBfBYyfB',
    },
    "o2oo" : {
        'fritz@o2oo.ch' : 'FritzO2oo',
        'mailhandler@o2oo.ch' : 'Mailhandler$99',
        'dump@o2oo.ch' : 'Dump$99',
    },
    "postgres" : {
        'alice2' : {
            '9.3:postgres' : 'RobiRo$99'
        },
    },
    "psytex" : {
        'admin@psytex.ch' : 'AdminPsy$99',
        'susanne.kappeler@psytex.ch' : 'PaLoKa?2PS',
        'mailhandler@psytex.ch' : 'PaPaLo$99',
        'odoo_admin_pw' : 'AdminPsy$99',
    },
    "nextcloud" : {
        'root' : 'coco2dil',
    },
    "tibhub" : {
        'odoo_admin_pw' : 'Terry$99Brenda',
        'email_pw_incomming' : 'Terry$99Brenda',
        'email_pw_outgoing' : 'Terry$99Brenda',
    },
    "rederpdemo" : {
        'odoo_admin_pw' : 'RederpOnFrieda$16',
        'email_pw_incomming' : 'HelpdeskErpdemo6670$ch',
        'email_pw_outgoing' : 'HelpdeskErpdemo6670$ch',
    },
    "redclean" : {
        'odoo_admin_pw' : 'RedClean$99X',
        'email_pw_incomming' : 'RedClean$99X',
        'email_pw_outgoing' : 'RedClean$99X',
    },
    "redcorkmu" : {
        'odoo_admin_pw' : 'RedcorKmuOnFrieda',
        'email_pw_incomming' : 'HelpdeskOnRedcorKmu$99',
        'email_pw_outgoing' : 'HelpdeskOnRedcorKmu$99',
        'michael' : 'Michi$99',
    },
    "redfsm" : {
        'odoo_admin_pw' : 'RedFsm$99X',
        'email_pw_incomming' : 'RedFsm$99X',
        'email_pw_outgoing' : 'RedFsm$99X',
    },
    "redo2oo" : {
        'email' : 'catchall@redo2oo.ch',
        'odoo_admin_pw' : 'Redo2ooOnAlice2',
        'email_pw_incomming' : 'Redo2ooOnAlice2$99',
        'email_pw_outgoing' : 'Redo2ooOnAlice2$99',
        'michael@redo2oo.ch' : 'Micha$99',
        'einkauf@redo2oo.ch' : 'PurchaseForUs$99',
        'google_account' : ('redo2ooklg@gmail.com', 'GoogleRedO2oo$99'),
        'google IAM' : {'google@redo2oo.ch' : 'GoogleRedO2oo$99'},
        'valiant' : {'vertragsnummer' : '20N0074914'},
        'froxlor alt' : 'coco2dil',
        'froxlor' : 'Coco2Dil$FRO',
    },
    "redo2oo11" : {
        'email' : 'catchall@redo2oo.ch',
        'odoo_admin_pw' : 'Redo2ooOnAlice2',
        'email_pw_incomming' : 'Redo2ooOnAlice2$99',
        'email_pw_outgoing' : 'Redo2ooOnAlice2$99',
        'michael@redo2oo.ch' : 'Micha$99',
        'einkauf@redo2oo.ch' : 'PurchaseForUs$99',
        'google_account' : ('redo2ooklg@gmail.com', 'GoogleRedO2oo$99'),
        'google IAM' : {'google@redo2oo.ch' : 'GoogleRedO2oo$99'},
        'valiant' : {'vertragsnummer' : '20N0074914'},
        'froxlor' : 'coco2dil',
    },
    "redo2oo_demo" : {
        'odoo_admin_pw' : 'RedDemo$99X',
        'email_account' : 'reddemo@redo2oo.ch',
        'email_pw_incomming' : 'RedDemo$99X',
        'email_pw_outgoing' : 'RedDemo$99X',
    },
    "redo2oom" : {
        'email' : 'helpdesk@redo2oo.ch',
        'odoo_admin_pw' : 'Redo2ooOnAlice2',
        'email_pw_incomming' : 'Redo2ooOnAlice2$99',
        'email_pw_outgoing' : 'Redo2ooOnAlice2$99',
    },
    'rottis$home' : {
        'rottis$home' : 'Rottis$2Home',
        'settings admin' : 'Rottis$2HomeAdmin',
    },
    'robert' : {
        'udemy' : 'coco2dil$99',
        'packt' : 'coco2dil$99R',
        'pkorg' : 'coco2dil$99PK'
    },
    'ruby' : {
        'https://rubygems.org/' : {'robert_the_greyt' : 'the usual ..'},
    },
    'six' : {
        'robert.rottermann' : 'the usual ..'
    },
    'susanne_mail' : {
        'susanne@redo2oo.ch' : 'PaLoKa?2RE',
        'susanne.kappeler.67@gmail.com' : 'SuKa1967',
        'telephon für wiederherstellung' : '079 222 42 07',
        'Adresse zur Kontowiederherstellung' : 'susanne@redo2oo.ch',
        'pin' : 1967,
        'apple id fuer susanne@redcor.ch' : 'PaLoKa?2RE',
        'Was war das erste Musikalbum, das du gekauft hast?' : 'abba',
        'Wie hiess dein erstes Haustier?' : 'naomi',
        # BFH
        'account' : 'LQYG',
        'pw' : 'SG4vt2M7',
        # login auch für VPN
        'kapps3' : 'PaLoKa?2BF',
        'valiant': '20N0036085',
        "CAS" : {
            "modul 18-19" : '1003932',
            'url' : 'https://moodle.bfh.ch/course/view.php?id=17121',
            "modul allgemeines" : 'allgemeines',
            'url' : 'https://moodle.bfh.ch/course/view.php?id=81',
        },
        "microsoft konto auf HP eingereichtet: code": "GP2CF-28RFZ-FW58H-2WJA5-K877U",
        'pin auf envy' : 1967,
    },
    'susanne.redcor.ch' : {
        'roundcube' : """<?php
                        ##
                        ## database access settings in php format
                        ## automatically generated from /etc/dbconfig-common/roundcube.conf
                        ## by /usr/sbin/dbconfig-generate-include
                        ## Sun, 05 Oct 2014 15:51:20 +0200
                        ##
                        ## by default this file is managed via ucf, so you shouldn't have to
                        ## worry about manual changes being silently discarded.  *however*,
                        ## you'll probably also want to edit the configuration file mentioned
                        ## above too.
                        ##
                        $dbuser='roundcube';
                        $dbpass='RoundcubeOnSusanne';
                        $basepath='';
                        $dbname='roundcube';
                        $dbserver='';
                        $dbport='';
                        $dbtype='mysql';

                    """,
        "mysql-root" : "MysqlOnSusanne",
    },
    "switchplus" : {
        '3479350' : 'wie üblich',
    },
    "tatjana" : {
        'tatjana@redo2oo.ch' : 'TatjanaH$99',
        'tatjana@redo2oo@gmail.com' : 'Alki2018Tan$'
    },
    "xchance" : {
        'odoo_admin_pw' : 'Xchance$99X',
        'email_account' : 'xchance@redo2oo.ch',
        'email_pw_incomming' : 'Xchance$99X',
        'email_pw_outgoing' : 'Xchance$99X',
    },
    'upc' : {
        'admin.44679' : 'wie immer'
    }
}

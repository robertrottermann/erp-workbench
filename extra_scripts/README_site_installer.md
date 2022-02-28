# Site installer
The site-installer "suite" includes 3 files:

## README_site_installer.md
This file ..

## site_samples.py
in this file we list the elements, we want to install
- MY_DBNAME
    The name of the database to deal with.
- MY_PORT
  The port to open
- MY_HOST
  on what host odoo is running
- SITE_ADDONS
  What odoo main modules should be installed
- OWN_ADDONS
  What OCA or self developed modules should be installed
- LANGUAGES
  What languages should be installed
- MAILHANDLERS
  What incomming and outgoing mail handler should be installed.
  The connectivity must be checked manually
- GROUPS
  What groups we will use (ins this necessary at all?)
  The groups then can be assigned to staff members.
  They are only available when the respective modules have been installed successfully
- USERS
  What users to create
- STAFF
  What employees to create and what groups to assign them
- ANY NUMBER OF OTHER OBJECTS like contracts
  You can add any number of other types with the respective data
  to the file.
  For every such object you need two methods in site_installer.py:
  - a property to read it (there are many samples)
  - a method to do the creation
  - a call of this method


## site_installer.py
This Script needs to be run in a virtual env. If not, it complains and tells you what modules sould be installed in tht environment.
It opens the definition file named with parameter -I (by default site_samples.py), and creates a connection to a running odoo as defined it the values found in it.
It then performs the following steps:

    if __name__ == "__main__":
        opts = parser.parse_args()
        installer = OdoobuildInstaller(opts)
        installer.get_odoo(verbose=True)
        installer.install_own_modules()
        installer.install_own_modules(what="own_addons")
        installer.install_mail_handler()
        installer.install_languages()
        installer.create_users()
        installer.install_objects()

What the methods do, should be clear by their names. Details you find in the respective methods.
After the site has been prepared, the method install_objects creates the requested objects by calling their creator methods in sequence.
To have any objects created, you have to edit the install_objects method accordingly.
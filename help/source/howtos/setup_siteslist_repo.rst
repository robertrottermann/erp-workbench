Create a remote sites-list repo
--------------------------------

You might want to share the list of sites managed by rp-workbench using
a remote repositoy.

THe list can be managed either locall, or on any remote git repository.
You define the urls to these repositories in the file::

    config/config.yaml

Each site is described like so::

    siteinfos:
        name_1:
            url_1
        name_2:
            url_2

Example::

    # sitesinfo_url:
    # sitesinfo_url is the url where git repositories can be found
    # in which the sites are maintained 
    siteinfos:
        localhost:
            'localhost'
        demo_sites:
            'https://gitlab.redcor.ch/open-source/demo_sites.git'

Setup a repository for the siteslist
************************************

You can have several sites lists.
Where thy are store in your erp-workbench is defined in your config/config.yaml::

  # sitesinfo_path:
  # Sites are defined in a sites description file
  # There exist local sites, which are not managed using a source
  # controll system (git), and gloabal sites which are managed with 
  # git and normaly describe sites that eventuall run on remote servers.
  # the sitesinfo_path points to a folder, where these site descriptions 
  # are kept in several subfolders
  # by default it is kept within the erp-workbench folder
  # %s(BASE_PATH)
  sitesinfo_path: '%(BASE_PATH)s/sites_list/'

it normally points to $WB/sites_list

In your config file you can add a list of urls where the lists are maintained::

  # sitesinfo_url:
  # sitesinfo_url is the url where the git repository can be found
  # with which the sites are maintained 
  #sitesinfo_url: 'ssh://git@gitlab.redcor.ch:10022/redcor_customers/sites_list.git'
  # sitesinfo_url:
  # sitesinfo_url is the url where the git repository can be found
  # with which the sites are maintained 
  siteinfos:
    localhost:
      sitesinfo_url: 'localhost'
    redo2oo:
      'ssh://git@gitlab.redcor.ch:/redcor_customers/sites_list.git'
    cooby:
      'git@gitlab.com:cooby/erp-workbench.git'

To add a new url proceed as follows:

  - add url in the above list like: 'git@gitlab.com:cooby/erp-workbench.git'
  - run erp-workbench with any command like: bin/ls  -> this will generate the site_list structure
  - change into the the newly  generated folder: cd sites_list/cooby
  - execute the following commands (assuming you use the above example)::

    cd INTO THE NEW FOLDER
    git init
    git remote add origin git@gitlab.com:cooby/erp-workbench.git
    touch .gitignore
    git add .gitignore sites_global
    git commit -m 'added coobytech'
    git push --set-upstream origin master
  

the git ignore file should have following content::

  **/*.pyc
  sites_local/*
  sites_pw.py
  __init__.py
  sites_global/__init__.py



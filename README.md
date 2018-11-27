# erp-workbench
an environment to create odoo sites
```
git clone https://github.com/robertrottermann/erp-workbench.git
cd erp-workbench/
```

install virtualenv:
-------------------

`cat install/virtualenv_wrapper.txt`

Preparation:
------------
```
    # install the virtualenv wrapper 
    # (see http://virtualenvwrapper.readthedocs.io/en/latest/install.html):
        pip install virtualenvwrapper
```

add the following instruction to .bashrc
```
    # ------------------ start workon stuff -------------------
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/projetcs
    source /usr/local/bin/virtualenvwrapper.sh
```
take care that the last line (source /usr/local/bin/virtualenvwrapper.sh) is correct.
It could be, that virtualenvwrapper.sh was installed to a different directory.

important:
make sure, that afther opening a new shell the following two conditions are met:
- no message after opening the shell like:
    /usr/local/bin/virtualenvwrapper.sh not found
- the command:
    which virtualenvwrapper.sh
    produces a valid result


create a virtualenv for erp-workbench
-------------------------------------
make sure you are in the folder into which you git cloned erp-workbench!

ececute the following commands:
```
    # create virtualenv for erp-workbench
    mkvirtualenv -a . -p python3 workbench
    # for convinience crete the following two links
    (cd bin; ln -s $(which python))
    (cd bin; ln -s $(which pip))
    # install all required python libraries
    bin/pip install -r install/requirements.txt
    # generate the help files
    (cd help; make html)
    # generate an alias to easily start the workbench
    (echo $'\n''alias  wb="workon workbench"' >> ~/.bash_aliases)
    # open the help files
    bin/help
```
After having executed the above commands and opened a new bash terminal
(you created a new alias, that is only active when loaded while opening a terminal)

the command:

`   wb`

will activate the workbench environment and cd into its main folder!

list existing site descriptions to force creation of config files
-----------------------------------------------------------------
```
wb # to start/set  erp-workbench
bin/c -ls   # list exising site descriptions
```
The following message will be displayed::

    --------------------------------------------------
    The structure of the config files have changed.
    please check /home/robert/erp-workbench/config/project.yaml if everything ist correct.
    --------------------------------------------------
and the command will terminate.
This is because no configuration files have existed yet, but have
been construced for you.
You have to restart your command, which then  will used the freshly created environment.

As a side effect, two new site descriptions have been created, and can be listed by repeating the above command:
```
bin/c -ls   # list exising site descriptions
```
now the two new site-descriptions are listed::
    demo_global
    demo_local (local)

To inspect them you can load any of them in the default editor, which is "code", by executing:
```
bin/e demo_global
```

If code is not installed, you can adapt what editor to use in::
    config/config.yaml

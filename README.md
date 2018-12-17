# erp-workbench
an environment to create odoo sites

Preparation:
------------
```
    # python-tk tcl8.6-dev tk8.6-dev
    # have postgres up and running
    sudo apt install -y postgresql postgresql-contrib

    #add yourself as postgres superuser to the database:
    sudo -u postgres psql -e --command "CREATE USER $USER WITH SUPERUSER PASSWORD 'admin'"

    # install os libraries
        sudo apt-get -y install build-essential libfreetype6-dev libjpeg8-dev liblcms2-dev libldap2-dev libsasl2-dev libssl-dev libffi-dev \
        libtiff5-dev libwebp-dev libxml2-dev libxslt1-dev node-less postgresql-server-dev* python-dev python3-dev python3-pip \
        zlib1g-dev postgresql-client python-virtualenv git vim npm nodejs libmysqlclient-dev \
        curl node-gyp

    # install the virtualenv wrapper 
    # (see http://virtualenvwrapper.readthedocs.io/en/latest/install.html):
        sudo pip install virtualenvwrapper
```

add the following lines to .bashrc by executing 
```
    echo "# ------------------ start workon stuff -------------------
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/projetcs
    source $(virtualenvwrapper.sh)" >> $HOME/.bashrc
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

clone the erp-workbench repo
----------------------------
```
git clone https://github.com/robertrottermann/erp-workbench.git
cd erp-workbench/
```

create a virtualenv for erp-workbench
-------------------------------------
make sure you are in the folder into which you git cloned erp-workbench!

ececute the following commands in a NEW bash window:
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

If want to use an oder editor than VS code or if it is not installed, you can adapt what editor to use in::
    
    config/config.yaml

On of the first elements you have to adapt, is to tell erp-workbench, in what repository to save the site-descriptions.
By default is done using localhost and without git.
Please generate and read the documentation on how to change it.


## step by step in a freshly installed ubuntu 18.04

as user root:
the package terminator is not strictly nessecary but very convinient for shekk junkies like me :)
It migth be possible, that the following list of libraries must be adapted to othe linux versions.

```
        sudo apt install -y terminator postgresql postgresql-contrib \
            build-essential libfreetype6-dev libjpeg8-dev liblcms2-dev libldap2-dev libsasl2-dev  libssl1.0-dev libffi-dev \
            libtiff5-dev libwebp-dev libxml2-dev libxslt1-dev node-less postgresql-server-dev* python-dev python3-dev \
            python-tk tcl8.6-dev tk8.6-dev zlib1g-dev postgresql-client python-virtualenv git vim npm nodejs libmysqlclient-dev \
            curl node-gyp python-pip python3-sphinx
```

als normal user:
### install and configure virtualenvwrapper

```
sudo pip install virtualenvwrapper
```
```
echo "
    # ------------------ start workon stuff -------------------
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/projetcs
    source $(which virtualenvwrapper.sh)
    " >> $HOME/.bashrc

```
test if this worked. 
```
workon
```
this should not provide any output at all

### clone erp-workbench

```
git clone https://github.com/robertrottermann/erp-workbench.git
```

### setup virtualenv an alias for erp-workbench

**IMPORTANT!** the following commands have to be executed in a **NEW** bash shell

```
    cd $HOME/erp-workbench
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

**BRAVO** you have installed erp-workbench, now lets configure it!

In an **NEW** bash-shell (*always when you alter the environment, the changes will only be active in a new window*) you can execute the command:
```
wb
```
this will activate the erp-workbench environment, and change to its main folder.




## Troubleshooting
### error running command wb

When after executing the command wb you get the message:
```
robert@lappi:~$ wb
ERROR: Environment 'workbench' does not exist. Create it with 'mkvirtualenv workbench'.
```

execute the following commands:

```
    cd $HOME/erp-workbench
    mkvirtualenv -a . -p python3 workbench
```

### command bin/help does not work

### could not import sites list
When executing a commmand like bin/c -ls
pruducing an error like
```
********************************************************************************
could not import sites list
```
then the easiest "solution" is to just remove the folder sites_list

```
rm -r sites_list/
# and then let erp-workbench recreate them
bin/c -ls
```


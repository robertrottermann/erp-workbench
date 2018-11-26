# erp-workbench
environment to creat odoo sites

git clone https://github.com/robertrottermann/erp-workbench.git
cd erp-workbench/

================================================================================
install virtualenv:
-------------------
cat install/virtualenv_wrapper.txt
Preparation:
------------
install the virtualenv wrapper (see http://virtualenvwrapper.readthedocs.io/en/latest/install.html):
    pip install virtualenvwrapper

add instructions the following instruction to .bashrc
then to add virtualenvwrapper when a shell is opened:

    # ------------------ start workon stuff -------------------
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/projetcs
    source /usr/local/bin/virtualenvwrapper.sh

take care that the last line (source /usr/local/bin/virtualenvwrapper.sh) is correct.
It could be, that virtualenvwrapper.sh was installed to a different directory.

important:
make sure, that afther opening a new shell the following two conditions are met:
- no message after opening the shell like:
    /usr/local/bin/virtualenvwrapper.sh not found
- the command:
    which virtualenvwrapper.sh
    produces a valid result

=====================================================================================
create a virtualenv for erp-workbench
-------------------------------------
make sure you are in the folder into which you git cloned erp-workbench!
ececute the following commands (you can cut and paste the whole block into a bash shell)

    mkvirtualenv -a . -p python3 workbench
    (cd bin; ln -s $(which python))
    (cd bin; ln -s $(which pip))
    bin/pip install -r install/requirements.txt
    (cd help; make html)
    (echo $'\n''alias  wb="workon workbench"' >> ~/.bash_aliases)

After having executed the above commands and opened a new bash terminal
(you created a new alias that is only active when freshly loaded)

the command:
    wb

will activate the workbench environment and cd into its installation folder!



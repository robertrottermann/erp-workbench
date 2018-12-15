Installing virtualenvwrapper
----------------------------

install the virtualenv wrapper according to the following instructions:
    http://virtualenvwrapper.readthedocs.io/en/latest/install.html

add instructions to .bashrc to add virtualenvwrapper when a shell is opened::

    # ------------------ start workon stuff -------------------
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/projetcs
    source $(which virtualenvwrapper.sh)

take care that the last lines which virtualenvwrapper.sh produces a result.
It could be, that virtualenvwrapper.sh was installed to a different directory that is not in the path
in which case it could not be found by the whihc command.

important:

make sure, that afther opening a new shell the following two conditions are met:

- no message after opening the shell like:
    /usr/local/bin/virtualenvwrapper.sh not found
- the command:
    which virtualenvwrapper.sh
    produces a valid result


---------------
Troubleshooting
---------------

Installing modules in single step mode:
---------------------------------------

For efficency erp-workbench tries to to load all modules in one batch.
When during this process an error occurs it migth be hard to spot what
module is the source of the problem.
Running in single step mode loads one module after the other::

    bin/c -I -s SITENAME

in container mode::

     bin/d -dI -s SITENAME


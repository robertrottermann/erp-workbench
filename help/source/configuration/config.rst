Erp-Workbench configuration
---------------------------

erp-workbench is configured by adapting yaml files that are found in the config folder.
When ever erp-workbench is started this files are checked for changes.
From the values found python data files in config/config_data/ are  thenconstructed.

These yaml files exist:

    - config.yaml
        It provides basic config values.
    - docker.yaml
        provides the information needed to work with docker
    - project.yaml
        how we start a new project
    - servers.yaml
        describes with what servers we deal

Base info (config.yaml)
=======================

.. literalinclude:: ../../../config/config.yaml
    :language: yaml

Docker (docker.yaml)
====================
.. literalinclude:: ../../../config/docker.yaml
    :language: yaml  

Project (project.yaml)
======================
.. literalinclude:: ../../../config/project.yaml
    :language: yaml  

Servers (servers.yaml)
======================
.. literalinclude:: ../../../config/servers.yaml
    :language: yaml  
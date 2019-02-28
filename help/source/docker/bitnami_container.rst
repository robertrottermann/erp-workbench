-------------------------------------------
creating a continer to be run by kubernetes
-------------------------------------------

Values defined in config/docker.yaml
------------------------------------

    in the docker yaml, we have defined what


Values defined in config/bitnami_chart.yaml
-------------------------------------------

Install odoo-Apps
=================

    ::

        bin/d -dI SITENAME [-v]

Install OCA and own Apps&Modules
================================

    ::

        bin/d -dio [all][m1,m2,..] SITENAME [-v]


parser_docker.add_argument(
        "-dBI", "--use_bitnami",
        action="store_true", dest="docker_use_bitnami", default=False,
        help='Use bitnami settings when handling docker or kubernetes',
    )

    parser_docker.add_argument(
        "-dBI", "--use_bitnami",
        action="store_true", dest="docker_use_bitnami", default=False,
        help='Use bitnami settings when handling docker or kubernetes',
    )

Refetch helm-chart
==================

    if the helmchart do be use (defined in ..)
    parser_docker.add_argument(
        "-drhc", "--refetch-helm-chart",
        action="store_true", dest="refetch_helm_chart", default=False,
        help='Refetch helm chart even if it already exists')


# dbdumper Dockerfile 
FROM debian:stretch

RUN apt update; apt install -y wget gnupg;     wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - ;     sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
RUN apt-get update &&  apt-get install postgresql-client-10 vim python -y --allow-unauthenticated

ENTRYPOINT ["/usr/bin/python", "/mnt/sites/dumper/dumper.py"]

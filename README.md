Docker Build Service
====================

Docker build service for Fedora. It will be integrated with koji (and copr) build system, fedmsg, Taskotron and other tools in Fedora infrastructure.

We are _not_ trying to compete with Docker Hub. Quite opposite. We would like to create an environment where Fedora users could very easily build images using Fedora infrastructure, test them and push them wherever they want (To Docker Hub for example).

Usage
=====

Currently it's under heavy development and not ready for testing. Stay tuned.


Development Instance
====================

    # clone git repository
    git clone

    # create
    ln -s site_settings-development.py dbs/site_settings.py
    ./manage.py syncdb
    ./manage.py runserver

Database Setup
==============

    # install, init and start PostgreSQL database
    dnf install postgresql-server
    postgresql-setup initdb
    systemctl start postgresql

    # create DB and user for DBS
    su - -c 'createdb dbs' postgres
    su - -c 'createuser dbs' postgres


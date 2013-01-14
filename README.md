fabric-openerp
==============

Install OpenERP server using fabric

Description
-----------
fabric-openerp is tool that makes it easy to setup and install OpenERP server in your Ubuntu Server.

Features
--------
* Installs all OpenERP's prerequisites.
* Create all necessary directories.
* Configure OpenERP Server.
* Start, stop and restart OpenERP Server.
* Backup OpenERP database.

Installation
------------
First of all you have to install `pip`

    $ sudo apt-get install python-pip

After that you gonna need to install some requirements like `Fabric` and `Jinja2`

    $ sudo pip install -r requirements.txt

#!/usr/bin/python
from __future__ import with_statement
from datetime import datetime
from fabric.api import *
from fabric.contrib.files import upload_template, exists
from mako.template import Template

env.hosts = ['ubuntu_vm'] 
env.user = 'ghassen'
env.password = 'ghassen'

env.prerequisites = ['build-essential',
                    'python-dev',
                    'python-pip',
                    'postgresql',
                    'libldap2-dev',
                    'python-dateutil',
                    'python-feedparser',
                    'python-gdata',   
                    'python-ldap',
                    'python-libxslt1',
                    'python-lxml',
                    'python-mako',
                    'python-openid',
                    'python-psycopg2',
                    'python-pybabel',
                    'python-pychart',
                    'python-pydot',
                    'python-pyparsing',
                    'python-reportlab',
                    'python-simplejson',
                    'python-tz',
                    'python-vatnumber',
                    'python-vobject',
                    'python-webdav',
                    'python-xlwt',
                    'python-yaml',
                    'python-zsi',
                    ]
NOW = datetime.now().strftime("%Y.%m.%d.%H.%M")
DIRS = {
        'OPENERP_HOME': '/opt/service/openerp',
        'SOURCE_CODE_BACKUP': '/opt/service/openerp/backup/source_code',
        'DATABASE_BACKUP': '/opt/service/openerp/backup/db',
}


def check_installed(package_name):
    """
    Checks package whether installed
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        result = run('dpkg -s {0} | grep "Status: install ok installed"'.format(package_name))
        return result.startswith("Status:")    
        
def apt_install(package_name):
    """
    Install package through apt-get install.
    """
    sudo('apt-get -y install {0}'.format(package_name))
    
def download_openerp(path):
    """
    Download OpenERP server source code
    """
    with cd(path):
        run('wget -c http://nightly.openerp.com/6.1/releases/openerp-6.1-latest.tar.gz')


def create_openerp_directories():
    sudo('mkdir -p ')
    sudo('mkdir -p ')
    sudo('mkdir -p ')
    #sudo('mkdir ')

@task
def pre_deploy():
    """
    Prepare enviroment before start installing python packages
    """
    for package_name in env.prerequisite:
        if not check_installed(package_name):
            apt_install(package_name)
        else:
            print('{0} already installed, moving on..'.format(package_name))
    sudo('pip install werkzeug')
    download_openerp()

def pg_setup():
    """usage: fab backup_db:db_name"""
    file_path = "{0}{1}.{2}.sql".format(POSTGRES_HOME,db_name,NOW)
    sudo("pg_dump {0} -f {1}".format(db_name, file_path), user= "postgres")
    sudo("gzip {0}".format(file_path), user= "postgres")
    
@task
def setup_pg_user(username, password, db_name):
    """Adds a user to postgres and creates a database"""
    sql = """
    CREATE USER '{0}' WITH CREATEDB PASSWORD '{1}';
    CREATE DATABASE {2} WITH OWNER {1};
    """.format(username, password, db_name)
    sudo('psql -c "{0}"'.format(sql), user= "postgres")
    pg_hba_conf_path =  "/etc/postgresql/9.1/main/pg_hba.conf"
    sudo('echo "host {0} {1} 127.0.0.1/32 trust" >> {2}'.format(_db_name, username, pg_hba_conf_path,
        user="postgres"
        )
    sudo("service postgres restart")

@task
def pg_backup():
    file_path = "{0}{1}.{2}.sql".format(POSTGRES_HOME,db_name,NOW)
    sudo("pg_dump {0} -f {1}".format(db_name, file_path), user= "postgres")
    sudo("gzip {0}".format(file_path), user= "postgres")
    
@task
def start_server():
    """
    Start OpenERP server
    """
    sudo('service openerp-server start')

@task    
def stop_server():
    """
    Stop OpenERP server
    """
    sudo('service openerp-server stop')

@task    
def restart_server():
    """
    Restart OpenERP server
    """
    sudo('service openerp-server restart')

@task    
def configure_openerp():
    sudo('mkdir -p {0}'.format(OPENERP_HOME))
    with cd('/tmp'):
        run('tar -xzf openerp-6.1-latest.tar.gz')
        sudo('mv openerp-6.1-2* {0}/server'.format(OPENERP_HOME))
    upload_template(
                    filename='templates/openerp-server.conf',
                    destination='{0}/server/openerp-server.conf'.format(OPENERP_HOME),
                    context={
                             'OPENERP_HOME': OPENERP_HOME,
                             'db_user': 'openerp',
                             'db_password': 'openerp',
                     },
                     use_jinja=True,
                     template_dir=None,
                     use_sudo=True,
                     backup=True, 
                     mirror_local_mode=False,
                     mode=None
    )
        
              
@task
def test():
    pass
        #openerp_conf = Template(filename='templates/openerp-server.conf')
        #print(openerp_conf.render())       
    
@task
def deploy():
    pg_setup()
    configure_openerp()
    start_server()
    
@task
def post_deploy():
    make_server_run_on_statup()
    backup_database()
    backup_source_code()
    

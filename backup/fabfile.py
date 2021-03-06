from fabric.api import *
from sys import exit

# Default release is 'staging'
env['release_type'] = 'staging'
staging_server = 'root@staging.theknetwork.org'
prod_server =  'root@prod.theknetwork.org'
env['repository'] = 'Codename-K'
env['branch'] = 'develop'

def staging():
    """Staging server settings"""
    env['path'] = '/environments/staging'
    env.host_string = staging_server


def prod():
    """Production server settings"""
    env['path'] = '/environments/prod'
    env['branch'] = 'master'
    env.host_string = prod_server

def deploy():
    """Deploy the latest version of the site to the server and restart apache"""
    checkout_latest()
    symlink_current_release()
    install_requirements()
    migrate()
    restart_apache()

def checkout_latest():
    """Pull the latest code into the git repo and copy to a timestamped release directory"""
    import time
    env['release'] = time.strftime('%Y%m%d%H%M%S')
    run('cd %(path)s/%(repository)s; git pull origin %(branch)s' % env, pty=True)
    run('cp -R %(path)s/%(repository)s %(path)s/releases/%(release)s; rm -rf %(path)s/releases/%(release)s/.git*' % env, pty=True)  

def symlink_current_release():
    """Symlink our current release"""
    run('cd %(path)s/releases; rm current; ln -s %(release)s current' % env, pty=True)

def install_requirements():
    """Install the required packages using pip"""
    run('cd %(path)s/releases/current; %(path)s/python/bin/pip install -r %(path)s/releases/current/dependencies.txt' % env, pty=True)

def migrate():
    """Run our migrations"""
    run('export DJANGO_ENV=%(release_type)s; cd %(path)s/releases/current/codenamek;  %(path)s/python/bin/python manage.py syncdb --noinput' % env, pty=True)

def restart_apache():
    "Reboot Apache2 server."
    sudo("service apache2 reload",pty=True)

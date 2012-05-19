from fabric.api import *
from sys import exit

# Default release is 'staging'
env['release_type'] = 'staging'
staging_server = 'root@staging.theknetwork.org'
prod_server =  'root@prod.theknetwork.org'
env['repository'] = 'knetwork'
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
    # restart_apache()
    # Restarting apache is usually not needed, because the wsgi file is updated and
    # apache doesn't need to reload anything, mod_wsgi takes care of that.

def checkout_latest():
    """Pull the latest code into the git repo and copy to a timestamped release directory"""
    import time
    env['release'] = time.strftime('%Y%m%d%H%M%S')
    run('cd %(path)s/git/%(repository)s; git pull origin %(branch)s' % env, pty=True)
    run('cp -R %(path)s/git/%(repository)s %(path)s/releases/%(release)s; rm -rf %(path)s/releases/%(release)s/.git*' % env, pty=True)  

def symlink_current_release():
    """Symlink our current release"""
    run('cd %(path)s/releases; rm knetwork; ln -s %(release)s knetwork' % env, pty=True)

def install_requirements():
    """Install the required packages using pip"""
    run('cd %(path)s/releases/knetwork; %(path)s/bin/pip install -r %(path)s/releases/knetwork/requirements/project.txt' % env, pty=True)

def migrate():
    """Run our migrations"""
    run('export DJANGO_ENV=%(release_type)s; cd %(path)s/releases/knetwork;  %(path)s/bin/python manage.py migrate schools' % env, pty=True)

def reload():
    "Touch wsgi.py"
    #sudo("service apache2 restart",pty=True)
    
def restart_apache():
    "Reboot Apache2 server."
    sudo("service apache2 restart",pty=True)
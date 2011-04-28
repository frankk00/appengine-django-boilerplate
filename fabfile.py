from fabric.api import local, prompt, puts
from fabric.contrib.console import confirm
from fabric.context_managers import lcd, hide
import os
from collections import namedtuple

RepoInfo = namedtuple('RepoInfo', 'local target remote')
REPO_DIR = os.path.expanduser("~/projects/repos")
CURRENT_DIR = os.path.dirname(__file__)

def get_repo(repo_info, repo_rename=None):
    """utility for getting the repo if it does not exist"""
    #if the path does not exist, download the repo
    if not os.path.exists(os.path.join(REPO_DIR, repo_info.local)):
        with lcd(REPO_DIR):
            if repo_info.remote.startswith("git"):
                local("git clone %s" % repo_info.remote, capture=False)
            elif "bitbucket" in repo_info.remote or "googlecode" in repo_info.remote:
                local("hg clone %s" % repo_info.remote, capture=False)

def symlink_packages():
    """sets up symlinked packages"""
    repos = [
        RepoInfo('django-dbindexer/dbindexer','dbindexer','https://bitbucket.org/wkornewald/django-dbindexer'),
        RepoInfo('django-nonrel/django','django','https://bitbucket.org/wkornewald/django-nonrel'),
        RepoInfo('djangoappengine','djangoappengine','https://bitbucket.org/wkornewald/djangoappengine'),
        RepoInfo('djangotoolbox/djangotoolbox','djangotoolbox','https://bitbucket.org/wkornewald/djangotoolbox'),
        RepoInfo('django-mediagenerator/mediagenerator', 'mediagenerator', 'https://iynaix@bitbucket.org/wkornewald/django-mediagenerator'),
        RepoInfo('jinja2/jinja2', 'jinja2', 'git://github.com/mitsuhiko/jinja2.git'),
        RepoInfo('gaeunit/gaeunit.py','gaeunit.py','git://github.com/iki/gaeunit.git'),
    ]

    #remove current batch of symlinks
    for r in repos:
        local("rm -rf %s" % r.target)

    #links the repos, and downloads if they are missing
    for r in repos:
        get_repo(r) #download the repo if needed
        local("ln -s %s %s" % (os.path.join(REPO_DIR, r.local), r.target)) #symlink

def settings(mode="dev"):
    """sets the app.yaml and settings.py and """
    if mode=="dev":
        local("ln -sf app_dev.yaml app.yaml")
    elif mode=="prod":
        local("ln -sf app_prod.yaml app.yaml")
    else:
        raise ValueError("The mode can only be 'dev' or 'prod'.")

def generatemedia(mode="dev", optimize=0):
    """generates the media for production"""
    settings(mode="prod")
    local("python manage.py generatemedia", capture=False)
    #optimize the pngs using optipng and jpgs using jpegtran
    #optimizations are in place and lossless
    if optimize:
        puts("Optimizing images...")
        with hide('running', 'stdout', 'stderr'):
            for root, dirs, files in os.walk("_generated_media"):
                for f in files:
                    fname = os.path.join(root, f)
                    if f.endswith(".png"):
                        local("optipng -quiet -o7 %s" % (fname))
                    elif f.endswith(".jpg") or f.endswith(".jpeg"):
                        local("jpegtran -copy none -optimize -outfile %s %s" % (fname, fname))
    settings(mode=mode)

def deploy(mode="pexpect"):
    """deploy the application"""
    import getpass
    import pexpect
    import sys

    try:
        clear_data() #clears the blob and datastores
        settings(mode="prod") #set to production settings
        #populate the categories
        if os.path.exists("./initial_data.json")
            local("python2.5 manage.py loaddata ./initial_data.json")
        username = prompt("Please enter your username: ")
        cmd = "python manage.py deploy --email='%s@gmail.com'" % username

        #normal deployment, everything keyed in manually
        if mode=="normal":
            local(cmd, capture=False) #normal version

        #fancy automated deployment using pexpect
        else:
            password = getpass.getpass("Please enter your password: ")

            child = pexpect.spawn(cmd, timeout=90000)
            child.logfile_read = sys.stdout
            child.logfile_send = None
            child.expect("Password for .*@gmail.com: .*")
            child.sendline(password)

            child.expect("Login via Google Account .*:.*")
            child.sendline("%s@gmail.com" % username)
            child.expect("Password: .*")
            child.sendline(password)
            child.expect("Login via Google Account .*:.*")
            child.sendline("%s@gmail.com" % username)
            child.expect("Password: .*")
            child.sendline(password)
    finally:
        settings(mode="dev") #set to production settings

def rollback():
    """rolls back the application"""
    local("appcfg.py rollback .", capture=False)

def clear_data():
    """clears the datastore and the blobstore"""
    local("rm -rf /tmp/*.datastore")
    local("rm -rf /tmp/*.blobstore")
    local("rm -rf .gaedata/*")

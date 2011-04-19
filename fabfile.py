from fabric.api import local, prompt, puts
from fabric.contrib.console import confirm
from fabric.context_managers import lcd
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
            #elif "googlecode" in repo_info.remote:
                #local("git svn clone %s %s" % (repo_info.remote, repo_info.local.split("/")[0]), capture=False)

def symlink_packages():
    """sets up symlinked packages"""
    repos = [
        RepoInfo('django-dbindexer/dbindexer','dbindexer','https://bitbucket.org/wkornewald/django-dbindexer'),
        RepoInfo('django-nonrel/django','django','https://bitbucket.org/wkornewald/django-nonrel'),
        RepoInfo('djangoappengine','djangoappengine','https://bitbucket.org/wkornewald/djangoappengine'),
        RepoInfo('djangotoolbox/djangotoolbox','djangotoolbox','https://bitbucket.org/wkornewald/djangotoolbox'),
        RepoInfo('django-debug-toolbar/debug_toolbar','debug_toolbar','git://github.com/robhudson/django-debug-toolbar.git'),
        #RepoInfo('django-extensions/django_extensions','django_extensions','git://github.com/django-extensions/django-extensions.git'),
        RepoInfo('django-registration/registration','registration','https://bitbucket.org/ubernostrum/django-registration'),
        RepoInfo('jinja2/jinja2', 'jinja2', 'git://github.com/mitsuhiko/jinja2.git'),
        RepoInfo('surlex/src/surlex', 'surlex', 'git://github.com/codysoyland/surlex.git'),
        RepoInfo('windmill/windmill', 'windmill', 'git://github.com/windmill/windmill.git'),
        #RepoInfo('django-test-utils/test_utils', 'test_utils', 'git://github.com/ericholscher/django-test-utils.git'),
        #RepoInfo('mock', 'mock', 'https://mock.googlecode.com/hg/'),
        RepoInfo('django-mediagenerator/mediagenerator', 'mediagenerator', 'https://iynaix@bitbucket.org/wkornewald/django-mediagenerator'),
        RepoInfo('django-taggit/taggit', 'taggit', 'git://github.com/alex/django-taggit.git'),
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
        #replace with the production app.yaml and settings.py
        local("rm -rf app.yaml settings.py")
        local("cp app_dev.yaml app.yaml")
        local("cp settings_dev.py settings.py")
    elif mode=="prod":
        #replace with the production app.yaml and settings.py
        local("rm -rf app.yaml settings.py")
        local("cp app_prod.yaml app.yaml")
        local("cp settings_prod.py settings.py")
    else:
        raise ValueError("The mode can only be 'dev' or 'prod'.")

def generatemedia(mode="dev"):
    """generates the media for production"""
    settings(mode="prod")
    local("python manage.py generatemedia", capture=False)
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

def populate():
    """populates the database with categories and users"""
    local("python2.5 manage.py loaddata ./initial_data.json") #categories
    local("python2.5 manage.py loaddata ./users.json") #dummy users

def clear_data():
    """clears the datastore and the blobstore"""
    local("rm -rf /tmp/*.datastore")
    local("rm -rf /tmp/*.blobstore")

def merge_clean():
    """cleans off all the .orig files after a merge"""
    problem_files = []
    #weed out the files
    for root, dirs, files in os.walk(CURRENT_DIR):
        for f in files:
            if f.endswith(".orig"):
                problem_files.append(os.path.join(root, f))

    #confirm then remove the files
    if problem_files:
        for f in problem_files:
            puts(f)
        ans = confirm("Remove the above files?", default=False)
        if ans:
            for f in problem_files:
                os.remove(f)

def test():
    """runs the test suite for the zoop application"""
    #runs the django unit tests for the zoop application
    local("python2.5 manage.py test --failfast zoop", capture=False)
    #runs the windmill test suite for the zoop application
    #local("p)thon2.5 manage.py test_windmill", capture=False)

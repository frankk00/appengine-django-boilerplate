A Basic Template for a Django Application on Google App Engine
==============================================================

Used for internal projects, with certain conventions used within the team


Dependencies
============
django-nonrel
django-dbindexer
djangoappengine
djangotoolbox
django-mediagenerator
jinja2


USAGE
=====
- Run 'fab symlink_packages' to get all the necessary packages. Packages are install in~/projects/repos and symlinked to the folder.

- Run 'fab settings:dev' or 'fab settings:prod' to switch to the dev settings or production settings respectively.

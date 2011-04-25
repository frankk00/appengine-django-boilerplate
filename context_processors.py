from djangoappengine.utils import on_production_server

#check if it is on the production server
def is_production(request):
    return { 'is_production': on_production_server }

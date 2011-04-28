from django.conf.urls.defaults import *
from django.views.generic import RedirectView, TemplateView, ListView

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    ('^$', 'django.views.generic.simple.direct_to_template',
     {'template': 'home.html.jin'}),
)

urlpatterns += patterns("",
    (r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
    (r'^sitemap\.xml$', RedirectView.as_view(url='sitemap.txt')),
    (r'^humans\.txt$', TemplateView.as_view(template_name='humans.txt')),
    (r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt')),
)

import os, sys
import pyworkflow as pw
from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from django.conf import settings
from pyworkflow.web.pages.settings import WS_ROOT, serviceFolders
from django.views.generic import TemplateView
from django.conf.urls.static import static

#===============================================================================
# URL ASSOCIATION
#===============================================================================

mainUrls = ['',
    # To serve different static files
    (r'^resources/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'emxconvert.views.index'),
    url(r'^emxconvert/', include('emxconvert.urls')), # ADD THIS NEW TUPLE!

]

urlpatterns = patterns(*mainUrls) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


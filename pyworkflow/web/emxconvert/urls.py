from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
        url(r'^list/$', views.list, name='list'),
        url(r'^$', views.index, name='index')
        )
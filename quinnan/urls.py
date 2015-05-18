from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',  (r'^$', 'core.views.index'),
 (r'^users/', include('samba.urls')),  (r'^admin/', include(admin.site.urls)),   
  (r'^systemstats/', include('system_stats.urls')),   
(r'^accounts/', include('dregistration.urls')), 

(r'^shares/add/$', 'samba.views.add_share'), (r'^shares/edit/(?P<id>\d+)/$', 'samba.views.edit_share'),  (r'^shares/$', 'samba.views.shares'),
(r'^shares/delete/(?P<id>\d+)/$', 'samba.views.delete_share'), (r'^shares/rdelete/(?P<id>\d+)/$', 'samba.views.really_delete_share'),

(r'^myfiles/$', 'filemanager.views.myshares'),

(r'^myfiles/(?P<path>.*)$', 'filemanager.views.get_path'),

)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns += staticfiles_urlpatterns()
from django.conf import settings

if settings.LOCAL_MAC== True:
    urlpatterns += patterns('', (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': settings.STATIC_DOC_ROOT}),)

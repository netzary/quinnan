from django.conf.urls import *
from views import *
from models import *


urlpatterns = patterns('',  (r'^$', index),(r'^add/$', add_user),  (r'^changepassword/(?P<id>\d+)/$', change_password),   

 (r'^delete/(?P<id>\d+)/$', delete),    (r'^rdelete/(?P<id>\d+)/$', really_delete),    (r'^enable/(?P<id>\d+)/$', enable),  
(r'^changequota/(?P<id>\d+)/$', change_quota),   (r'^set_storage/$', set_storage),  (r'^saved/$', saved), (r'^cleanup/(?P<id>\d+)/$', clean_up),

(r'^disabled/$', disabled),

)

from django.conf.urls import *
'''import settings'''
from django.conf import settings
from views import *
from models import *


urlpatterns = patterns('', (r'^memorystat/$', get_mem),   (r'^memory/$', memory),   
)

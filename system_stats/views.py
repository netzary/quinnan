from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import *
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.views.decorators.csrf import *
from django.conf import settings
from django.utils import simplejson
from django.core.context_processors import csrf
from django import forms
from django.conf import settings
from django.forms import ModelForm
from django.template import Context, loader
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
'''import settings'''
from datetime import datetime
from datetime import date
import re
from decimal import Decimal

from models import *
import psutil

def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9.8 K/s'
    >>> bytes2human(100001221)
    '95.4 M/s'
    """
    symbols = ('KB', 'MB', 'GB', 'TB', 'PB', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s %s' % (value, s)
    return "0 Bytes"


def get_mem(request):
	phymem = psutil.phymem_usage()
	vmem=   psutil.virtmem_usage()
	data={}
	data["totalp"]= int(phymem.total)/(1024*1024) 
	data["freep"] = int(phymem.free)/(1024*1024)
	data["usedp"] = int(phymem.used)/(1024*1024)
	data["percentp"] = (phymem.percent)
	data["totalv"] = int(vmem.total)/(1024*1024)
	data["freev"] = int(vmem.free)/(1024*1024)
	data["usedv"] = int(vmem.used)/(1024*1024)
	data["percentv"] = (vmem.percent)
        
	
    
	return render_to_response("system/memory.html", {"data":data})


def memory(request):
	return render_to_response("memory.html")

def process(request):
	return render_to_response("process.html")

def get_top(request):
	procs = [p for p in psutil.process_iter()]
	

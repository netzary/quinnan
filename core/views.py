from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
import datetime  
from django.contrib.auth.models import User
import datetime, random, csv
from django.template import Context, Template, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.forms import ModelForm
from django import forms
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_unicode
from models import *
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.core.mail import send_mail


def index(request):
	return render_to_response("base.html", context_instance=RequestContext(request))
	

def base(request):
	return render_to_response("base.html", context_instance=RequestContext(request))
	

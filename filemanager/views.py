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
from datetime import datetime
from datetime import date
import re, os, subprocess
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from samba.models import *
import psutil, pexpect
from django.core.servers.basehttp import FileWrapper

@login_required
def myshares(request):
    user= request.user
    try:
	samba= SambaUser.objects.get(user=user)
    except SambaUser.DoesNotExist:
	return HttpResponse("There are no Shares")
    shares=Share.objects.filter(read=samba)
    paths =[]
    base_path=(Storage.objects.all()[0]).share_path
    for share in shares:
	paths.append( {"name":share, "path": os.path.join(base_path, share.share)})
    
    home = {"name":user.username, "path": os.path.join("/home", user.username)}
    return render_to_response("filemanager/shares.html", {"object_list": paths, "home":home}, context_instance=RequestContext(request))

@login_required
def get_path(request,path):
    user= request.user
    try:
	samba= SambaUser.objects.get(user=user)
    except SambaUser.DoesNotExist:
	return HttpResponse("There are no Shares")
    home = os.path.join("/home", user.username)
    paths =[]
    shares=Share.objects.filter(read=samba)
    paths =[]
    base_path=(Storage.objects.all()[0]).share_path
    for share in shares:
	paths.append(os.path.join(base_path, share.share))
    paths.append(home)
    if not path.startswith("/"):
        path ="/"+path

    for pat in paths:
	#return HttpResponse(str(path+"  "+ pat))
	if path.startswith(pat):
	    #return HttpResponse("Fucks")
	    
	    
	    if os.path.exists(path):
		#return HttpResponse("Fucks2")
		if os.path.isdir(path):
		    dirs =[]
		    files=[]
		    contents = os.listdir(path)
		    for cunt in contents:
			if os.path.isdir(os.path.join(path,cunt)):
			    shelf ={}
			    shelf["name"]=cunt
			    shelf["path"]=os.path.join(path,cunt)
			    dirs.append(shelf)
			elif os.path.isfile(os.path.join(path,cunt)):
			    shelf ={}
			    shelf["name"]=cunt
			    shelf["path"]=os.path.join(path,cunt)
			    files.append(shelf)
		    return render_to_response("filemanager/dirs.html", {"dirs":dirs, "files":files}, context_instance=RequestContext(request))
			
		    
		elif os.path.isfile(path):
		    
		    wrapper = FileWrapper(file(path))
		    response = HttpResponse(wrapper, content_type='text/plain')
		    folder, name = os.path.split(path)
		    filename = 	'attachment; filename=%s' % str(name)
		    response['Content-Disposition'] = filename
		    response['Content-Length'] = os.path.getsize(path)
		    return response
	    else:
		return HttpResponse("The path does not exist")
	else:
	    pass
    return HttpResponse("You dont have permissions")



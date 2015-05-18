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
import re, os, subprocess
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from models import *
import psutil, pexpect
attrs_dict = { 'class': 'required' }

from django import forms
class UserAddForm(forms.Form):


    username = forms.RegexField(regex=r'^\w+$',
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'username'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_(u'email address'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'password'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'password (again)'))
    quota     = forms.RegexField(regex=r'^\d+$',
                                max_length=10,
                                widget=forms.TextInput(attrs=attrs_dict), label=_(u'Quota'))
                                
	
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))
     
    def clean_email(self):
		try:
			user = User.objects.get(email__iexact=self.cleaned_data['email'])
		except User.DoesNotExist:
			return self.cleaned_data['email']
		except:
			raise forms.ValidationError(_(u'This email is already taken. Please choose another.'))
		raise forms.ValidationError(_(u'This email is already taken. Please choose another.'))
    def clean_quota(self):
		free =psutil.disk_usage('/home/').free/(1024*1024)
		if int(self.cleaned_data["quota"])> (free-500):
			raise forms.ValidationError(_(u'Please choose a smaller size for the quota size. Maximum allowed is %s MB' % str(free-500)))
		return self.cleaned_data['quota']
    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u'You must type the same password each time'))
        return self.cleaned_data
    

@staff_member_required
def add_user(request):
	
	try:
		storage = Storage.objects.all()[0]
	except IndexError:
		return HttpResponseRedirect("/users/set_storage/")
	
	if request.method=="POST":
		form = UserAddForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(username=form.cleaned_data['username'],
                                                                    password=form.cleaned_data['password1'],
                                                                    email=form.cleaned_data['email'])
            
			samba = SambaUser(user=user, quota= int(form.cleaned_data['quota']))
			
			
		
			
			command = 'sudo smbldap-useradd -a -m -P %s' % form.cleaned_data['username']
			ch =pexpect.spawn(command)
			ch.expect('New password:')
			ch.sendline(form.cleaned_data['password1'])
			ch.expect('Retype new password:') 
			ch.sendline(form.cleaned_data['password1'])
			quota = int(form.cleaned_data["quota"]) * 1024 
			command = "sudo setquota -u %s -F vfsv0 0 %s 0 0 %s"  %( str( form.cleaned_data['username']), str(quota), str(storage.mount.strip()))
			os.system(command)
			command ="sudo quotacheck -u %s" % str(storage.mount.strip())
			os.system(command)
			samba.path ="/home/" + form.cleaned_data['username'] +"/"
			samba.save()
			
			return HttpResponseRedirect("/users/saved/")
	else:
		form = UserAddForm()
	free =psutil.disk_usage('/home/').free/(1024*1024) -500

	return render_to_response("samba/adduser.html", {"form":form, "free":free}, context_instance=RequestContext(request))






class PasswordChangeForm(forms.Form):
	password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'password'))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'password (again)'))
	
	
	




@staff_member_required
def change_password(request, id):
	sambauser = get_object_or_404(SambaUser,id__exact =id)
	if request.method =="POST":
		form =PasswordChangeForm(request.POST)
		if form.is_valid():
			user = sambauser.user
			user.set_password(form.cleaned_data.get("password1"))
			
			username =user.username
			password = str(form.cleaned_data.get("password1"))
			command = 'sudo smbldap-passwd %s' % username
			ch =pexpect.spawn(command)
			ch.expect('New password:')
			ch.sendline(password)
			ch.expect('Retype new password:') 
			ch.sendline(password)
			
			user.save()
			sambauser.save()
			
			
			return HttpResponseRedirect("/users/saved/")
	else:
		form =PasswordChangeForm()
	return render_to_response("samba/changepassword.html", {"form":form}, context_instance=RequestContext(request))

class ChangeQuotaForm(ModelForm):
	class Meta:
		model = SambaUser
		exclude = ('user', 'used', 'path', 'is_disabled','percent')
		


@staff_member_required
def change_quota(request, id):
	try:
		storage = Storage.objects.all()[0]
	except IndexError:
		return HttpResponseRedirect("/users/set_storage/")
	user = get_object_or_404(SambaUser,id__exact =id)
	if request.method =="POST":
		form =ChangeQuotaForm(request.POST, instance=user)
		if form.is_valid():
			user =form.save(commit=False)
			user.save()
			quota = int(form.cleaned_data["quota"]) * 1024 
			command = "sudo setquota -u %s -F vfsv0 0 %s 0 0 %s"  %( str( user.user.username), str(quota), str(storage.mount.strip()))
			os.system(command)
			command ="sudo quotacheck -u %s" % str(storage.mount.strip())
			os.system(command)
			return HttpResponseRedirect("/users/saved/")
	else:
		form =ChangeQuotaForm( instance=user)
	return render_to_response("samba/changequota.html", {"form":form}, context_instance=RequestContext(request))

		
@staff_member_required
def index(request):
	users = SambaUser.objects.filter(is_disabled=False)
	return render_to_response("samba/index.html" ,{"object_list":users},  context_instance=RequestContext(request))

	
@staff_member_required	
def disabled(request):
	users = SambaUser.objects.filter(is_disabled=True)
	
	return render_to_response("samba/disabled.html" ,{"object_list":users},  context_instance=RequestContext(request))
@staff_member_required
def clean_up(request,id):
	user =get_object_or_404(SambaUser, id__exact =id)
	path = user.path
	user.delete()
	user.user.delete()
	if len(path)>7:
		command= "sudo rm -r %s" % path
		os.system(command)
		return HttpResponseRedirect("/saved/")
	else:
		return HttpResponseRedirect("/users/")
	
class EnableForm(forms.Form):
	

    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'password'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'password (again)'))
    quota     = forms.RegexField(regex=r'^\d+$',
                                max_length=10,
                                widget=forms.TextInput(attrs=attrs_dict), label=_(u'Quota'))
@staff_member_required
def enable(request,id):
	try:
		storage = Storage.objects.all()[0]
	except IndexError:
		return HttpResponseRedirect("/users/set_storage/")
	sambauser =get_object_or_404(SambaUser, id__exact =id)
	if sambauser.is_disabled == False:
		return HttpResponse("The User is enabled")
	used =sambauser.used  
	if request.method == "POST":
		form = EnableForm(request.POST)
		if form.is_valid():
			
			username = sambauser.user.username
			user = sambauser.user
			user.set_password(form.cleaned_data.get("password1"))
			
			
			password = str(form.cleaned_data.get("password1"))
			command = "sudo smbldap-useradd  -a -P %s" % username
			ch =pexpect.spawn(command)
			ch.expect('New password:')
			ch.sendline(password)
			ch.expect('Retype new password:') 
			ch.sendline(password)
			
			user.save()
			sambauser.is_disabled=False
			sambauser.save()
			
			if int(form.cleaned_data["quota"])> sambauser.used:
				sambauser.quota =int(form.cleaned_data["quota"])
				
				quota = int(form.cleaned_data["quota"]) * 1024 
				command = "sudo setquota -u %s -F vfsv0 0 %s 0 0 %s"  %( str(user.username), str(quota), str(storage.mount.strip()))
				os.system(command)
				command ="sudo quotacheck -u %s" % str(storage.mount.strip())
				os.system(command)
				sambauser.is_disabled=False
				sambauser.quota =quota
				sambauser.save()
			return HttpResponseRedirect("/users/saved/")
	else:
		form = EnableForm()
	return render_to_response("samba/enable_form.html", {"form":form, "used":used}, context_instance=RequestContext(request))

			
	
	
	


class StorageForm(ModelForm):
	quota = forms.RegexField(regex=r'^\d+$', max_length=10, widget=forms.TextInput(attrs=attrs_dict), label=_(u'Quota',))
	
	class Meta:
		model =Storage
		exclude =( "site",)
	def clean_total(self):
		if self.cleaned_data.get("total"):
			try:
				k=int(self.cleaned_data["total"])
				pass
			except ValueError:
				raise forms.ValidationError(_(u'Please ensure you choose an integer. Avoid commas, dots etc'))
				
				
		free =psutil.disk_usage('/home/').total/(1024*1024)
		if int(self.cleaned_data["total"])> (free-500):
			raise forms.ValidationError(_(u'Please choose a smaller size for the quota size. Maximum allowed is %s MB' % str(free-500)))
		return self.cleaned_data['total']


                                
@staff_member_required
def set_storage(request):
	free =psutil.disk_usage('/home/').total/(1024*1024) -500
	try:
		
		site =Site.objects.all()[0]
		
		
		
	except Site.DoesNotExist:
		return HttpResponse("Error")
	
	try:
		storage =Storage.objects.get(site=site)
		
		if request.method == "POST":
			form = StorageForm(request.POST, instance=storage)
			if form.is_valid():
				storage = form.save(commit=False)
				storage.site =site
				storage.save()
				return HttpResponseRedirect("/users/saved/")
		else:
			form = StorageForm(instance=storage)
			free =psutil.disk_usage('/home/').total/(1024*1024) -500
		return render_to_response("samba/storage.html", {"form":form, "free":free},  context_instance=RequestContext(request))
				
		
	except Storage.DoesNotExist:
		
		
		if request.method=="POST":
			form = StorageForm(request.POST)
			if form.is_valid():
				storage = form.save(commit=False)
				storage.site =site
				storage.save()
				return HttpResponseRedirect("/users/saved/")
	
		else:
			free =psutil.disk_usage('/home/').total/(1024*1024) -500
			form =StorageForm()
		return render_to_response("samba/storage.html", {"form":form, "free":free},  context_instance=RequestContext(request))
	

@staff_member_required
def delete(request, id):
	user = get_object_or_404(SambaUser, id__exact =id)
	
	url ="/users/rdelete/%s/" % str(id)
	return HttpResponseRedirect(url)


delete_choices = (('1', "No, Please Don't Delete"), ('2', "Disable, but dont delete files or folders of the user"), ('3', "Delete, along with user directory. I will lose all files saved by user"))
class DeleteForm(forms.Form):
	option= forms.ChoiceField(label = "Delete Options", choices= delete_choices) 
@staff_member_required
def really_delete(request,id):
	user = get_object_or_404(SambaUser, id__exact =id)
	username = user.user.username
	djangouser= User.objects.get(username__exact=username)
	if request.method=="POST":
		
		form = DeleteForm(request.POST)
		if form.is_valid():
			if form.cleaned_data.get("option")=='1':
				return HttpResponseRedirect("/users/")
			elif form.cleaned_data.get("option") == '2':
				command = "sudo smbldap-userdel %s" % username
				os.system(command)
				user.is_disabled=True
				user.save()
				take_from_groups(user)
				return HttpResponseRedirect("/users/")
			else:
				command = "sudo smbldap-userdel -r %s" % username
				os.system(command)
				take_from_groups(user)

				user.delete()
				djangouser.delete()
				return HttpResponseRedirect("/users/")
	else:
		form = DeleteForm()
	
		return render_to_response("samba/delete.html", {"form":form},  context_instance=RequestContext(request))

def saved(request):
    return render_to_response("samba/saved.html")

@staff_member_required
def browse(request):
    return render_to_response("samba/browse.html")
    



class ShareForm(ModelForm):
    class Meta:
	model = Share
    def clean_share(self):
	if self.cleaned_data['share']:
	    share = self.cleaned_data['share']
	    users =[samba.user.username for samba in SambaUser.objects.all()]
	    if share in users:
		raise forms.ValidationError(_(u'Please choose another share name. A user with the same name exists'))
	    
	    regex=r'^\w+$'
	    reg = re.compile(regex)
	    s= re.match(reg,share)
	    
	    if s == None:
		
		raise forms.ValidationError(_(u'Please ensure that no space or special characters are used for the share name'))

	return self.cleaned_data['share']
	
class Share2Form(ModelForm):
    class Meta:
	model = Share
	exclude =('share',)
   
	
@staff_member_required
def edit_share(request, id):
    share= get_object_or_404(Share, id__exact=id)
    if request.method=="POST":
	form = Share2Form(request.POST, instance=share)
	if form.is_valid():
	    form.save()
	    share_edit(share)
	    return HttpResponseRedirect("/shares/")
    else:
	form =Share2Form( instance=share)
    return render_to_response("samba/addshare.html", {"form":form},  context_instance=RequestContext(request))


	
@staff_member_required
def add_share(request):
    try:
		
	site =Site.objects.all()[0]
		
		
		
    except Site.DoesNotExist:
	return HttpResponse("Error")
    try:
	storage =Storage.objects.get(site=site)
    except Storage.DoesNotExist:
	return HttpResponseRedirect("/users/set_storage/")
    path = storage.share_path 
    if request.method=="POST":
	form = ShareForm(request.POST)
	if form.is_valid():
	    form.save()
	    share = Share.objects.get(share= form.cleaned_data['share'])
	    create_share(share)
	    
	    
	    
	    
	    return HttpResponseRedirect("/shares/")
    else:
	form =ShareForm()
    return render_to_response("samba/addshare.html", {"form":form},  context_instance=RequestContext(request))
    
    
    
@staff_member_required
def shares(request):
    users = Share.objects.all()
    return render_to_response("samba/shares_index.html" ,{"object_list":users},  context_instance=RequestContext(request))

	

	
@staff_member_required
def delete_share(request, id):
    share= get_object_or_404(Share, id__exact=id)
    url = "/shares/rdelete/%s" % (share.id)
    return HttpResponseRedirect(url)
    
    
sdelete_choices = (('1', "No, Please Don't Delete"), ('2', "Delete, I will lose all files saved by my users in this share"))

class ShareDeleteForm(forms.Form):
    option= forms.ChoiceField(label = "Delete Options", choices= sdelete_choices) 
    
    
@staff_member_required
def really_delete_share(request,id):
    share= get_object_or_404(Share, id__exact=id)
	
    if request.method=="POST":
		
	form = ShareDeleteForm(request.POST)
	if form.is_valid():
	    if form.cleaned_data.get("option")=='1':
		
		return HttpResponseRedirect("/shares/")
	    elif form.cleaned_data.get("option") == '2':
		deleteshare(share)
			
		return HttpResponseRedirect("/shares/")
    else:
	form = ShareDeleteForm()
	
    return render_to_response("samba/delete_share.html", {"form":form},  context_instance=RequestContext(request))

 
 
def take_from_groups(user):
    
    storage = Storage.objects.all()[0]
    path =storage.share_path
    shares =Share.objects.all()
    for share in shares:
	writes = share.write.all()
	reads = share.read.all()
	if user in writes:
	    share.write.remove(user)
	if user in reads:
	    share.write.remove(user)
	share.save()
	 
	reader=[read.user.username for read in reads]
	writer =[read.user.username for read in writes]
	
	reader.extend(writer)
	share.old_shares = ','.join(reader)
	share.save()
	if user.user.username in reader:
	    command  =   "smb-ldap-groupmod -x %s %s" %(  user.user.username, share.share)
	    os.system(command)
    filename = "/etc/samba/shares.smb.conf"
    f= open(filename, 'w')
    
    for share in shares:
	f.write("[" + share.share + "]")
	f.write("\n")
	f.write("\t\t")
	f.write("guest ok = Yes")
	f.write("\n")
	
	
	f.write("\t\t")
	
	
	fpath = "path = %s " %(path+"/"+ share.share)
	f.write(fpath)
	f.write("\n")
	
	s_read = share.read.all()
	s_write = share.write.all()
		
	    
	if len(s_read)>0:    
	    f.write("\t\t")
	    read_list = "read list = %s" % (' '.join([s.user.username for s in s_read]))
	    f.write(read_list)
	    f.write("\n")



	if len(s_write)>0:   
	    f.write("\t\t")
	    read_list = "write list = %s" % (' '.join([s.user.username for s in s_write]))
	    f.write(read_list)
	    f.write("\n")
	
	f.write("\t\t")
	f.write("create mask = 0770")
	f.write("\n")
		
	
	f.write("\t\t")
	f.write("force create mode = 0770")
	f.write("\n")
	
	f.write("\t\t")
	f.write("directory mode = 0770")
	f.write("\n")
	
	f.write("\t\t")
	f.write("force directory mode = 0770")
	f.write("\n")
	
    f.close()
	
	
    command ="sudo /etc/init.d/samba reload"
    
    os.system(command)
   

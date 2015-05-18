from django.db import models
from django.contrib.auth.models import *
from django.contrib.sites.models import Site

from django.utils.translation import ugettext_lazy as _
from django import forms
import os, logging

import shutil


def uniqify(seq):
    # Not order preserving
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()
class Storage(models.Model):
	site = models.ForeignKey(Site, unique=True)
	total = models.IntegerField(default=0)
	balance = models.IntegerField(default=0, editable=False)
	free  = models.IntegerField(default=0, editable=False)
	mount = models.CharField("Partition", max_length=100, default="/dev/sdb1")
	share_path = models.CharField("Path of Share",max_length=100)
	def __str__(self):
		return str(self.id)
	def save(self):
		if not self.id:
			self.balance =  self.free =self.total
			
		super(Storage, self).save()
		
		

class SambaUser(models.Model):
	user = models.ForeignKey(User, unique=True)
	quota = models.IntegerField(help_text="Enter in digits, the quota in MB, viz for 10 GB  its 10000, do not use commas")
	used = models.IntegerField(default=0)
	percent = models.IntegerField(default=0)
	path = models.CharField(max_length=700, blank =True)
	
	is_disabled = models.BooleanField(default=False)

	def __unicode__(self):
		return self.user.username
		
	def save(self):
		self.path = "/home/" + self.user.username +"/"
		super(SambaUser,self).save()
		total_quota = sum([user.quota for user in SambaUser.objects.all()])
		try:
			storage = Storage.objects.all()[0]
			storage.balance = storage.total - total_quota
			
			
			storage.save()
		except Storage.DoesNotExist, IndexError:
			raise forms.ValidationError(_(u'Make Sure you set up Storage'))
		super(SambaUser,self).save()
			

class Share(models.Model):
    share = models.CharField(max_length=30, unique=True)
    read = models.ManyToManyField( SambaUser, blank =True, limit_choices_to = {'is_disabled': False}, related_name="readonly")
    write = models.ManyToManyField(SambaUser, limit_choices_to = {'is_disabled': False},  related_name="write")
    old_shares = models.CharField(max_length=200, default='  ', editable=False, null =True, blank =True)
    def __str__(self):
	return self.share
    
    
	    
 

def create_share(share):
    
    
    
    storage = Storage.objects.all()[0]
    path =storage.share_path
	    
    share.save()
    file_path=path+"/"+share.share
    os.mkdir(file_path)
    
    
	
    reads = share.read.all()
    writes = share.write.all()
    command = "sudo smbldap-groupadd -a %s" %  share.share
   
    os.system(command)
    
    
    reader=[read.user.username for read in reads]
    writer =[read.user.username for read in writes]
	
    reader.extend(writer)
    reader = uniqify(reader)
    share.old_shares = ','.join(reader)
    share.save()
    readstring =','.join(reader)
    command = 'sudo smbldap-groupmod -m %s %s' % (readstring, share.share)
   
    os.system(command)
    filename = "/etc/samba/shares.smb.conf"
    command ="sudo chmod 775 %s" %( file_path)   
    os.system(command)
    command ="sudo chgrp -R %s %s " %( share.share,  file_path) 
    os.system(command)
    command ="sudo chmod g+s %s" %(   file_path) 
    os.system(command)
    
    f= open(filename, 'w')
    shares =Share.objects.all()
       
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
	
	
    share.save()
    command ="sudo /etc/init.d/samba reload"
  
    os.system(command)
	    
	

def share_edit(share):
    
   
    
    
    storage = Storage.objects.all()[0]
    path =storage.share_path
	
    
    
	    
	
	
    reads = share.read.all()
    writes = share.write.all()
    old_shares = share.old_shares
    old_shares = old_shares.split(",")
    
  
    
    
    reader=[read.user.username for read in reads]
    writer =[read.user.username for read in writes]
	
    reader.extend(writer)
    reader = uniqify(reader)
    for ol in old_shares:
	if ol not in reader:
	    command = "smb-ldap-groupmod -x %s %s" %( ol, share.share)
	    os.system(command)
    
    newreader=[] 
    for read in reader:
	if read not in old_shares:
	    newreader.append(read)
	
    
    
    share.old_shares = ','.join(reader)
    
    readstring =','.join(newreader)
    if len(readstring)>1:
	command = 'sudo smbldap-groupmod -m %s %s' % (readstring, share.share)
	
	os.system(command)
    filename = "/etc/samba/shares.smb.conf"
    f= open(filename, 'w')
    shares =Share.objects.all()
    share.save()   
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
    
    
def dir_delete(folder_path):
    for file_object in os.listdir(folder_path):
	file_object_path = os.path.join(folder_path, file_object)
	if os.path.isfile(file_object_path):
	    os.unlink(file_object_path)
	else:
	    shutil.rmtree(file_object_path)
    shutil.rmtree(folder_path)

    
def deleteshare(share):
    
    name =share.share
    storage = Storage.objects.all()[0]
    path =storage.share_path
    
    command = "sudo smbldap-groupdel %s" % name
    os.system(command) 
    filepath = path +"/"+name
    command = "sudo rm -r %s" % filepath
    os.system(command)
    share.delete()
    filename = "/etc/samba/shares.smb.conf"
    f= open(filename, 'w')
    
    shares =Share.objects.all()
       
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

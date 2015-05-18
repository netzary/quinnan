from django.db import models
from django.contrib.auth.models import *
# Create your models here.

class User_Root(models.Model):
    user = models.ForeignKey(User)
    folders = models.ManyToManyField(Folder)
    

    def __str__(self):
	return self.user.username
	
class Folder(models.Model):
    
    is_root = models.BooleanField(default=False)
    parent = models.ForeignKey(Folder, null=True, blank=True)
    name = models.CharField(max_length=256)
    path= models.CharField(max_length=324)
    
    def __str__(self):
	return self.name
	
    
    
class File_(models.Model):
    parent = models.ForeignKey(Folder)
    name = models.CharField(max_length=256)
    path= models.CharField(max_length=324)
    size = models.IntegerField()

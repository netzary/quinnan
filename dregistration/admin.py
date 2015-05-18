from django.contrib import admin

from models import *






class  RegistrationProfileAdmin(admin.ModelAdmin):
	pass
admin.site.register( RegistrationProfile, RegistrationProfileAdmin)
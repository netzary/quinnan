from django import template
import os
register = template.Library()

from settings import STATIC_URL as static
from settings import PROJECT_PATH as ROOT
def iconify(path):
    """
    Simple kb/mb/gb size snippet for templates:
    
    {{ product.file.size|sizify }}
    """
    #value = ing(value)
    if os.path.isdir(path):
	return "/static/icons/folder.png"
    elif os.path.isfile(path):
	path, ext=os.path.splitext(path)
	ext=ext.lstrip(".")
	ext =ext.lower()
	icons= os.listdir(os.path.join(ROOT,"static_media/icons"))
	filenames=[(os.path.splitext(f)[0]).lower() for f in icons]
	if ext in filenames:
	    return "/static/icons/%s.%s" %(ext, "png")
	else:
	    return "/static/icons/%s.%s" %("file", "png")    
    else:
	return "/static/icons/%s.%s" %("file", "png") 
	
register.filter('iconify', iconify)

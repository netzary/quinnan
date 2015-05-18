import os

def get_dir_size(root):
    size = 0
    for path, dirs, files in os.walk(root):
        for f in files:
			try:
				size +=  os.path.getsize( os.path.join( path, f ) )
			except Exception, err:
				pass

    return size/(1024*1024)

import os, os.path, sys, socket, time, datetime
import shutil
import paramiko
from nacm1.views import *

def backup_conf():
	backup_dir = "/backup/"
	temp_dir = "/uploads/"
	now = datetime.datetime.now()
	if not os.path.exists(backup_dir):
		os.makedirs(backup_dir)
	ssh_client = paramiko.SSHClient()
	file_paths = get_all_file_paths(backup_dir)
	stdin, stdout, stderr = ssh_client.exec_command('/export')
	backup = stdout.read()
	# filename = "%s_%.2i-%.2i-%i_%.2i-%.2i-%.2i" % (filename_complete,now.day,now.month,now.year,now.hour,now.minute,now.second)
	filename = "%s" % (filename_complete)
	ff = open(filename, 'a')
	ff.write(backup)
	ff.close()
	zipper = shutil.make_archive(file_name, 'zip', backup_dir)

	# with ZipFile('my_python_files.zip','a') as zip:
	# 	# writing each file one by one
	# 	for file in file_paths:
	# 		zip.write(file)
	# ff.close()

	ff.close()
	value_bak=2

def get_all_file_paths(directory):

    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # returning all file paths
    return file_paths

import paramiko
import os, os.path, sys, socket, time, datetime
import shutil
from django.conf import settings
from shutil import make_archive
import re
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from ..functions.functions import handle_uploaded_file
from ..models import Connect
from ..forms import NacmForm, IpFormset
from .. import models
from django.utils.encoding import smart_str

def backup(request):
	ip_list = []
	# backup_dir = os.getcwd()+"backup/"
	bak_dir = "backup/"
	backup_dir = os.path.join(settings.MEDIA_ROOT, bak_dir)
	now = datetime.datetime.now()
	file_download = "%s_%.2i-%.2i-%i" % ('conf_backup',now.day,now.month,now.year)
	file_name = "%s" % ('conf_backup')
	if request.method == 'POST':
		formm = NacmForm(request.POST or None)
		ipform = IpFormset(request.POST)
		userValue = formm['username'].value()
		passValue = formm['password'].value()
		confValue = formm['conft'].value()

		if ipform.is_valid():
			simpanForm = formm.save()
			for form in ipform:
				ipaddr = form.cleaned_data.get('ipaddr')
				vendor = form.cleaned_data.get('vendor')
				filename_prefix = ipaddr+'.rsc'
				filename_complete = os.path.join(backup_dir, filename_prefix)
				collect_config = "<b>Backup on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
				print ("true")
				# print ipaddr
				try:
					ssh_client = paramiko.SSHClient()
					ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue)

					if request.POST.get("backup"):
						if not os.path.exists(backup_dir):
							oldmask = os.umask(0)
							os.makedirs(backup_dir, 0o755)
							os.umask(oldmask)
						
						# file_paths = get_all_file_paths(backup_dir)
						# stdin, stdout, stderr = ssh_client.exec_command('/export')
						# stdin, stdout, stderr = ssh_client.exec_command('show run')
						stdin, stdout, stderr = ssh_client.exec_command(eval(vendor.sett_backup))
						backup_conf = stdout.read()

						filename = "%s" % (filename_complete)
						ff = open(os.path.join(settings.MEDIA_ROOT, filename), 'wb')
						print(settings.MEDIA_ROOT)
						ff.write(backup_conf)
						ff.close()
						# value_bak="next_zip"
						# print('sembaranglah')
					messages.success(request, "sucess backup configuration")
					simpanForm.conft = "backup configuration"
					simpanIp = form.save(commit=False)
					simpanIp.connect_id = simpanForm
					print (simpanIp)
					simpanIp.save()

					simpanForm.save()
				except paramiko.AuthenticationException:
					error_conf(request, collect_config, "</br>Authentication failed, please verify your credentials")
				except paramiko.SSHException as sshException:
					error_conf(request, collect_config, "</br>Could not establish SSH connection: %s" % sshException)
				except socket.timeout as e:
					error_conf(request, collect_config, "</br>Connection timed out")
				except Exception as e:
					ssh_client.close()
					error_conf(request, collect_config, "</br>Exception in connecting to the server")

	# elif value_bak=="next_zip":
		# content_type = request.headers['content-type']
		# content_len = request.headers['content-length']			
		# zipper = make_archive(file_name, "zip", backup_dir)
		try:
			
			zipper = shutil.make_archive(base_name = os.path.join(settings.MEDIA_ROOT,file_download), format = 'zip', root_dir = backup_dir, base_dir = './' )
			print(zipper)
			shutil.rmtree(backup_dir)
			resp = HttpResponse(open(zipper, 'rb').read(), content_type = "application/zip")
			# resp = HttpResponse(content_type = "application/zip")
			# resp['Content-Type'] = 'application/zip'
			# resp['Content-Length'] = len(zipper.encode('utf-8'))
			# ..and correct content-disposition
			# resp['X-Sendfile'] = smart_str(os.path.join(settings.MEDIA_ROOT,file_name+'.zip'))
			# resp['X-Sendfile'] = open(zipper, 'rb'), content_type = "application/zip"
			resp['Content-Disposition'] = 'attachment; filename=%s.zip' % smart_str(file_download)
			# resp['X-Sendfile'] = smart_str(os.path.join(settings.MEDIA_ROOT,file_download+'.zip'))
			resp['Set-Cookie'] = 'fileDownload=true; Path=/'
			
			del_dir = os.getcwd()
			# os.remove(del_dir+'/'+file_name+'.zip')
			os.remove(os.path.join(settings.MEDIA_ROOT,file_download+'.zip'))

			formm.save()

			return resp
		except IOError as e:
			print ("Unable to copy file. %s"%e)
			messages.error(request, "Unable to copy file. %s"%e)
			# 	make_zip(file_name,backup_dir,file_download,value_bak)
			# formm.save()
		return HttpResponseRedirect('/backup')
	else:
		formm = NacmForm()
		ipform = IpFormset()
		return render(request, 'backup.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform, 'file_download':file_download})


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

def error_conf(request, collect_config, error1):
	conf_error = collect_config+error1
	messages.error(request, conf_error)
	result_flag = False
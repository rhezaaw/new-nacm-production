import paramiko
import os, os.path, time
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from ..models import Connect
from ..forms import NacmForm, IpFormset, UploadForm
from .. import models
from scp import SCPClient
from django.conf import settings

def restore(request):
	ip_list = []

	if request.method == 'POST':
		formm = NacmForm(request.POST or None)
		ipform = IpFormset(request.POST)
		upform = UploadForm(request.POST,request.FILES)
		userValue = formm['username'].value()
		passValue = formm['password'].value()
		up_dir = "upload/"
		upload_dir = os.path.join(settings.MEDIA_ROOT, up_dir)
		ssh_client = paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh_client.load_system_host_keys()
		if ipform.is_valid():
			simpanForm = formm.save()
			for form in ipform:
				ipaddr = form.cleaned_data.get('ipaddr')
				vendor = form.cleaned_data.get('vendor')
				fileconf = ipaddr+'.rsc'
				collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
				print ("true")
				# ssh_client = paramiko.SSHClient()
				# ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				# ssh_client.load_system_host_keys()
				# ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue)
				# remote_conn=ssh_client.invoke_shell()
				# shell = remote_conn.recv(65535)
				config_read = str(vendor.sett_restore)	
				if request.POST.get("upload"):
					localfilepath = os.getcwd()
					remotefilepath = 'auto.cfg'
					print('test wanna upload something....')
					mediapath = upload_dir
					# try:
					for count, x in enumerate(request.FILES.getlist("files")):
						def process(f):
							with open( upload_dir + f.name, 'wb+') as destination:
								for chunk in f.chunks():
									destination.write(chunk)

							def files(mediapath):
								for file in os.listdir(mediapath):
									if os.path.isfile(os.path.join(mediapath, file)):
										files = file.rsplit('.',1)[0]
										yield files

							for ftp_con in files(mediapath):
								print (ftp_con)
								fileconf = ftp_con+'.rsc'
								# config_read = str(vendor.sett_restore)	
								print(fileconf)
								ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
								ssh_client.load_system_host_keys()
								ssh_client.connect(hostname=ftp_con,username=userValue,password=passValue)
								print("upload")
								scp = SCPClient(ssh_client.get_transport())
								scp.put(mediapath + fileconf, fileconf)
								# scp.close()
								# if config_read != '':
								# print(eval(config_read))
								# ssh_client.exec_command('adsd')	
								# remote_conn.send('configure terminal\n')
								# remote_conn.send('ip route 210.200.210.0 255.255.255.0 50.50.50.2')
								scp.close()
								time.sleep(1)				
								os.remove(mediapath+fileconf)
								# time.sleep(5)
						# print (str(x+"ini proses x"))
						process(x)
					# finally:
					# ssh_client.exec_command('tes')
						# time.sleep(5)
					ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue)
					remote_conn=ssh_client.invoke_shell()
					# shell = remote_conn.recv(65535)
					config_send = eval(config_read)
					collect_config = collect_config + config_send+"</br>" 
					try:
						# stdin, stdout, stderr = ssh_client.exec_command(config_send+"\n")
						ssh_client.exec_command(config_send+"\n\r")
						time.sleep(1)
						ssh_client.exec_command(" \r\n")
						# ssh_client.exec_command("\n")
						time.sleep(1)
						print('coba exec')
						# results = stdout.read()
						# print (str(results))
					except:
						try:
							# remote_conn.send(config_send+"\n")
							# remote_conn.send(config_read+'\n\r')
							print ('coba interactive')
							print (config_send+'\n')
							remote_conn.send(config_send+'\n\r')
							time.sleep(1)
							remote_conn.send(' \r\n')
							# remote_conn.send('ip route 210.200.210.0 255.255.255.0 50.50.50.2\n')
							time.sleep(1)
							results = remote_conn.recv(65535)
							print ('coba interactive 2')
							

							# print (results)
						except paramiko.ssh_exception.SSHException as e:
							print("error paramiko %s" % e)
						# except:
						# 	print('error paramikone cook')
					# messages.success(request, collect_config)
					print('testlah habis upload')
				# return HttpResponseRedirect('/restore')
				messages.success(request, "sucess restore configuration")
				simpanForm.conft = "restore configuration"
				simpanIp = form.save(commit=False)
				simpanIp.connect_id = simpanForm
				print (simpanIp)
				simpanIp.save()
				simpanForm.save()
				formm.save()

			return HttpResponseRedirect('/restore')
	else:
		formm = NacmForm()
		ipform = IpFormset()
		upform = UploadForm()
		return render(request, 'restore.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform, 'upform': upform })
import paramiko
import os, os.path, time
import re
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from ..models import Connect
from ..forms import NacmForm, IpFormset
from .. import models

def config_codeBased(request):

	ip_list = []
	status = ''
	value_bak = 1
	# backup_dir = "/var/www/nacm/backup/"

	if request.method == 'POST':
		formm = NacmForm(request.POST or None)
		ipform = IpFormset(request.POST)
		userValue = formm['username'].value()
		passValue = formm['password'].value()
		confValue = formm['conft'].value()

		if ipform.is_valid() and formm.is_valid():
			simpanForm = formm.save()
			for form in ipform:
				ipaddr = form.cleaned_data.get('ipaddr')
				vendor = form.cleaned_data.get('vendor')
				collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
				print (vendor)
				try:
					ssh_client = paramiko.SSHClient()
					ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue)
					# ssh_client.exec_command(confValue)
					remote_conn=ssh_client.invoke_shell()
					output = remote_conn.recv(65535)
					collect_config_print = collect_config + confValue+"</br>"
					try:
						print("try exec command")
						ssh_client.exec_command(confValue+"\n")
						time.sleep(1)
					except:
						try:
							print("try shell interactive")
							remote_conn.send(confValue+"\n")
							time.sleep(1)
						except:
							print ("error paramiko")
					# print (output)
					# print (stdout.read())
					simpanForm.conft = collect_config_print
					simpanIp = form.save(commit=False)
					simpanIp.connect_id = simpanForm
					print (simpanIp)
					simpanIp.save()
					
					simpanForm.save()
					messages.success(request, collect_config_print)
				except paramiko.AuthenticationException:
					error_conf(request, collect_config, "</br>Authentication failed, please verify your credentials")
				except paramiko.SSHException as sshException:
					error_conf(request, collect_config, "</br>Could not establish SSH connection: %s" % sshException)
				except socket.timeout as e:
					error_conf(request, collect_config, "</br>Connection timed out")
				except Exception as e:
					ssh_client.close()
					error_conf(request, collect_config, "</br>Exception in connecting to the server")
		return HttpResponseRedirect('code_based')
	else:
		formm = NacmForm()
		ipform = IpFormset()
		return render(request, 'config/code_based.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform, 'status': status })

def error_conf(request, collect_config, error1):
	conf_error = collect_config+error1
	messages.error(request, conf_error)
	result_flag = False

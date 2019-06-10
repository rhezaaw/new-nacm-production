import paramiko
import os, os.path, time, socket
import re
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from ..models import Connect
from ..forms import NacmForm, IpFormset
from .. import models
from netaddr import IPAddress, IPNetwork

def vlan(request):
	ip_list = []
	status = ''
	value_bak = 1
	count_form = 0

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
				vlans_id = (request.POST.getlist('vlan_id'))
				vlans_name = (request.POST.getlist('vlan_name'))
				interface = str(request.POST['interface'])
				collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
				print (vendor)
				
				try:
					ssh_client = paramiko.SSHClient()
					ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue,look_for_keys=False, allow_agent=False, timeout=5)
					remote_conn=ssh_client.invoke_shell()
					shell = remote_conn.recv(65535)
					# connect_dev(ssh_client,ipaddr,userValue,passValue)
					config_read = str(vendor.sett_vlan)
					# split memakai \r dulu
					array_read = config_read.split('\r')
					# hasilnya akan ada \n
					output_line = ""
					# print (array_read)
					for x in range(len(vlans_id)):
						vlan_id = vlans_id[x]
						vlan_name = vlans_name[x]
						# interface = interfaces[x]
						for line in array_read:
							# menghilangkan \n
							new_line = re.sub(r'\n','',line)
							# print new_line
							# akan error karena ada nilai kosong dan eval tidak bisa membacanya
							# sehingga mengeleminasi nilai kosong
							if new_line != '':
								config_send = eval(new_line)
								collect_config = collect_config + config_send+"</br>" 
								print(config_send+" ini config send")
								try:
									stdin, stdout, stderr = ssh_client.exec_command(config_send+"\n")
									time.sleep(1)
									results = stdout.read()
									print (str(results))
								except:
									try:
										remote_conn.send(config_send+"\n")
										time.sleep(1)
										results = remote_conn.recv(65535)
										print (results.decode('ascii'))
										# print (results)
									except:
										print("error paramiko")

					messages.success(request, collect_config)
					count_form = count_form + 1	
					collect_data = collect_data + collect_config
					if count_form == len(ipform):
						simpanForm.conft = collect_data
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

		return HttpResponseRedirect('vlan')
	else:
		formm = NacmForm()
		ipform = IpFormset()
		return render(request, 'config/vlan.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform, 'status': status })

def error_conf(request, collect_config, error1):
	conf_error = collect_config+error1
	messages.error(request, conf_error)
	result_flag = False
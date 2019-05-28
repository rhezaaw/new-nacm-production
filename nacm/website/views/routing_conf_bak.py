import paramiko
import os, os.path, sys, socket, time
import re
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from ..models import Connect
from ..forms import NacmForm, IpFormset, UploadForm
from .. import models
from netaddr import IPAddress, IPNetwork

def config_static(request):
	ip_list = []
	status = ''
	value_bak = 1

	if request.method == 'POST':
		formm = NacmForm(request.POST or None)
		ipform = IpFormset(request.POST)
		upform = UploadForm(request.POST,request.FILES)
		userValue = formm['username'].value()
		passValue = formm['password'].value()
		destination = str(request.POST['destination'])
		prefix = str(request.POST['prefix'])
		gateway = str(request.POST['gateway'])
		localfilepath = os.getcwd()
		staticDir = localfilepath+"/plugin/config/routing/static/"
		# ssh_client = paramiko.SSHClient()
		if ipform.is_valid() and formm.is_valid():
			simpanForm = formm.save()

			for form in ipform:
				ipaddr = form.cleaned_data.get('ipaddr')
				vendor = form.cleaned_data.get('vendor')
				networks = str(destination+"/"+prefix)
				netmask = IPNetwork(networks).netmask
				collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
				print (netmask)
				print (prefix)
				# print (localfilepath)
				try:
					ssh_client = paramiko.SSHClient()
					ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue,look_for_keys=False, allow_agent=False, timeout=5)
					remote_conn=ssh_client.invoke_shell()
					shell = remote_conn.recv(65535)
					# connect_dev(ssh_client,ipaddr,userValue,passValue)
					config_read = str(vendor.sett_static_routing)
					# split memakai \r dulu
					array_read = config_read.split('\r')
					# hasilnya akan ada \n
					output_line = ""
					# print (array_read)

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
					
					ssh_client.close()
					# paramiko.util.log_to_file(os.path.join(settings.MEDIA_ROOT,"filename.log"))
					simpanIp = form.save(commit=False)
					simpanIp.connect_id = simpanForm
					print (simpanIp)
					simpanIp.save()

					simpanForm.save()

				except paramiko.AuthenticationException:
					# print ("Authentication failed, please verify your credentials")
					# conf_error = collect_config+"</br>Authentication failed, please verify your credentials"
					# messages.error(request, conf_error)
					# result_flag = False
					error_conf(request, collect_config, "</br>Authentication failed, please verify your credentials")
				except paramiko.SSHException as sshException:
					error_conf(request, collect_config, "</br>Could not establish SSH connection: %s" % sshException)
				except socket.timeout as e:
					error_conf(request, collect_config, "</br>Connection timed out")
				except Exception as e:
					ssh_client.close()
					error_conf(request, collect_config, "</br>Exception in connecting to the server")

		return HttpResponseRedirect('routing_static')
		# return render(request, 'config/routing_static.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform, 'status': status, 'output1':output1 })
	else:
		formm = NacmForm()
		ipform = IpFormset()
		return render(request, 'config/routing_static.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform, 'status': status})


def config_dynamic(request):
	ip_list = []
	status = ''
	value_bak = 1

	if request.method == 'POST':
		formm = NacmForm(request.POST or None)
		ipform = IpFormset(request.POST)
		upform = UploadForm(request.POST,request.FILES)
		userValue = formm['username'].value()
		passValue = formm['password'].value()
		confValue = formm['conft'].value()
		rd_select = str(request.POST['dynamic_routing_select'])
		print(rd_select)
		id_ospf = str(request.POST['id_ospf'])
		router_id = str(request.POST['rid_ospf'])
		print(router_id)
		network = str(request.POST['network_ospf'] or request.POST['network_ripv1'] or request.POST['network_ripv2'])
		print (network)
		prefix = str(request.POST['prefix_ospf'] or request.POST['prefix_ripv1'] or request.POST['prefix_ripv2'])
		area = str(request.POST['area'])
		interface_ospf = str(request.POST['interface_ospf'])
		interface_ripv1 = str(request.POST['interface_ripv1'])
		interface_ripv2 = str(request.POST['interface_ripv2'])
		if ipform.is_valid() and formm.is_valid():
			simpanForm = formm.save()
			for form in ipform:
				ipaddr = form.cleaned_data.get('ipaddr')
				vendor = form.cleaned_data.get('vendor')
				networks = netmask = wildcard = ""
				collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
				if prefix != '':
					networks = str(network+"/"+prefix)
					print(networks)
					netmask = IPNetwork(networks).netmask
					print(netmask)
					wildcard = IPNetwork(networks).hostmask
					print(wildcard)
					print (vendor)
				try:
					ssh_client = paramiko.SSHClient()
					ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue)
					remote_conn=ssh_client.invoke_shell()
					output = remote_conn.recv(65535)
					config_read = None
					if rd_select == 'ospf':
						config_read = str(vendor.sett_dynamic_routing_ospf)
					elif rd_select == 'ripv1':
						config_read = str(vendor.sett_dynamic_routing_ripv1)
					elif rd_select == 'ripv2':
						config_read = str(vendor.sett_dynamic_routing_ripv2)
					# split memakai \r dulu
					array_read = config_read.split('\r')
					# hasilnya akan ada \n
					counter = 0
					for line in array_read:
						# menghilangkan \n
						new_line = re.sub(r'\n','',line)
						# print new_line
						# akan error karena ada nilai kosong dan eval tidak bisa membacanya
						# sehingga mengeleminasi nilai kosong
						if new_line != '':
							config_send = eval(new_line)
							collect_config = collect_config + config_send+"</br>" 
							print(config_send)
							try:
								ssh_client.exec_command(config_send+"\n")
								time.sleep(1)
							except:
								try:
									if counter == 0:
										print("try shell interactive")
										counter+=1
									remote_conn.send(config_send+"\n")
									time.sleep(1)
								except:
									print("error paramiko")
					
					messages.success(request, collect_config)
					ssh_client.close()
					
					# paramiko.util.log_to_file("filename.log")
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

		return HttpResponseRedirect('routing_dynamic')
	else:
		formm = NacmForm()
		ipform = IpFormset()
		return render(request, 'config/routing_dynamic.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform, 'status': status })

def config_bgp(request):
	ip_list = []
	status = ''
	value_bak = 1

	if request.method == 'POST':
		formm = NacmForm(request.POST or None)
		ipform = IpFormset(request.POST)
		upform = UploadForm(request.POST,request.FILES)
		userValue = formm['username'].value()
		passValue = formm['password'].value()
		confValue = formm['conft'].value()
		bgp_name = str(request.POST['bgp_name'])
		asn = str(request.POST['bgp_asn'])
		router_id = str(request.POST['bgp_router_id'])
		neighbor_address = str(request.POST['bgp_neighbor_address'])
		neighbor_asn = str(request.POST['bgp_neighbor_asn'])
		network = str(request.POST['bgp_network'])
		prefix = str(request.POST['bgp_prefix'])
		if ipform.is_valid() and formm.is_valid():
			simpanForm = formm.save()
			for form in ipform:
				ipaddr = form.cleaned_data.get('ipaddr')
				vendor = form.cleaned_data.get('vendor')
				collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
				networks = netmask = wildcard = ""
				if prefix != '':
					networks = str(network+"/"+prefix)
					print(networks)
					netmask = IPNetwork(networks).netmask
					print(netmask)
					wildcard = IPNetwork(networks).hostmask
					print(wildcard)
					print (vendor)
				try:
					ssh_client = paramiko.SSHClient()
					ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue,look_for_keys=False, allow_agent=False, timeout=5)
					remote_conn=ssh_client.invoke_shell()
					shell = remote_conn.recv(65535)
					# connect_dev(ssh_client,ipaddr,userValue,passValue)
					config_read = str(vendor.sett_dynamic_routing_bgp)
					# split memakai \r dulu
					array_read = config_read.split('\r')
					# hasilnya akan ada \n
					output_line = ""
					# print (array_read)

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
					
					ssh_client.close()
					# paramiko.util.log_to_file(os.path.join(settings.MEDIA_ROOT,"filename.log"))
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
		return HttpResponseRedirect('routing_bgp')
	else:
		formm = NacmForm()
		ipform = IpFormset()
		return render(request, 'config/routing_bgp.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform, 'status': status })

def error_conf(request, collect_config, error1):
	conf_error = collect_config+error1
	messages.error(request, conf_error)
	result_flag = False

def connect_dev(ipaddr,userValue,passValue):
	ssh_client = paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue,look_for_keys=False, allow_agent=False, timeout=5)
	remote_conn=ssh_client.invoke_shell()
	shell = remote_conn.recv(65535)
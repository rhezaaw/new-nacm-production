import paramiko
import os, os.path, sys, socket, time
import re
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.views import View
from netaddr import IPAddress, IPNetwork
from ..models import Connect
from ..forms import NacmForm, IpFormset, UploadForm
from .. import models

# class config_static(View):
# 	ip_list = []
# 	status = ''

# 	def post(self, request, *args, **kwargs):
# 		formm = NacmForm(request.POST or None)
# 		ipform = IpFormset(request.POST)
# 		userValue = formm['username'].value()
# 		passValue = formm['password'].value()

# 		if ipform.is_valid() and formm.is_valid():
# 			simpanForm = formm.save()

# 			for form in ipform:
# 				ipaddr = form.cleaned_data.get('ipaddr')
# 				vendor = form.cleaned_data.get('vendor')
# 				con = connect_management()
# 				con.connect_dev(request, ipaddr, userValue, passValue, vendor, form, simpanForm)

# 		return HttpResponseRedirect('routing_static')
		
# 	def get(self, request, *args, **kwargs):
# 		formm = NacmForm()
# 		ipform = IpFormset()
# 		return render(request, 'config/routing_static.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform, 'status': self.status})

class config_static(View):
	ip_list = []
	status = ''
	
	def post(self, request, *args, **kwargs):
		formm = NacmForm(request.POST)
		ipform = IpFormset(request.POST)
		upform = UploadForm(request.POST,request.FILES)
		userValue = formm['username'].value()
		passValue = formm['password'].value()
		destination = str(request.POST['destination'])
		prefix = str(request.POST['prefix'])
		gateway = str(request.POST['gateway'])

		if ipform.is_valid() and formm.is_valid():
			print ('is valid bruh')
			formm.cleaned_data['conft'] = 'ip static route'
			simpanForm = formm.save()
			collect_data = ""
			count_form = 0
			for form in ipform:
				ipaddr = form.cleaned_data.get('ipaddr')
				vendor = form.cleaned_data.get('vendor')
				networks = str(destination+"/"+prefix)
				netmask = IPNetwork(networks).netmask
				collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
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
					# 	conf_list.append(list)
					# print (conf_list)
					count_form = count_form + 1	
					collect_data = collect_data + collect_config
					if count_form == len(ipform):
						simpanForm.conft = collect_data
					print (collect_config)
					messages.success(request, collect_config)
					# NacmForm(initial={'conft': 'other_field_initial'})
					ssh_client.close()
					
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
					error_conf(request, collect_config, "</br>Exception in connecting to the server: %s" % e)

		return HttpResponseRedirect('routing_static')
	def get(self, request, *args, **kwargs):
		formm = NacmForm()
		ipform = IpFormset()
		return render(request, 'config/routing_static.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform})


def config_dynamic(request):
	ip_list = []
	status = ''
	value_bak = 1
	count_form = 0

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
		# for x in test:
		# 	print (x)
		# networkx = (request.POST.getlist('network_ospf') or request.POST.getlist('network_ripv1') or request.POST.getlist('network_ripv2'))
		if rd_select == 'ospf':
			networkx = (request.POST.getlist('network_ospf'))
			prefixs = (request.POST.getlist('prefix_ospf'))
		elif rd_select == 'ripv1':
			networkx = (request.POST.getlist('network_ripv1'))
			prefixs = (request.POST.getlist('prefix_ripv1'))
		elif rd_select == 'ripv2':
			networkx = (request.POST.getlist('network_ripv2'))
			prefixs = (request.POST.getlist('prefix_ripv2'))
		# networkx = (request.POST.getlist('network_ospf') or request.POST.getlist('network_ripv1') or request.POST.getlist('network_ripv2'))
		# prefixs = (request.POST.getlist('prefix_ospf') or request.POST.getlist('prefix_ripv1') or request.POST.getlist('prefix_ripv2'))
		areas = (request.POST.getlist('area'))
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
					for x in range(len(networkx)):
						if rd_select == 'ospf':
							network = networkx[x]
							prefix = prefixs[x]
							area = areas[x]
						elif rd_select == 'ripv1' or rd_select == 'ripv2':
							network = networkx[x]
							prefix = prefixs[x]
						if prefix != '':
							networks = str(network+"/"+prefix)
							print(networks)
							netmask = IPNetwork(networks).netmask
							print(netmask)
							wildcard = IPNetwork(networks).hostmask
							print(wildcard)
							print (vendor)
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
					
					count_form = count_form + 1	
					collect_data = collect_data + collect_config
					if count_form == len(ipform):
						simpanForm.conft = collect_data
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
					error_conf(request, collect_config, "</br>Exception in connecting to the server :%s" % e)
					print (e)

		return HttpResponseRedirect('routing_dynamic')
	else:
		formm = NacmForm()
		ipform = IpFormset()
		return render(request, 'config/routing_dynamic.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform, 'status': status })

def config_bgp(request):
	ip_list = []
	status = ''
	value_bak = 1
	count_form = 0
	
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
		networkx = (request.POST.getlist('bgp_network'))
		prefixs = (request.POST.getlist('bgp_prefix'))
		if ipform.is_valid() and formm.is_valid():
			simpanForm = formm.save()
			for form in ipform:
				ipaddr = form.cleaned_data.get('ipaddr')
				vendor = form.cleaned_data.get('vendor')
				collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
				networks = netmask = wildcard = ""

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
					for x in range(len(networkx)):
						network = networkx[x]
						print ('test cokk')
						print(network)
						prefix = prefixs[x]
						if prefix != '':
							networks = str(network+"/"+prefix)
							print(networks)
							netmask = IPNetwork(networks).netmask
							print(netmask)
							wildcard = IPNetwork(networks).hostmask
							print(wildcard)
							print (vendor)
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

					count_form = count_form + 1	
					collect_data = collect_data + collect_config
					if count_form == len(ipform):
						simpanForm.conft = collect_data					
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

# def connect_dev(self, ipaddr,userValue,passValue):
# 	ssh_client = paramiko.SSHClient()
# 	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 	ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue,look_for_keys=False, allow_agent=False, timeout=5)
# 	remote_conn=ssh_client.invoke_shell()
# 	shell = remote_conn.recv(65535)

class connect_management():
	def connect_dev(self, request, ipaddr, userValue, passValue, vendor, form, simpanForm):
		destination = str(request.POST['destination'])
		prefix = str(request.POST['prefix'])
		gateway = str(request.POST['gateway'])
		networks = str(destination+"/"+prefix)
		netmask = IPNetwork(networks).netmask
		collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
		try:
			ssh_client = paramiko.SSHClient()
			ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue,look_for_keys=False, allow_agent=False)
			remote_conn=ssh_client.invoke_shell()
			shell = remote_conn.recv(65535)
			# connect_dev(self, ipaddr, userValue, passValue)
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
					collect_config_print = collect_config + config_send+"</br>" 
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
			messages.success(request, collect_config_print)
			simpanForm.conft = collect_config_print
			ssh_client.close()
			# paramiko.util.log_to_file(os.path.join(settings.MEDIA_ROOT,"filename.log"))
			simpanIp = form.save(commit=False)
			simpanIp.connect_id = simpanForm
			print (simpanIp)
			simpanIp.save()

			simpanForm.save()

		except paramiko.AuthenticationException:
			print ("Authentication failed, please verify your credentials")
			conf_error = collect_config+"</br>Authentication failed, please verify your credentials"
			messages.error(request, conf_error)
			result_flag = False
		except paramiko.SSHException as sshException:
			print ("Could not establish SSH connection: %s" % sshException)
			conf_error = collect_config+"</br>Could not establish SSH connection: %s" % sshException
			messages.error(request, conf_error)
			result_flag = False
		except socket.timeout as e:
			print ("Connection timed out")
			conf_error = collect_config+"</br>Connection timed out"
			messages.error(request, conf_error)
			result_flag = False
		except Exception as e:
			print ("Exception in connecting to the server")
			print ("PYTHON SAYS:",e)
			conf_error = collect_config+"</br>Exception in connecting to the server"
			print(e)
			messages.error(request, conf_error)
			result_flag = False
			# self.client.close()
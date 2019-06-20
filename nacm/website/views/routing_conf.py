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


class config_static(View):
	ip_list = []

	# hal yang dilakukan ketika melakukan action POST	
	def post(self, request, *args, **kwargs):
		# mengambil nilai dari form
		formm = NacmForm(request.POST)
		ipform = IpFormset(request.POST)
		upform = UploadForm(request.POST,request.FILES)
		userValue = formm['username'].value()
		passValue = formm['password'].value()
		destinations = (request.POST.getlist('destination'))
		prefixs = (request.POST.getlist('prefix'))
		gateways = (request.POST.getlist('gateway'))

		# jika form valid
		if ipform.is_valid() and formm.is_valid():
			simpanForm = formm.save()
			collect_data = ""
			count_form = 0

			# perulangan data pada form ipform
			for form in ipform:
				ipaddr = form.cleaned_data.get('ipaddr')
				vendor = form.cleaned_data.get('vendor')
				collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
				networks = netmask = wildcard = ""
				# mengkoneksikan ke perangkat via protokol SSH menggunakan library Paramiko
				try:
					ssh_client = paramiko.SSHClient()
					ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					# memasukkan informasi username, password SSH
					ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue,look_for_keys=False, allow_agent=False, timeout=5)
					remote_conn=ssh_client.invoke_shell()
					shell = remote_conn.recv(65535)
					config_read = str(vendor.sett_static_routing)
					# split memakai \r dulu
					array_read = config_read.split('\r')
					# hasilnya akan ada \n
					output_line = ""

					# membuat perulangan pada network yang di advertise, karena pada advertise network menggunakan form dinamis
					for x in range(len(destinations)):
						destination = destinations[x]
						prefix = prefixs[x]
						gateway = gateways[x]
						if prefix != '':
							networks = str(destination+"/"+prefix)
							print(networks)
							netmask = IPNetwork(networks).netmask
							print(netmask)
							wildcard = IPNetwork(networks).hostmask

						# membaca code tiap line
						for line in array_read:
							# menghilangkan \n
							new_line = re.sub(r'\n','',line)
							# akan error karena ada nilai kosong dan eval tidak bisa membacanya
							# sehingga mengeleminasi nilai kosong
							if new_line != '':
								config_send = eval(new_line)
								collect_config = collect_config + config_send+"</br>" 
								print(config_send+" ini config send")
								# mengirim perintah yang akan dikonfig
								# menggunakan non-interactive shell
								try:
									stdin, stdout, stderr = ssh_client.exec_command(config_send+"\n")
									time.sleep(1)
									results = stdout.read()
									print (str(results))
								except:
									# jika gagal menggunakan interactive shell
									try:
										remote_conn.send(config_send+"\n")
										time.sleep(1)
										results = remote_conn.recv(65535)
										print (results.decode('ascii'))
									except:
										print("error paramiko")

					# menyimpan data ke sqlite
					count_form = count_form + 1	
					collect_data = collect_data + collect_config
					if count_form == len(ipform):
						simpanForm.conft = collect_data
					print (collect_config)
					messages.success(request, collect_config)
					ssh_client.close()
					
					simpanIp = form.save(commit=False)
					simpanIp.connect_id = simpanForm
					print (simpanIp)
					simpanIp.save()
					simpanForm.save()

				# jika gagal terkoneksi
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
	
	# hal yang dilakukan ketika melakukan action GET
	def get(self, request, *args, **kwargs):
		formm = NacmForm()
		ipform = IpFormset()
		return render(request, 'config/routing_static.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform})


class config_dynamic(View):
	ip_list = []

	# hal yang dilakukan ketika melakukan action POST
	def post(self, request, *args, **kwargs):

		# mengambil nilai dari form
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

		# kondisi menentukan routing dynamic yang dipilih
		if rd_select == 'ospf':
			networkx = (request.POST.getlist('network_ospf'))
			prefixs = (request.POST.getlist('prefix_ospf'))
		elif rd_select == 'ripv1':
			networkx = (request.POST.getlist('network_ripv1'))
			prefixs = (request.POST.getlist('prefix_ripv1'))
		elif rd_select == 'ripv2':
			networkx = (request.POST.getlist('network_ripv2'))
			prefixs = (request.POST.getlist('prefix_ripv2'))

		areas = (request.POST.getlist('area'))
		interface_ospf = str(request.POST['interface_ospf'])
		interface_ripv1 = str(request.POST['interface_ripv1'])
		interface_ripv2 = str(request.POST['interface_ripv2'])

		# jika form valid
		if ipform.is_valid() and formm.is_valid():
			collect_data = ""
			count_form = 0
			simpanForm = formm.save()

			# perulangan data pada form ipform
			for form in ipform:
				ipaddr = form.cleaned_data.get('ipaddr')
				vendor = form.cleaned_data.get('vendor')
				networks = netmask = wildcard = ""
				collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"

				# mengkoneksikan ke perangkat via protokol SSH menggunakan library Paramiko
				try:
					ssh_client = paramiko.SSHClient()
					ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					# memasukkan informasi username, password SSH
					ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue)
					remote_conn=ssh_client.invoke_shell()
					output = remote_conn.recv(65535)
					config_read = None
					# menentukan routing dynamic yang digunakan dan membaca template syntax yang tersimpan dari database
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

					# membuat perulangan pada network yang di advertise, karena pada advertise network menggunakan form dinamis
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

						# membaca code tiap line
						for line in array_read:
							# menghilangkan \n
							new_line = re.sub(r'\n','',line)
							# akan error karena ada nilai kosong dan eval tidak bisa membacanya
							# sehingga mengeleminasi nilai kosong
							if new_line != '':
								config_send = eval(new_line)
								collect_config = collect_config + config_send+"</br>" 
								print(config_send)

								# mengirim perintah yang akan dikonfig
								# menggunakan non-interactive shell
								try:
									ssh_client.exec_command(config_send+"\n")
									time.sleep(1)
								except:
									# jika gagal menggunakan interactive shell
									try:
										if counter == 0:
											print("try shell interactive")
											counter+=1
										remote_conn.send(config_send+"\n")
										time.sleep(1)
									except:
										print("error paramiko")
					
					# menyimpan data ke sqlite
					count_form = count_form + 1	
					collect_data = collect_data + collect_config
					if count_form == len(ipform):
						simpanForm.conft = collect_data
					messages.success(request, collect_config)
					ssh_client.close()
					simpanIp = form.save(commit=False)
					simpanIp.connect_id = simpanForm
					print (simpanIp)
					simpanIp.save()
					simpanForm.save()

				# jika gagal terkoneksi
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

	# hal yang dilakukan ketika melakukan action GET
	def get(self, request, *args, **kwargs):
		formm = NacmForm()
		ipform = IpFormset()
		return render(request, 'config/routing_dynamic.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform })

class config_bgp(View):
	ip_list = []
	
	# hal yang dilakukan ketika melakukan action POST
	def post(self, request, *args, **kwargs):
		# mengambil nilai dari form
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

		# jika form valid
		if ipform.is_valid() and formm.is_valid():
			collect_data = ""
			count_form = 0
			simpanForm = formm.save()

			# perulangan data pada form ipform
			for form in ipform:
				ipaddr = form.cleaned_data.get('ipaddr')
				vendor = form.cleaned_data.get('vendor')
				collect_config = "<b>Configure on "+str(ipaddr)+" | vendor = "+str(vendor)+"</b></br>"
				networks = netmask = wildcard = ""

				# mengkoneksikan ke perangkat via protokol SSH menggunakan library Paramiko
				try:
					ssh_client = paramiko.SSHClient()
					ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					# memasukkan informasi username, password SSH
					ssh_client.connect(hostname=ipaddr,username=userValue,password=passValue,look_for_keys=False, allow_agent=False, timeout=5)
					remote_conn=ssh_client.invoke_shell()
					shell = remote_conn.recv(65535)
					config_read = str(vendor.sett_dynamic_routing_bgp)
					# split memakai \r dulu
					array_read = config_read.split('\r')
					# hasilnya akan ada \n
					output_line = ""

					# membuat perulangan pada network yang di advertise, karena pada advertise network menggunakan form dinamis
					for x in range(len(networkx)):
						network = networkx[x]
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

						# membaca code tiap line
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
								# mengirim perintah yang akan dikonfig
								# menggunakan non-interactive shell
								try:
									stdin, stdout, stderr = ssh_client.exec_command(config_send+"\n")
									time.sleep(1)
									results = stdout.read()
									print (str(results))
								except:
									# jika gagal menggunakan interactive shell
									try:
										remote_conn.send(config_send+"\n")
										time.sleep(1)
										results = remote_conn.recv(65535)
										print (results.decode('ascii'))
										# print (results)
									except:
										print("error paramiko")

					# menyimpan data ke sqlite
					count_form = count_form + 1	
					collect_data = collect_data + collect_config
					if count_form == len(ipform):
						simpanForm.conft = collect_data					
					messages.success(request, collect_config)

					ssh_client.close()
					simpanIp = form.save(commit=False)
					simpanIp.connect_id = simpanForm
					print (simpanIp)
					simpanIp.save()
					simpanForm.save()

				# jika gagal terkoneksi
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

	# hal yang dilakukan ketika melakukan action GET
	def get(self, request, *args, **kwargs):
		formm = NacmForm()
		ipform = IpFormset()
		return render(request, 'config/routing_bgp.html', {'form': formm, 'logins': Connect.objects.all(), 'ipform': ipform })

def error_conf(request, collect_config, error1):
	conf_error = collect_config+error1
	messages.error(request, conf_error)
	result_flag = False



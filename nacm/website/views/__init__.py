import os, os.path
import json
from django.shortcuts import render
from django.http import HttpResponse
from .. import models
from .. import serializers
from rest_framework import generics
from .backup_conf import *
from .code_based_conf import *
from .restore_conf import *
from .routing_conf import *
from .setting_conf import *
from .vlan_conf import *
from ..models import Connect, Ip, c_Setting as settings
ip_list = []

def index(request):
	# if request.method == "GET":
	count_all = Connect.objects.all().count()
	vendor_all = settings.objects.all().count()
	print (count_all)
	context={'count_all':count_all,'vendor_all':vendor_all}
	return render(request, 'index.html',context)

def verifip(request):
	print ("verifikasi ip")

def ip_validation(request):
	
	if request.method == 'POST':
		if request.is_ajax():
			ip_list_json = request.POST.get('iplist')
			ok_ip_list = []
			print (ip_list_json)
			print ("Checking the connection.....")
			response = os.system("ping -c 3 " + ip_list_json)
			respon_koneksi = " "
			if response == 0 :
				respon_koneksi = ip_list_json+" is connected"
				# print respon_koneksi
			else:
				respon_koneksi = ip_list_json+" is not connected"

			print (respon_koneksi)
			data = {'respon_koneksi': respon_koneksi}
			return HttpResponse(
				json.dumps(data)
			)
	else:
		passes = "nothing"
		return HttpResponse(content_type="application/json")

def history(request):
	return render(request, 'history.html')


class LoginInfo(generics.ListCreateAPIView):
	queryset = models.Connect.objects.all()
	serializer_class = serializers.AutonetSerializer

class LoginInfoDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = models.Connect.objects.all()
	serializer_class = serializers.AutonetSerializer

class IpInfo(generics.ListCreateAPIView):
	queryset = models.Ip.objects.all()
	serializer_class = serializers.IpAutonetSerializer

class IpInfoDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = models.Ip.objects.all()
	serializer_class = serializers.IpAutonetSerializer

class DataInfo(generics.ListCreateAPIView):
	queryset = models.Connect.objects.all()
	serializer_class = serializers.DataAutonetSerializer

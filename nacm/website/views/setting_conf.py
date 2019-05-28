import paramiko
import os, os.path, time
import re
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from ..forms import NacmForm, IpFormset, SettingForm
from .. import models
from ..models import c_Setting as settings

def Settings_display(request):

	settForm = SettingForm()
	return render(request, 'setting/display.html', {'settings': settings.objects.all(), 'form': settForm })

def Settings_add(request):
	if request.method == 'POST':
		settForm = SettingForm(request.POST)
	
		if settForm.is_valid():
			settForm.save()

		return HttpResponseRedirect('/setting')
	
	else:
		settForm = SettingForm()
		return render(request, 'setting/add.html', {'settings': settings.objects.all(), 'form': settForm })

def Settings_edit(request, pk):
	setting = get_object_or_404(settings, pk=pk)
	status = 'success'
	nameValue = settings.objects.filter(pk=pk).values('sett_name')[0];
	name = nameValue['sett_name']

	if request.method == 'POST':
		post_form = SettingForm(request.POST, instance=setting)
		if post_form.is_valid():
			post_form.save()
		return HttpResponseRedirect('/setting')
	else:
		form = SettingForm(instance=setting)
		return render(request, 'setting/edit.html', {'form': form, 'name': name, 'status': status })

def Settings_delete(request, pk):
    settingdel = settings.objects.get(pk=pk)
    settingdel.delete()
    return HttpResponseRedirect('/setting')
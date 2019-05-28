from django import forms
from django.forms import BaseFormSet
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm, modelformset_factory, formset_factory
from .models import Connect, Ip, c_Setting as settings


class NacmForm(ModelForm):
	password = forms.CharField(widget=forms.PasswordInput,required = False)
	# conft = forms.Textarea()
	class Meta:
		model = Connect
		fields = ['username', 'password','conft']

	labels = {'conft':_('Config'),}

# class RequiredFormSet(BaseFormSet):
#     def __init__(self, *args, **kwargs):
#         super(RequiredFormSet, self).__init__(*args, **kwargs)
#         for form in self.forms:
#             form.empty_permitted = False

class IpForm(ModelForm):
	vendor = forms.ModelChoiceField(queryset=settings.objects.all().order_by('sett_name'))
	class Meta:
		model = Ip
		fields = ['ipaddr','vendor']
	labels = {'ipaddr':_('IP address'),}


IpFormset = formset_factory(IpForm,  extra=1)
# IpFormset = formset_factory(IpForm,  extra=1, formset=RequiredFormSet)

class UploadForm(forms.Form):
	fileup = forms.FileField()
	fileup_name = forms.CharField(max_length=255)


class SettingForm(ModelForm):
	class Meta:
		model = settings
		fields = [
			'sett_name',
			'sett_name_desc',
			'sett_static_routing',
			'sett_dynamic_routing_ospf',
			'sett_dynamic_routing_ripv1',
			'sett_dynamic_routing_ripv2',
			'sett_dynamic_routing_bgp',
			'sett_vlan',
			'sett_backup',
			'sett_restore'
		]
		widgets = {
			'sett_static_routing': forms.Textarea(attrs={'cols':100, 'rows':4}),
			'sett_dynamic_routing_ospf': forms.Textarea(attrs={'cols':100, 'rows':4}),
			'sett_dynamic_routing_ripv1': forms.Textarea(attrs={'cols':100, 'rows':4}),
			'sett_dynamic_routing_ripv2': forms.Textarea(attrs={'cols':100, 'rows':4}),
			'sett_dynamic_routing_bgp': forms.Textarea(attrs={'cols':100, 'rows':4}),
			'sett_vlan': forms.Textarea(attrs={'cols':100, 'rows':4}),
			'sett_backup': forms.Textarea(attrs={'cols':100, 'rows':4}),
			'sett_restore': forms.Textarea(attrs={'cols':100, 'rows':4})
		}
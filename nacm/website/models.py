from django.db import models

# Create your models here.
class Connect(models.Model):
	username = models.CharField(max_length=255)
	password = models.CharField(max_length=255,null=True, blank=True)
	conft = models.TextField(null=True, blank=True)
	fileup = models.FileField(null=True, blank=True)
	fileup_name = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return unicode(self.username)

	def get_devices(self):
		return ', '.join(self.devices.all().values_list('username', flat=True))

class Ip(models.Model):
	class Meta:
		db_table = 'autonet_ip'

	connect_id = models.ForeignKey(Connect, on_delete=models.CASCADE, related_name='devices')
	ipaddr = models.CharField(max_length=255)
	vendor = models.CharField(max_length=255)

	def __str__ (self):
		return self.ipaddr

	def __str__(self):
		return 'ip address : %s: , vendor : %s' % (self.ipaddr, self.vendor)


class c_Setting(models.Model):
	class Meta:
		db_table = 'autonet_setting'

	sett_name = models.CharField(max_length=255)
	sett_name_desc = models.CharField(max_length=255)
	sett_static_routing = models.TextField(null=True, blank=True)
	sett_dynamic_routing_ospf = models.TextField(null=True, blank=True)
	sett_dynamic_routing_ripv1 = models.TextField(null=True, blank=True)
	sett_dynamic_routing_ripv2 = models.TextField(null=True, blank=True)
	sett_dynamic_routing_bgp = models.TextField(null=True, blank=True)
	sett_vlan = models.TextField(null=True, blank=True)
	sett_backup = models.TextField(null=True, blank=True)
	sett_restore = models.TextField(null=True, blank=True)

	def __str__(self):
		return self.sett_name
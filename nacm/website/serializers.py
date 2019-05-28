from rest_framework import serializers
from . import models


class AutonetSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'username',
            'password',
            'conft',
            'created_at',
        )
        model = models.Connect

class IpAutonetSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'connect_id',
            'ipaddr',
            'vendor',
        )
        model = models.Ip

class DataAutonetSerializer(serializers.ModelSerializer):
    # usernameinf = IpAutonetSerializer(source='ip_set')
    devices = serializers.StringRelatedField(many=True)

    class Meta:
        model = models.Connect
        fields = (
            'id',
            'username',
            'conft',
            'devices',
            'created_at',
        )

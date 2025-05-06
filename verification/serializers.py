from rest_framework import serializers
from .models import AadhaarVerification,PanCardVerification

class AadhaarVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AadhaarVerification
        fields = '__all__'

class PanCardVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanCardVerification
        fields = '__all__'

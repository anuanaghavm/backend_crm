from rest_framework import serializers
from .models import Agent
from policy.models import Policy  # Ensure correct import of the policy model

# Serializer for PolicyType
class PolicyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = '__all__'  # Include the required fields from the Policy model


# Serializer for Agent
class AgentSerializer(serializers.ModelSerializer):
    join_date = serializers.DateField(format="%Y-%m-%d")  # Ensure it's formatted correctly

    class Meta:
        model = Agent
        fields = ['id', 'full_name', 'email', 'contact_number', 'branch', 'address', 'gender', 'join_date', 'created_by', 'commission_percentage']
        read_only_fields = ['created_by']


    def validate_email(self, value):
        """Ensure that the email is unique."""
        if Agent.objects.filter(email=value).exists():
            raise serializers.ValidationError("An agent with this email already exists.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['created_by'] = getattr(request, 'user', None)
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.created_by:
            representation["created_by"] = {
                "id": instance.created_by.id,
                "name": "Admin" if instance.created_by.role.name == "Admin" else instance.created_by.user.name
            }
        return representation

from rest_framework import serializers
from .models import  User
from login.models import Account
from branch.models import Branch


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'branch_name', 'branch_code', 'address', 'city', 'state', 'country', 'email', 'contact']

class UserSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False)
    branch_name = serializers.SerializerMethodField()
    password = serializers.CharField(source='account.password', read_only=True)  # Include password from the Account model

    class Meta:
        model = User
        fields = [
            "id", "account", "email", "name", "contact", "address", 
            "role", "job_type", "status", "created_date", "created_by", 
            "branch","branch_name", "password",'target'
        ]

    def get_branch_name(self, obj):
        return obj.branch.branch_name if obj.branch else None

    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %I:%M %p')
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.created_by:
            representation["created_by"] = {
                "id": instance.created_by.id,
                "name": "Admin" if instance.created_by.role.name == "Admin" else instance.created_by.user.name
            }
        return representation


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'contact', 'address', 'job_type', 'status', 'created_date']

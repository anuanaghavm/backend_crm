from rest_framework import serializers
from .models import Company, PolicyCategory, Policy,PolicyType,PlanCoverage
from .models import Policy, PolicyType, PolicyCategory
from rest_framework import serializers
from .models import Policy, PolicyType, PolicyCategory, Company ,Plan
from login.models import Account

# class TaxManagementSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TaxManagement
#         fields = ['id', 'name', 'tax']

#         ref_name = 'TaxManagementPolicy'  # Unique name

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'logo']


class PolicyTypeSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    company_name = serializers.CharField(source='company.name', read_only=True)
    policy_category = serializers.PrimaryKeyRelatedField(queryset=PolicyCategory.objects.all())
    policy_category_name = serializers.CharField(source='policy_category.policy_name', read_only=True)

    class Meta:
        model = PolicyType
        fields = ['id', 'name', 'company', 'company_name', 'policy_category', 'policy_category_name']


class PolicyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyCategory
        fields = ['id', 'policy_name']  # Use 'policy_name' instead of 'name'


class PlanCoverageSerializer(serializers.ModelSerializer):
    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all())  # Add this line

    class Meta:
        model = PlanCoverage
        fields = ['id', 'plan', 'coverage_amount', 'premium_amount']  # Include 'plan'


class PlanSerializer(serializers.ModelSerializer):
    policy = serializers.PrimaryKeyRelatedField(queryset=Policy.objects.all())  # Accept policy_id
    coverages = PlanCoverageSerializer(many=True, read_only=True)  # Remove 'source' argument

    class Meta:
        model = Plan
        fields = ['id', 'plan_name', 'policy','coverages']


class PolicySerializer(serializers.ModelSerializer):
    # Displaying details of related models for better readability
    policy_type_details = serializers.StringRelatedField(source='policy_type', read_only=True)
    policy_category_details = serializers.StringRelatedField(source='policy_category', read_only=True)
    company_details = serializers.StringRelatedField(source='company', read_only=True)
    plans = PlanSerializer(many=True, read_only=True)  # Include plans which now include PlanCoverage

    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Policy
        fields = [
            'id', 'policy_name', 'policy_code', 'policy_type', 'policy_type_details',
            'policy_category', 'policy_category_details', 'company', 'company_details',
            'description', 'coverage_type', 'payment_frequency',
            'commission_agent', 'commission_kannat', 'policy_term_duration', 'status',
            'created_by', 'created_by_name', 'created_date', 'updated_date', 'no_claim_bonus',
            'terms_conditions_document', 'policy_brochure', 'eligibility_criteria',
            'exclusions', 'maturity_benefits', 'cancellation_policy', 'plans'
        ]
        read_only_fields = ['created_by', 'created_date', 'updated_date', 'created_by_name']
        ref_name = 'PolicySerializerPolicy'  # Explicitly set ref_name

    def create(self, validated_data):
        try:
            admin_user = Account.objects.get(id=1)
        except Account.DoesNotExist:
            raise serializers.ValidationError("Admin user with ID 1 does not exist.")

        validated_data['created_by'] = admin_user
        return super().create(validated_data)




    # def create(self, validated_data):
    #     # Fetch the admin user with ID 1
    #     try:
    #         admin_user = Account.objects.get(id=1)
    #     except Account.DoesNotExist:
    #         raise serializers.ValidationError("Admin user with ID 1 does not exist.")

    #     # Set the created_by field to the admin user
    #     validated_data['created_by'] = admin_user

    #     # Create and return the policy
    #     return super().create(validated_data)
    # def validate_tax_amount(self, value):
    #     """
    #     Validation logic for tax_amount if needed.
    #     For example, you can check if the value is valid based on tax_type.
    #     """
    #     return value

    # def validate_total_premium_amount(self, value):
    #     """
    #     Validation logic for total_premium_amount if needed.
    #     You can validate based on tax_amount and premium_amount.
    #     """
    #     return value
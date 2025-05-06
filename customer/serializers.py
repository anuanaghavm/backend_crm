from rest_framework import serializers
from .models import Customer, Nominee, Payment,CustomerPolicy,FamilyMember,AgentIncentive,UserIncentive
from policy.models import Policy,Plan,PlanCoverage
from login.models import Account
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
import jwt
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from decimal import Decimal
from agents.models import Agent

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'plan_name']

class PlanCoverageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanCoverage
        fields = ['id', 'plan', 'coverage_amount', 'premium_amount']

class PolicyCustomerSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    policy = serializers.PrimaryKeyRelatedField(queryset=Policy.objects.all())
    policy_name = serializers.SerializerMethodField()
    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all(), required=False, allow_null=True)
    plan_coverage = serializers.PrimaryKeyRelatedField(queryset=PlanCoverage.objects.all(), required=False, allow_null=True)
    agent = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all(), required=False, allow_null=True)
    start_date = serializers.DateField()
    company_id = serializers.IntegerField(source='policy.company.id', read_only=True)
    company_name = serializers.CharField(source='policy.company.name', read_only=True)
    policy_category_id = serializers.IntegerField(source='policy.policy_category.id', read_only=True)
    policy_category_name = serializers.CharField(source='policy.policy_category.policy_name', read_only=True)
    policy_master_id = serializers.IntegerField(source='policy.policy_type.id', read_only=True)
    policy_master_name = serializers.CharField(source='policy.policy_type.name', read_only=True)

    class Meta:
        model = CustomerPolicy
        fields = [
            'id', 'customer', 'policy', 'policy_name','plan', 'plan_coverage', 'agent','company_id','company_name', 
            'policy_category_id', 'policy_category_name', 'policy_master_id', 'policy_master_name',
            'coverage_amount1', 'premium_amount1','total_premium_amount1', 'tax_percentage', 'start_date', 'end_date'
        ]
        read_only_fields = ['end_date']


    def validate(self, data):
        policy = data.get('policy')
        plan = data.get('plan')
        plan_coverage = data.get('plan_coverage')
        coverage_amount1 = data.get('coverage_amount1')
        premium_amount1 = data.get('premium_amount1')
        tax_percentage = data.get('tax_percentage')

        if not policy:
            raise serializers.ValidationError({"policy": "Policy field cannot be null."})

        has_plans = Plan.objects.filter(policy=policy).exists()

        if has_plans:
            if not plan:
                raise serializers.ValidationError({"plan": "This policy has plans. You must select a plan."})

            if not Plan.objects.filter(id=plan.id, policy=policy).exists():
                raise serializers.ValidationError({"plan": "The selected plan does not belong to the chosen policy."})

            if plan_coverage:
                if not PlanCoverage.objects.filter(id=plan_coverage.id, plan=plan).exists():
                    raise serializers.ValidationError({"plan_coverage": "The selected plan coverage does not belong to the selected plan."})

                # Assign values if plan_coverage exists
                data['coverage_amount'] = plan_coverage.coverage_amount
                data['premium_amount'] = plan_coverage.premium_amount
            else:
                if not coverage_amount1 or not premium_amount1:
                    raise serializers.ValidationError({
                        "coverage_amount1": "Coverage amount is required if plan coverage is not selected.",
                        "premium_amount1": "Premium amount is required if plan coverage is not selected."
                    })

        else:
            # Allow manual input for policies without plans
            if not coverage_amount1 or not premium_amount1 or not tax_percentage:
                raise serializers.ValidationError({
                    "coverage_amount1": "Coverage amount is required for policies without plans.",
                    "premium_amount1": "Premium amount is required for policies without plans.",
                    "tax_percentage1": "Tax percentage is required for policies without plans."
                })

        return data

    def calculate_end_date(self, start_date, policy):
        """Calculate the end date based on policy_term_duration."""
        term = policy.policy_term_duration.lower()
        duration = None

        if "year" in term:
            try:
                years = int(term.split()[0])
                duration = relativedelta(years=years)
            except ValueError:
                raise serializers.ValidationError("Invalid policy term format. Expected 'X years'.")
        elif "month" in term:
            try:
                months = int(term.split()[0])
                duration = relativedelta(months=months)
            except ValueError:
                raise serializers.ValidationError("Invalid policy term format. Expected 'X months'.")
        elif "day" in term:
            try:
                days = int(term.split()[0])
                duration = timedelta(days=days)
            except ValueError:
                raise serializers.ValidationError("Invalid policy term format. Expected 'X days'.")
        else:
            raise serializers.ValidationError("Invalid policy_term_duration format.")

        return start_date + duration if duration else None

    def create(self, validated_data):
        customer = validated_data['customer']
        policy = validated_data['policy']
        plan = validated_data.get('plan')
        plan_coverage = validated_data.get('plan_coverage')
        coverage_amount1 = validated_data.get('coverage_amount1')
        premium_amount1 = validated_data.get('premium_amount1')
        tax_percentage = validated_data.get('tax_percentage')
        start_date = validated_data['start_date']

        end_date = self.calculate_end_date(start_date, policy)

        customer_policy = CustomerPolicy.objects.create(
            customer=customer,
            policy=policy,
            plan=plan,
            plan_coverage=plan_coverage,
            coverage_amount1=coverage_amount1,
            premium_amount1=premium_amount1,
            tax_percentage=tax_percentage,
            start_date=start_date,
            end_date=end_date
        )

        return customer_policy

    def update(self, instance, validated_data):
        start_date = validated_data.get('start_date', instance.start_date)
        agent = validated_data.get('agent', instance.agent)
        plan = validated_data.get('plan', instance.plan)
        plan_coverage = validated_data.get('plan_coverage', instance.plan_coverage)

        if plan and plan.policy != instance.policy:
            raise serializers.ValidationError({"plan": "Selected plan does not belong to the assigned policy."})

        if plan_coverage and plan_coverage.plan != plan:
            raise serializers.ValidationError({"plan_coverage": "Selected plan coverage does not belong to the assigned plan."})

        if start_date != instance.start_date:
            instance.end_date = self.calculate_end_date(start_date, instance.policy)

        instance.start_date = start_date
        instance.agent = agent
        instance.plan = plan
        instance.plan_coverage = plan_coverage

        # Prevent AttributeError when plan_coverage is None
        if plan_coverage:
            instance.coverage_amount = plan_coverage.coverage_amount
            instance.premium_amount = plan_coverage.premium_amount

        instance.save()
        return instance
    
    def get_policy_name(self, obj):
        policy = Policy.objects.filter(id=obj.policy_id).first()  # Fetch the Policy object
        return policy.policy_name if policy else None


    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Include policy name as a direct field
        # data['policy_name'] = instance.policy.policy_name if instance.policy else None

        # Include plan and plan_coverage details
        data['plan'] = PlanSerializer(instance.plan).data if instance.plan else None
        data['plan_coverage'] = PlanCoverageSerializer(instance.plan_coverage).data if instance.plan_coverage else None

        return data

class FamilyMemberSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    
    class Meta:
        model = FamilyMember
        fields = ['id', 'first_name','middle_name','last_name', 'relationship', 'dob', 'contact', 'email', 'gender','address1','address2','address3','district','pincode','pan_no','occupation','customer']
class NomineeSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(),required=False, allow_null=True)  
    family_member = serializers.PrimaryKeyRelatedField(queryset=FamilyMember.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Nominee
        fields = ['id', 'name', 'relationship','phone_number','address','nominee_appointee_name','customer', 'family_member']

class PaymentSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    policy_id = serializers.PrimaryKeyRelatedField(queryset=Policy.objects.all())
    total_paid_amount = serializers.SerializerMethodField()
    total_premium_amount1 = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    due_amount = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    policy_name = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    transaction_date = serializers.DateField(format="%m/%d/%Y")

    class Meta:
        model = Payment
        fields = [
            'id', 'policy_id', 'policy_name', 'customer', 'customer_name', 'branch_name',
            'transaction_date', 'total_premium_amount1',
            'amount_paid', 'payment_method', 'payment_status', 'due_amount', 'loan_tenure',
            'good_health_declaration', 'GHI_sum_insured', 'GPA_sum_insured', 'GCC_sum_insured',
            'EMI_amount', 'SI_flag', 'SI_date', 'total_premium_collected', 'transaction_id',
            'notes', 'total_paid_amount', 'balance', 'created_by'
        ]

    def get_policy_name(self, obj):
        return obj.policy_id.policy_name if obj.policy_id else None
    
    def get_customer_name(self, obj):
        return obj.customer.first_name if obj.policy_id else None

    def get_branch_name(self, obj):
        """
        Fetch the branch_name from the created_by's user branch.
        """
        created_by = obj.customer.created_by  # Get created_by from customer
        if created_by and hasattr(created_by, 'user') and hasattr(created_by.user, 'branch'):
            return created_by.user.branch.branch_name
        return "No Branch"
    
    def get_total_premium_amount1(self, obj):
        customer_policy = CustomerPolicy.objects.filter(customer=obj.customer, policy=obj.policy_id).first()
        return customer_policy.total_premium_amount1 if customer_policy else None
    

    def get_total_paid_amount(self, obj):
        total_paid = Payment.objects.filter(
            customer=obj.customer,
            policy_id=obj.policy_id,
            payment_status='successful'
        ).aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0
        return Decimal(total_paid)  # Ensure it returns a Decimal value


    def get_balance(self, obj):
    # Ensure the related policy has a customer policy entry
        customer_policy = CustomerPolicy.objects.filter(customer=obj.customer, policy=obj.policy_id).first()
    
        if customer_policy:
            total_premium = customer_policy.total_premium_amount1 or Decimal('0.00')
            total_paid = Payment.objects.filter(customer=obj.customer, policy_id=obj.policy_id).aggregate(
            total=Sum('amount_paid'))['total'] or Decimal('0.00')
        
            return total_premium - total_paid

        return Decimal('0.00')  


    def get_due_amount(self, obj):
        """
        Calculate due amount: 
        due_amount = total_premium_amount1 - total amount paid so far
        """
        customer_policy = CustomerPolicy.objects.filter(customer=obj.customer, policy=obj.policy_id).first()
        if customer_policy:
            total_premium = customer_policy.total_premium_amount1 or 0
            total_paid = Payment.objects.filter(customer=obj.customer, policy_id=obj.policy_id).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
            return total_premium - total_paid
        return None

    
    def get_login_id_from_token(self, token):
        try:
            # Decode the token
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return decoded_token.get('user_id')
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Token has expired.")
        except jwt.InvalidTokenError:
            raise serializers.ValidationError("Invalid token.")

    def create(self, validated_data):
        request = self.context.get('request')
        token = request.headers.get('Authorization', '').split(' ')[1]  # Extract token from "Bearer <token>"
        login_id = self.get_login_id_from_token(token)

        try:
            account = Account.objects.get(id=login_id)
        except Account.DoesNotExist:
            raise serializers.ValidationError("Invalid login_id in token.")

        validated_data['created_by'] = account
        return super().create(validated_data)
        
class CustomerSerializer(serializers.ModelSerializer):
    customer_policies = serializers.SerializerMethodField()  
    family_members = FamilyMemberSerializer(many=True, read_only=True)  
    nominees = NomineeSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    family_member_nominees = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    branch_code = serializers.SerializerMethodField()
    dob = serializers.DateField(format="%m/%d/%Y")
    name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'customer_id','branch_name','branch_code','first_name','middle_name','last_name','name','title','member_relation', 'profile_image','email', 'contact', 'aadhar_card_number', 'pan_no',
            'gender', 'dob', 'address1','address2','address3','district','pincode','occupation', 'health_condition',
            'father_name', 'mother_name', 'guardian_name', 'created_date','created_by','family_members','family_member_nominees','customer_policies','nominees', 'payments','status'
        ]
        read_only_fields = ['created_by']

    def get_name(self, obj):
        return obj.name

    def get_created_date(self, obj):
        return obj.created_date.strftime('%Y-%m-%d')

    def get_family_member_nominees(self, obj):
        family_members = obj.family_members.all()
        nominees = []
        for family_member in family_members:
            nominees.extend(family_member.nominees.all())
        return NomineeSerializer(nominees, many=True).data

    def get_login_id_from_token(self, token):
        try:
            # Decode the token
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return decoded_token.get('user_id')
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Token has expired.")
        except jwt.InvalidTokenError:
            raise serializers.ValidationError("Invalid token.")
    
    def get_branch_name(self, obj):
        """Fetch branch name from the created_by user's branch."""
        if obj.created_by and hasattr(obj.created_by, 'user') and obj.created_by.user.branch:
            return obj.created_by.user.branch.branch_name
        return None

    def get_branch_code(self, obj):
        """Fetch branch code from the created_by user's branch."""
        if obj.created_by and hasattr(obj.created_by, 'user') and obj.created_by.user.branch:
            return obj.created_by.user.branch.branch_code
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.created_by:
            representation['created_by'] = {
                'id': instance.created_by.id,
                'name': instance.created_by.user.name if hasattr(instance.created_by, 'user') else 'Unknown'
            }
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        token = request.headers.get('Authorization', '').split(' ')[1]  # Extract token from "Bearer <token>"
        login_id = self.get_login_id_from_token(token)

        try:
            account = Account.objects.get(id=login_id)
        except Account.DoesNotExist:
            raise serializers.ValidationError("Invalid login_id in token.")

        validated_data['created_by'] = account
        return super().create(validated_data)
    
    # def get_customer_policies(self, obj):
    #     return [
    #         {
    #             "policy_id":cp.policy.id,
    #             "policy_name": cp.policy.policy_name,
    #             'policy_code':cp.policy.policy_code,
    #             'company':cp.policy.company.name,
    #             'policy_category':cp.policy.policy_category.policy_name,
    #             'policy_type':cp.policy.policy_type.name,
    #             'plan':cp.policy.plans.all(),
    #             "coverage_amount":cp.coverage_amount,
    #             "premium_amount":cp.premium_amount,
    #             "tax_type":cp.tax_type,
    #             "tax_amount":cp.tax_amount,
    #             "total_amount":cp.total_premium_amount,
    #             'agent': cp.agent.full_name if cp.agent else None, # this agent will be null 
    #             "start_date": cp.start_date,
    #             "end_date": cp.end_date,
    #         }
    #         for cp in obj.customer_policies.all()
    #     ]
    def get_customer_policies(self, obj):
        policies = CustomerPolicy.objects.filter(customer=obj)
        return PolicyCustomerSerializer(policies, many=True).data
    
    def validate(self, data):
        request = self.context.get('request')
        
        if isinstance(data, list):  # bulk creation
            contact_numbers = [item.get('contact') for item in data]
            if len(contact_numbers) != len(set(contact_numbers)):
                raise serializers.ValidationError("Duplicate contact numbers found in the request.")

            existing_contacts = Customer.objects.filter(contact__in=contact_numbers).values_list('contact', flat=True)
            if existing_contacts:
                raise serializers.ValidationError(f"These contact numbers already exist: {', '.join(existing_contacts)}")
        else:
            contact = data.get('contact')
            if self.instance:
                if Customer.objects.exclude(id=self.instance.id).filter(contact=contact).exists():
                    raise serializers.ValidationError({"contact": "This contact number is already used by another customer."})
            else:
                if Customer.objects.filter(contact=contact).exists():
                    raise serializers.ValidationError({"contact": "This contact number already exists."})
        
        return data

class AgentIncentiveSerializer(serializers.ModelSerializer):
    agent = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all())
    customer_policy = serializers.PrimaryKeyRelatedField(queryset=CustomerPolicy.objects.all())
    incentive_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    customer = serializers.SerializerMethodField()

    class Meta:
        model = AgentIncentive
        fields = ['id', 'agent','customer' ,'customer_policy', 'incentive_amount', 'created_at']

    def get_customer(self, obj):
        return obj.customer_policy.customer.name

    def update(self, instance, validated_data):
        """Allow updating the agent and recalculate incentive."""
        instance.agent = validated_data.get('agent', instance.agent)
        instance.save()
        instance.calculate_incentive()
        return instance
    
class UserIncentiveSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.name
    class Meta:
        model = UserIncentive
        fields = ['id', 'user', 'customer_policy', 'incentive_amount', 'issued_date']
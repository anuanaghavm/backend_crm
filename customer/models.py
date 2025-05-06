from django.db import models
from policy.models import Policy,Plan,PlanCoverage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from login.models import Account
from django.utils import timezone
from django.utils.timezone import now
from agents.models import Agent
from decimal import Decimal
from django.db.models import Sum ,DecimalField
from users.models import User

class Customer(models.Model):
    GENDER_CHOICES = [
        ('Male', 'M'),
        ('Female', 'F'),
        ('Other', 'O'),
    ]

    TITLE_CHOICES = [
        ('MR', 'Mr.'),
        ('MRS', 'Mrs.'),
        ('MS', 'Ms.'),
    ]

    RELATIONSHIP_CHOICES = [
        ('E', 'Self-E'),
        ('S', 'Spouse-S'),
        ('D', 'Daughter-D'),
        ('C', 'Son-C'),
    ]

    first_name = models.CharField(max_length=255)  # New Field
    middle_name = models.CharField(max_length=255, null=True, blank=True)  # New Field
    last_name = models.CharField(max_length=255)  # New Field
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, null=True, blank=True) 
    member_relation = models.CharField(max_length=10, choices=RELATIONSHIP_CHOICES, null=True, blank=True)  # New Field
    address1 = models.CharField(max_length=255, null=True, blank=True)  # New Field
    address2 = models.CharField(max_length=255, null=True, blank=True)  # New Field
    address3 = models.CharField(max_length=255, null=True, blank=True)  # New Field
    district = models.CharField(max_length=255, null=True, blank=True)  # New Field
    pincode = models.CharField(max_length=10, null=True, blank=True)  # New Field
    profile_image = models.ImageField(upload_to="profile_images/",null=True,blank=True)
    email = models.EmailField(unique=True,default=None,null=True,blank=True)
    contact = models.CharField(max_length=15)
    aadhar_card_number = models.CharField(max_length=12,validators=[RegexValidator(regex='^\d{12}$', message="Aadhar number must be exactly 12 digits.")],null=True,blank=True)
    pan_no = models.TextField(null=True,blank=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)
    dob = models.DateField(verbose_name="Date of Birth")
    occupation = models.CharField(max_length=255,null=True,blank=True)
    health_condition = models.TextField(null=True,blank=True)
    father_name = models.CharField(max_length=255,null=True,blank=True)
    mother_name = models.CharField(max_length=255,null=True,blank=True)
    guardian_name = models.CharField(max_length=255,null=True,blank=True)
    created_date = models.DateField(auto_now_add=True)     
    status = models.CharField(max_length=30, choices=[('active', 'Active'), ('deactivated', 'Deactivated')], default='active')  # Default status is active
    created_by = models.ForeignKey(Account,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_customers")
    customer_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # Generate customer_id if not already set
        if not self.customer_id:
            # Get the branch_code of the created_by user's branch
            created_by_user = self.created_by.user
            branch_code = created_by_user.branch.branch_code

            # Get the current year
            current_year = timezone.now().year

            # Get the latest customer_id number in the current year
            last_customer = Customer.objects.filter(customer_id__startswith=f'{branch_code}{current_year}').order_by('customer_id').last()
            if last_customer:
                # Extract the last 6-digit number and increment it
                last_number = int(last_customer.customer_id[-6:])
                new_number = last_number + 1
            else:
                new_number = 1  # Start from 000001

            # Format new_number as 6 digits
            customer_id = f"{branch_code}{current_year}{new_number:06}"

            self.customer_id = customer_id
        
        super().save(*args, **kwargs)

    @property
    def name(self):
        name_parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(filter(None, name_parts))
    
    def _str_(self):
        return self.name

class FamilyMember(models.Model):
    RELATIONSHIP_CHOICES = [
        ('E', 'Self-E'),
        ('S', 'Spouse-S'),
        ('D', 'Daughter-D'),
        ('C', 'Son-C'),
    ]
    GENDER_CHOICES = [
        ('Male', 'M'),
        ('Female', 'F'),
        ('Other', 'O'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="family_members")
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255,null=True,blank=True)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)
    address1 = models.TextField()
    address2 = models.TextField(null=True,blank=True)
    address3 = models.TextField(null=True,blank=True)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    dob = models.DateField(verbose_name="Date of Birth")
    contact = models.CharField(max_length=15)
    email = models.EmailField(null=True,blank=True)
    district = models.TextField()
    pincode = models.TextField()
    pan_no = models.TextField(null=True,blank=True)
    occupation = models.TextField(null=True,blank=True)

    def _str_(self):
        return f"{self.name} ({self.relationship})"
    
class Nominee(models.Model):
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('brother', 'Brother'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="nominees")
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="nominees", null=True, blank=True)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Updated to optional
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    address = models.TextField(null=True, blank=True)  # Updated to optional
    nominee_appointee_name = models.CharField(max_length=255, null=True, blank=True)  # New Field

    def _str_(self):
        return f"{self.name} ({self.relationship})"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('other', 'Other'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('successful', 'Successful'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]
    policy_id = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="payments")    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="payments")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_date = models.DateField(null=True, blank=True)  
    loan_tenure = models.IntegerField(null=True, blank=True)  
    good_health_declaration = models.BooleanField(default=False,null=True, blank=True)  # New Field
    GHI_sum_insured = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New Field
    GPA_sum_insured = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New Field
    GCC_sum_insured = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New Field
    EMI_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New Field
    SI_flag = models.BooleanField(default=False,null=True, blank=True)  # New Field
    SI_date = models.DateField(null=True, blank=True)  # New Field
    total_premium_collected = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New Field
    transaction_id = models.TextField(null=True,blank=True)
    notes = models.TextField(null=True,blank=True)
    created_by = models.ForeignKey(Account,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_payments")


    def _str_(self):
        return f"Payment for {self.policy.name} on {self.transaction_date}"
    
class CustomerPolicy(models.Model):

    TAX_TYPE_CHOICES = [
        ('Inclusive', 'Inclusive'),
        ('Exclusive', 'Exclusive'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer_policies")
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="customer_policies")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="customer_policies", null=True, blank=True)  # Add Plan Field
    plan_coverage = models.ForeignKey(PlanCoverage,on_delete=models.CASCADE,related_name="customer_policies", null=True, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="customer_policies")
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tax_type = models.CharField(max_length=10, choices=TAX_TYPE_CHOICES, blank=True, null=True)
    coverage_amount1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    premium_amount1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_premium_amount1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def _str_(self):
        return f"{self.customer.name} - {self.policy.policy_name}"

class AgentIncentive(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="incentives")
    customer_policy = models.ForeignKey(CustomerPolicy, on_delete=models.CASCADE, related_name="incentives")
    incentive_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def calculate_incentive(self):
        """Calculate incentive as per formula: (policy premium * agent commission) / 100"""
        if self.customer_policy.agent and self.customer_policy.policy:
            self.incentive_amount = (
                self.customer_policy.policy.total_premium_amount * Decimal(self.customer_policy.policy.commission_agent) / Decimal(100)
                )
            self.save()

    def _str_(self):
        return f"Incentive for {self.agent.name} - {self.incentive_amount}"
    
class UserIncentive(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="incentives")
    customer_policy = models.ForeignKey(CustomerPolicy, on_delete=models.CASCADE, null=True, blank=True)
    incentive_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateField(auto_now_add=True)

    def calculate_user_incentive(user):
    # Get all customer policies created by this user where no agent is assigned
        customer_policies = CustomerPolicy.objects.filter(customer_created_by=user, agent_isnull=True)
    
    # Sum up the total premium amounts of these policies
        total_policy_amount = customer_policies.aggregate(total=Sum('policy__total_premium_amount'))['total'] or 0

    # Check if the total meets or exceeds the user's target
        user_target = user.target  # Assuming target is stored in the User model
        if total_policy_amount >= user_target:
        # Sum of paid amounts for these policies
            paid_amount = Payment.objects.filter(
                customer__created_by=user, 
                customer_customer_policiesagent_isnull=True,  # Only for policies without an agent
                payment_status='successful'
            ).aggregate(total=Sum('amount_paid'))['total'] or 0

        # Calculate incentive (8.4% of the paid amount)
            incentive_amount = (paid_amount * 8.4) / 100

        # Create a UserIncentive record
            UserIncentive.objects.create(
                user=user,
                incentive_amount=incentive_amount
            )
            return incentive_amount
        return 0  # No incentive if the target is not met
    
    def _str_(self):
        return f"Incentive {self.incentive_amount} for {self.user.name}"
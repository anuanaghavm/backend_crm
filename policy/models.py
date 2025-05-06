from django.db import models
from login.models import Account


class Company(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logo/')

    def __str__(self):
        return self.name


class PolicyCategory(models.Model):
    policy_name = models.CharField(max_length=255)

    def __str__(self):
        return self.policy_name


class PolicyType(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Foreign key for role
    policy_category = models.ForeignKey(PolicyCategory, on_delete=models.CASCADE)  # Foreign key for category
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Policy(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Expired', 'Expired'),
    ]

    PAYMENT_FREQUENCY_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Annually', 'Annually'),
    ]

    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False)
    policy_name = models.CharField(max_length=255, null=False)
    policy_code = models.CharField(max_length=255, unique=True, null=False)
    policy_type = models.ForeignKey('PolicyType', on_delete=models.CASCADE, null=False)
    policy_category = models.ForeignKey('PolicyCategory', on_delete=models.CASCADE, null=False)
    description = models.TextField(blank=True, null=True)
    coverage_type = models.CharField(max_length=255, blank=True, null=True)
    payment_frequency = models.CharField(max_length=10, choices=PAYMENT_FREQUENCY_CHOICES, blank=True, null=True)
    commission_agent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    commission_kannat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    policy_term_duration = models.CharField(max_length=255, null=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=False)
    created_date = models.DateField(auto_now_add=True, editable=False)
    updated_date = models.DateField(auto_now=True, editable=False)
    created_by = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_policies")
    eligibility_criteria = models.TextField(blank=True, null=True)
    exclusions = models.TextField(blank=True, null=True)
    grace_period = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    late_payment_penalty = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    maturity_benefits = models.TextField(blank=True, null=True)
    cancellation_policy = models.TextField(blank=True, null=True)
    terms_conditions_document = models.FileField(upload_to='policy_documents/', blank=True, null=True)
    policy_brochure = models.FileField(upload_to='policy_documents/', blank=True, null=True)
    no_claim_bonus = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.policy_name


class Plan(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="plans")
    plan_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.plan_name} - {self.policy.policy_name}"


class PlanCoverage(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="coverages")
    coverage_amount = models.TextField()
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.plan.plan_name} - Coverage: {self.coverage_amount} - Premium: {self.premium_amount}"

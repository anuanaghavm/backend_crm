from django.db import models
from roles.models import Role
from branch.models import Branch
from policy.models import Policy
from login.models import Account

class Agent(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    contact_number = models.BigIntegerField()
    # role = models.ForeignKey(Role, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE,null=True, blank=True)
    address = models.TextField()
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    join_date = models.DateField(auto_now_add=True)  # Automatically add the current datetime on creation
    created_by = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='created_agents')
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)


    def __str__(self):
        return self.full_name()







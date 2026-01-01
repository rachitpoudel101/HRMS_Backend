from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.common.models import SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin


class Company(SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin):
    
    """Multi-company support"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    registration_number = models.CharField(max_length=100, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nepal')
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['name', 'code']
        db_table = 'company'

    def __str__(self):
        return self.name


class User(SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin, AbstractUser):
    """Extended user model"""
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('HR', 'HR Manager'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users', null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username
    class Meta:
        db_table = 'users'
        

class Branch(SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin):

    """Branch/Office locations"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['company', 'code']
        db_table = 'branch'

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Employee(models.Model):
    """Employee profile"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ]
    EMPLOYMENT_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ON_LEAVE', 'On Leave'),
        ('SUSPENDED', 'Suspended'),
        ('TERMINATED', 'Terminated'),
        ('RESIGNED', 'Resigned'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='employees')
    department = models.ForeignKey('department.Department', on_delete=models.SET_NULL, null=True, related_name='employees')
    designation = models.ForeignKey('department.Designation', on_delete=models.SET_NULL, null=True, related_name='employees')
    manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subordinates')

    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES)
    nationality = models.CharField(max_length=100, default='Nepali')
    personal_email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_relation = models.CharField(max_length=100)
    permanent_address = models.TextField()
    current_address = models.TextField()
    date_of_joining = models.DateField()
    date_of_exit = models.DateField(null=True, blank=True)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='ACTIVE')
    probation_end_date = models.DateField(null=True, blank=True)
    confirmation_date = models.DateField(null=True, blank=True)
    pan_number = models.CharField(max_length=50, blank=True, help_text="Tax ID")
    citizenship_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
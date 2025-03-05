from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission,  # ✅ Import Group & Permission
)
from django.db import models
import uuid
import random
from django.utils.timezone import now
from datetime import timedelta


class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not phone_number:
            raise ValueError("The Phone Number field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    state = models.CharField(max_length=100)
    address1 = models.TextField()
    address2 = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    country = models.CharField(max_length=20, default="US")
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)

    # Banking Details
    ssn_tin = models.CharField(max_length=30, unique=True)  # SSN/TIN
    occupation = models.CharField(max_length=100)
    annual_income = models.CharField(max_length=100, default=0)
    passport = models.FileField(upload_to="passports/")

    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    is_logged_in_verified = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number", "first_name", "last_name"]
    
    reset_token = models.UUIDField(default=None, null=True, blank=True) 
    reset_token_expiry = models.DateTimeField(null=True, blank=True)

    verification_code = models.IntegerField(null=True, blank=True)
    verification_code_expiry = models.DateTimeField(null=True, blank=True)

    login_code = models.IntegerField(null=True, blank=True)
    login_code_expiry = models.DateTimeField(null=True, blank=True)
    
    date_joined = models.DateTimeField(default=now)

    groups = models.ManyToManyField(
        Group, related_name="custom_user_groups", blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permissions", blank=True
    )

    def __str__(self):
        return self.email

    def generate_reset_token(self):
        # Generate a UUID token for password reset
        self.reset_token = uuid.uuid4()
        self.reset_token_expiry = now() + timedelta(hours=24)
        self.save()
        return self.reset_token

    def generate_verification_code(self):
        # Generate a 4-digit verification code
        self.verification_code = random.randint(1000, 9999)
        self.verification_code_expiry = now() + timedelta(minutes=10)
        self.save()
        return self.verification_code

    def generate_login_code(self):
        # Generate a 4-digit login code
        self.login_code = random.randint(1000, 9999)
        self.login_code_expiry = now() + timedelta(minutes=10)
        self.save()
        return self.login_code
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission,  # ✅ Import Group & Permission
)
from django.db import models
import uuid
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
    address = models.TextField()
    city = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)

    # Banking Details
    ssn_tin = models.CharField(max_length=30, unique=True)  # SSN/TIN
    occupation = models.CharField(max_length=100)
    annual_income = models.DecimalField(max_digits=15, decimal_places=2)
    passport_file = models.FileField(upload_to="passports/")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number", "first_name", "last_name"]

    # Reset Password Token
    reset_token = models.UUIDField(
        default=None, null=True, blank=True
    )  # ✅ Removed unique=True
    reset_token_expiry = models.DateTimeField(null=True, blank=True)

    groups = models.ManyToManyField(
        Group, related_name="custom_user_groups", blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permissions", blank=True
    )

    def __str__(self):
        return self.email

    def generate_reset_token(self):
        """Generate a password reset token and expiry timestamp."""
        self.reset_token = uuid.uuid4()
        self.reset_token_expiry = now() + timedelta(hours=1)  # Token valid for 1 hour
        self.save(
            update_fields=["reset_token", "reset_token_expiry"]
        )  # ✅ Optimized save
        return self.reset_token  # ✅ Ensure token is stored properly

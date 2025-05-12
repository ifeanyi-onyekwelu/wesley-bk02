from django.db import models
from django.contrib.auth import get_user_model
import uuid
import random

User = get_user_model()


def generate_account_number():
    return str(random.randint(1000000000, 9999999999))  # 10-digit account number


class Recipient(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # The user adding the recipient
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    transfer_type = models.CharField(
        max_length=50,
        choices=[
            ("wire_transfer", "Wire Transfer"),
            ("international", "International Transfer"),
        ],
    )
    iban = models.CharField(
        max_length=34, blank=True, null=True
    )  # Required for European transfers
    swift_code = models.CharField(
        max_length=11, blank=True, null=True
    )  # Required for wire transfers
    account_number = models.CharField(max_length=20)  # Required for all transfers
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.country} ({self.transfer_type})"


class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ("SAVINGS", "Savings"),
        ("CURRENT", "Current"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(
        max_length=10, unique=True, default=generate_account_number
    )
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES)
    account_currency = models.CharField(max_length=255)
    is_blocked = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    transaction_pin = models.CharField(max_length=6)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.account_number}"


class Transfer(models.Model):
    TRANSFER_TYPES = [
        ("interbank", "InterBank Transfer"),  # To the same bank
        ("wire", "Wire Transfer"),
        ("other", "Other Bank Transfer"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_transfers"
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name="recipient_account",
    )
    sender = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name="sender_account"
    )
    wire_recipient = models.ForeignKey(
        Recipient, on_delete=models.CASCADE, blank=True, null=True
    )  # Links to the saved recipient
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPES)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.recipient.full_name} ({self.amount})"


class Receipt(models.Model):
    """Stores receipts for transactions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pdf_file = models.FileField(upload_to="receipts/")

    def __str__(self):
        return f"Receipt for {self.transaction.id}"

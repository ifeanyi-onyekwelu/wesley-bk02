from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import login, logout
from app.models import BankAccount
from users.models import User
from django.db import transaction
from django.utils.timezone import now
from utils.helpers import json_response, send_email
from datetime import timedelta
from django.contrib import messages

template_root = "public/auth"


def signup_view(request):
    if request.method == "GET":
        return render(request, f"{template_root}/signup.html")

    if request.method == "POST":
        # Personal details
        first_name = request.POST.get("firstName")
        middle_name = request.POST.get("middleName", "")  # Optional
        last_name = request.POST.get("lastName")
        date_of_birth = request.POST.get("dateOfBirth")  # YYYY-MM-DD format
        address1 = request.POST.get("address1")
        country = request.POST.get("country")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zipcode = request.POST.get("zipcode")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone")

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Banking details
        ssn_tin = request.POST.get("ssn")  # Social Security Number / Tax ID
        occupation = request.POST.get("occupation")
        annual_income = request.POST.get("income")
        account_type = request.POST.get("accountType", "SAVINGS")  # Default to savings
        account_currency = request.POST.get("currency", "USD")  # Default currency
        transaction_pin = request.POST.get("pin")  # 6-digit PIN
        passport = request.FILES.get("passport")  # Uploaded passport image

        # Validate required fields
        required_fields = [
            first_name,
            last_name,
            date_of_birth,
            state,
            address1,
            city,
            zipcode,
            email,
            phone_number,
            password1,
            password2,
            ssn_tin,
            occupation,
            annual_income,
            transaction_pin,
            passport,
        ]

        if any(field is None or field == "" for field in required_fields):
            messages.error(request, "All fields are required.")
            return redirect("auth:signup")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("auth:signup")

        if len(transaction_pin) != 4 or not transaction_pin.isdigit():
            messages.error(request, "Transaction PIN must be a 4-digit number.")
            return redirect("auth:signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("auth:signup")

        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already exists.")
            return redirect("auth:signup")

        if User.objects.filter(ssn_tin=ssn_tin).exists():
            messages.error(request, "SSN already linked with an account.")
            return redirect("auth:signup")

        # Create User
        user = User(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            state=state,
            address1=address1,
            city=city,
            zipcode=zipcode,
            country=country,
            email=email,
            phone_number=phone_number,
            ssn_tin=ssn_tin,
            occupation=occupation,
            annual_income=annual_income,
            passport=passport,
        )
        
        user.set_password(password1)
        user.save()

        # Create a Bank Account
        bank_account = BankAccount.objects.create(
            user=user,
            account_type=account_type,
            account_currency=account_currency,
            transaction_pin=transaction_pin,
        )
        
        context = {
            "subject": "Verify Your Account",
            "first_name": first_name,
            "last_name": last_name,
            "account_number": bank_account.account_number,
            "account_type": account_type,
            "account_currency": account_currency,
            "annual_income": annual_income,
            "transaction_pin": transaction_pin,
        }
        
        send_email(
            "Verify Your Account",  # Subject
            "email/auth/account_verification_email.html",  # Template path
            context,  # Context data to be passed to the template
            [email],  # Recipient list
        )

        # Generate a random verification code
        verification_code = user.generate_verification_code()

        # Send the Verification Code Email
        verification_context = {
            "subject": "Your Verification Code",
            "verification_code": verification_code,
        }

        send_email(
            "Verify Your Account",  # Subject
            "email/auth/verification_code_email.html",  # Path to a simple verification code template
            verification_context,  # Context with the verification code
            [email],  # Recipient list
        )

        messages.success(request, "Signup successful! Please verify your email.")
        return redirect("auth:verify_account")


def login_view(request):
    if request.method == "GET":
        return render(request, f"{template_root}/login.html")

    if request.method == "POST":
        account_number = request.POST.get("account-number")
        password = request.POST.get("password")

        try:
            bank_account = BankAccount.objects.get(account_number=account_number)
            user = bank_account.user
        except BankAccount.DoesNotExist:
            messages.error(request, "Invalid account number or password.")
            return redirect("auth:login")

        if not user.check_password(password):
            messages.error(request, "Invalid account number or password.")
            return redirect("auth:login")

        if not user.is_active:
            messages.error(request, "Account is not active.")
            return redirect("auth:login")


        send_verification_email(user, "login")
        login(request, user)
        return redirect(reverse('auth:verify_login'))


def send_verification_email(user, code_type):
    verification_code = None
    if code_type == "verification":
        verification_code = user.generate_verification_code()
    elif code_type == "login":
        verification_code = user.generate_login_code()

    verification_context = {
        "user": user,
        "subject": "Your Verification Code",
        "verification_code": verification_code,
    }

    send_email(
        "Verify Your Account", 
        "email/auth/verification_code_email.html",  
        verification_context,  
        [user.email],  
    )


def resend_verification_email(request):
    if request.method == "POST":
        user = request.user

        if user.is_verified:
            messages.info(request, "Your account is already verified.")
        else:
            send_verification_email(user, "verification")
            messages.success(request, "A new verification email has been sent.")
        return redirect("dashboard:home")


def resend_password_reset_email(request):
    if request.method == "POST":
        user = request.user

        # Generate new reset token
        reset_token = user.generate_reset_token()

        # Send the Reset Token Email
        reset_context = {
            "subject": "Password Reset Code",
            "reset_token": reset_token,
        }

        send_email(
            "Reset Your Password", 
            "email/auth/reset_token_email.html",  
            reset_context,  
            [user.email],  
        )

        messages.success(request, "A new password reset email has been sent")


def resend_verify_login_email(request):
    if request.method == "POST":
        user = request.user

        send_verification_email(user, "login")
        messages.success(request, "A new login verification email has been sent")
        return redirect(reverse('auth:verify_login'))


def verify_account(request):
    if request.method == 'GET':
        return render(request, f"{template_root}/verify_login.html")
    
    if request.method == 'POST':
        try:
            code = request.POST.get('verification_code')
            user = get_object_or_404(User, verification_code=code)

            # Optional: Check if the code has expired (10-minute window)
            if user.verification_code_expiry and now() - user.verification_code_expiry > timedelta(minutes=10):
                messages.error(request, 'Email verification code has expired. Please request a new code')
                return redirect(reverse('auth:verify_account'))

            # Mark the user as verified
            user.verification_code = None
            user.verification_code_expiry = None
            user.is_verified = True
            user.save()

            messages.success(request, 'Your email has been successfully verified')
            return redirect(reverse('user:dashboard'))

        except Exception as e:
            messages.error(request, 'Invalid code. Please request a new code')
            return redirect(reverse('auth:verify_account'))


def verify_login(request):
    if request.method == 'GET':
        return render(request, f"{template_root}/verify_login.html")
    
    if request.method == 'POST':
        try:
            code = request.POST.get('verification_code')
            user = get_object_or_404(User, login_code=code)

            # Optional: Check if the code has expired (10-minute window)
            if user.login_code_expiry and now() - user.login_code_expiry > timedelta(minutes=10):
                messages.error(request, 'Login verification code has expired. Please request a new code')
                return redirect(reverse('auth:verify_login'))

            # Mark the user as verified
            user.is_logged_in_verified = True  # Set it to True once they verify
            user.login_code = None
            user.login_code_expiry = None
            user.save()
            
            messages.success(request, 'Your email has been successfully verified!')
            return redirect(reverse('user:dashboard'))

        except Exception as e:
            messages.error(request, f'Invalid code. Please request a new code')
            return redirect(reverse('auth:verify_login'))


def forgot_password_view(request):
    if request.method == "GET":
        return render(request, f"{template_root}/forgot_password.html")

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return json_response(
                False, "User with this email does not exist.", status=200
            )

        if not user.is_active:
            return json_response(False, "Account is not active.", status=200)

        # Generate Reset Token
        reset_token = user.generate_reset_token()

        # Send Reset Link via Email
        reset_link = f"http://yourfrontend.com/reset-password/{reset_token}/"  # Update with frontend URL
        send_email(
            "Password Reset Link",
            f"Click the link to reset your password: {reset_link}",
            [email],
        )

        return json_response(True, "Password reset link sent to your email.")


def reset_password_view(request, token):
    if request.method == "GET":
        return render(request, f"{template_root}/reset_password.html")

    if request.method == "POST":
        new_password = request.POST.get("new_password")

        try:
            user = User.objects.get(reset_token=token, reset_token_expiry__gt=now())
        except User.DoesNotExist:
            return json_response(False, "Invalid or expired token.", status=400)

        user.set_password(new_password)
        user.reset_token = None  # Clear the token after successful reset
        user.reset_token_expiry = None
        user.save()

        return json_response(True, "Password reset successfully.")


def reset_password_sent_view(request):
    return render(request, f"{template_root}/reset_password_sent.html")


def reset_password_done_view(request):
    return render(request, f"{template_root}/reset_password_done.html")


def logout_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse("app:home"))
    
    user = request.user
    user.is_logged_in_verified = False
    user.save()
    logout(request)
    return redirect(reverse("auth:login"))

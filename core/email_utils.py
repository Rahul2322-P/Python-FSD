"""
Email utility functions for sending OTP verification codes.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EmailVerification


def send_verification_email(email, verification_type='registration'):
    """
    Generate a 6-digit OTP code, save it to DB, and send it via email.
    
    Args:
        email: The recipient email address
        verification_type: One of 'registration', 'login', 'admin_login'
    
    Returns:
        The EmailVerification object created
    """
    # Invalidate any previous unused codes for this email + type
    EmailVerification.objects.filter(
        email=email,
        verification_type=verification_type,
        is_verified=False
    ).delete()
    
    # Generate new 6-digit code
    code = EmailVerification.generate_code()
    
    # Create verification record (expires in 10 minutes)
    verification = EmailVerification.objects.create(
        email=email,
        verification_code=code,
        verification_type=verification_type,
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    
    # Build email content based on type
    if verification_type == 'registration':
        subject = '🌿 EcoLearn — Your Registration Verification Code'
        message = (
            f'Hello!\n\n'
            f'Thank you for signing up with EcoLearn — Sustainable Living Education Platform.\n\n'
            f'Your verification code is:\n\n'
            f'    ✅  {code}\n\n'
            f'This code will expire in 10 minutes.\n\n'
            f'If you did not request this, please ignore this email.\n\n'
            f'— The EcoLearn Team 🌍'
        )
    elif verification_type == 'login':
        subject = '🔐 EcoLearn — Your Login Verification Code'
        message = (
            f'Hello!\n\n'
            f'A login attempt was made on your EcoLearn account.\n\n'
            f'Your verification code is:\n\n'
            f'    ✅  {code}\n\n'
            f'This code will expire in 10 minutes.\n'
            f'If you did not attempt to log in, please change your password immediately.\n\n'
            f'— The EcoLearn Team 🌍'
        )
    elif verification_type == 'admin_login':
        subject = '🛡️ EcoLearn — Admin Login Verification Code'
        message = (
            f'Hello Administrator!\n\n'
            f'An admin login attempt was detected on EcoLearn.\n\n'
            f'Your admin verification code is:\n\n'
            f'    ✅  {code}\n\n'
            f'This code will expire in 10 minutes.\n'
            f'If you did not attempt this, your admin credentials may be compromised.\n\n'
            f'— The EcoLearn Security Team 🛡️'
        )
    else:
        subject = 'EcoLearn — Verification Code'
        message = f'Your verification code is: {code}\nExpires in 10 minutes.'
    
    # Send the email
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    
    return verification


def verify_otp_code(email, code, verification_type):
    """
    Verify the OTP code for a given email and type.
    
    Args:
        email: The email address
        code: The OTP code entered by the user
        verification_type: One of 'registration', 'login', 'admin_login'
    
    Returns:
        (True, verification_obj) if valid, (False, error_message) if invalid
    """
    try:
        verification = EmailVerification.objects.filter(
            email=email,
            verification_type=verification_type,
            is_verified=False,
        ).latest('created_at')
    except EmailVerification.DoesNotExist:
        return False, 'No verification code found. Please request a new one.'
    
    # Check expiry
    if verification.is_expired():
        return False, 'Verification code has expired. Please request a new one.'
    
    # Check max attempts (5 attempts max)
    if verification.attempts >= 5:
        return False, 'Too many failed attempts. Please request a new code.'
    
    # Check code
    if verification.verification_code != code.strip():
        verification.attempts += 1
        verification.save()
        remaining = 5 - verification.attempts
        return False, f'Invalid verification code. {remaining} attempt(s) remaining.'
    
    # Mark as verified
    verification.is_verified = True
    verification.save()
    
    return True, verification

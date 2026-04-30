from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import LearningModule, Challenge, UserProfile


class LearningModuleForm(forms.ModelForm):
    """Form for creating and editing learning modules with validation"""
    
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Detailed content (supports HTML)',
        }),
        help_text="You can use HTML formatting for rich content"
    )
    
    class Meta:
        model = LearningModule
        fields = ['title', 'description', 'content', 'difficulty_level', 'estimated_time', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter module title',
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description (min 10 characters)',
                'minlength': '10'
            }),
            'difficulty_level': forms.Select(attrs={'class': 'form-control'}),
            'estimated_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'help_text': 'Time in minutes'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_title(self):
        """Validate title uniqueness and length"""
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError('Title cannot be empty')
        if len(title) < 3:
            raise ValidationError('Title must be at least 3 characters')
        
        # Check for duplicate (excluding current instance on edit)
        qs = LearningModule.objects.filter(title__iexact=title)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(f'Module with title "{title}" already exists')
        return title
    
    def clean_description(self):
        """Validate description"""
        description = self.cleaned_data.get('description', '').strip()
        if not description:
            raise ValidationError('Description cannot be empty')
        if len(description) < 10:
            raise ValidationError('Description must be at least 10 characters')
        return description
    
    def clean_content(self):
        """Validate content"""
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise ValidationError('Content cannot be empty')
        return content
    
    def clean_estimated_time(self):
        """Validate estimated time"""
        time = self.cleaned_data.get('estimated_time')
        if time and time < 1:
            raise ValidationError('Estimated time must be at least 1 minute')
        return time


class ChallengeForm(forms.ModelForm):
    """Form for creating and editing challenges with validation"""
    
    class Meta:
        model = Challenge
        fields = ['title', 'description', 'points', 'difficulty', 'repeatable', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Challenge name',
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What is the challenge? (min 10 characters)',
                'minlength': '10'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Points for completing'
            }),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'repeatable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_title(self):
        """Validate title uniqueness and length"""
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError('Title cannot be empty')
        if len(title) < 3:
            raise ValidationError('Title must be at least 3 characters')
        
        # Check for duplicate
        qs = Challenge.objects.filter(title__iexact=title)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(f'Challenge with title "{title}" already exists')
        return title
    
    def clean_description(self):
        """Validate description"""
        description = self.cleaned_data.get('description', '').strip()
        if not description:
            raise ValidationError('Description cannot be empty')
        if len(description) < 10:
            raise ValidationError('Description must be at least 10 characters')
        return description
    
    def clean_points(self):
        """Validate points"""
        points = self.cleaned_data.get('points')
        if points and points < 1:
            raise ValidationError('Points must be at least 1')
        if points and points > 500:
            raise ValidationError('Points cannot exceed 500')
        return points


# ─────────────────────────────────────────────────────────────
# REGISTRATION FORM (Step 1: Collect user details)
# ─────────────────────────────────────────────────────────────

class CustomUserCreationForm(UserCreationForm):
    """User registration form — collects username, email, password."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
            'minlength': '3',
            'maxlength': '150'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repeat your password',
            'autocomplete': 'new-password',
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        kwargs.pop('request', None)  # Accept but ignore request kwarg
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Must be at least 8 characters'

    def clean_username(self):
        """Validate username format"""
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise ValidationError('Username cannot be empty')
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters')
        # Removed duplicate check to avoid database queries during form validation
        return username

    def clean_email(self):
        """Validate email format"""
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('Email is required')
        # Removed duplicate check to avoid database queries during form validation
        return email

    def clean_password2(self):
        """Validate password confirmation"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match')
        if password1 and len(password1) < 8:
            raise ValidationError('Password must be at least 8 characters')
        return password2

    def save(self, commit=True):
        """Save user with email"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────────────────────
# OTP VERIFICATION FORM (Used for all OTP steps)
# ─────────────────────────────────────────────────────────────

class OTPVerificationForm(forms.Form):
    """Form for entering the 6-digit email verification code."""
    
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center fw-bold',
            'placeholder': '● ● ● ● ● ●',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'maxlength': '6',
            'style': 'letter-spacing: 12px; font-size: 1.8rem; padding: 12px;',
            'id': 'otp-input',
        }),
        help_text='Enter the 6-digit code sent to your email.'
    )

    def clean_otp_code(self):
        code = self.cleaned_data.get('otp_code', '').strip()
        if not code:
            raise ValidationError('Verification code is required')
        if not code.isdigit():
            raise ValidationError('Code must contain only numbers')
        if len(code) != 6:
            raise ValidationError('Code must be exactly 6 digits')
        return code


# ─────────────────────────────────────────────────────────────
# LOGIN FORM (Step 1: Collect credentials)
# ─────────────────────────────────────────────────────────────

class CustomLoginForm(AuthenticationForm):
    """User login form — collects username, password, and caption code."""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your password',
            'autocomplete': 'current-password',
        })
    )
    captcha_code = forms.CharField(
        label='Caption code',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the caption shown above',
            'autocomplete': 'off',
        }),
        help_text='Enter the letters and numbers shown in the caption.',
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(request=request, *args, **kwargs)

    def clean_captcha_code(self):
        code = self.cleaned_data.get('captcha_code', '').strip()
        expected = (self.request.session.get('captcha_expected') or '').strip()
        if not code:
            raise ValidationError('Caption code is required')
        if not expected:
            raise ValidationError('Session captcha expired. Refresh and try again.')
        if code.replace(' ', '').upper() != expected.replace(' ', '').upper():
            raise ValidationError('The caption code does not match.')
        return code

    def clean(self):
        """Override clean to provide better error handling"""
        try:
            super().clean()
        except ValidationError as e:
            if 'invalid_login' in str(e.code):
                raise ValidationError('Invalid username or password')
            raise


# ─────────────────────────────────────────────────────────────
# ADMIN LOGIN FORM (Step 1: Collect credentials + admin secret)
# ─────────────────────────────────────────────────────────────

class CustomAdminLoginForm(AuthenticationForm):
    """Admin login form — collects username, password, admin secret, and caption code."""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Admin username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Admin password',
            'autocomplete': 'current-password',
        })
    )
    admin_secret = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter admin secret code',
            'autocomplete': 'off',
        }),
        help_text='Special admin access code required for administrator login.'
    )
    captcha_code = forms.CharField(
        label='Caption code',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the caption shown above',
            'autocomplete': 'off',
        }),
        help_text='Enter the letters and numbers shown in the caption.',
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(request=request, *args, **kwargs)

    def clean_admin_secret(self):
        """Validate the admin secret code"""
        secret = self.cleaned_data.get('admin_secret', '').strip()
        if not secret:
            raise ValidationError('Admin secret code is required')
        expected = getattr(settings, 'ADMIN_SECRET_CODE', 'ECOADMIN2026')
        if secret != expected:
            raise ValidationError('Invalid admin secret code. Access denied.')
        return secret

    def clean_captcha_code(self):
        code = self.cleaned_data.get('captcha_code', '').strip()
        expected = (self.request.session.get('captcha_expected') or '').strip()
        if not code:
            raise ValidationError('Caption code is required')
        if not expected:
            raise ValidationError('Session captcha expired. Refresh and try again.')
        if code.replace(' ', '').upper() != expected.replace(' ', '').upper():
            raise ValidationError('The caption code does not match.')
        return code

    def clean(self):
        """Override clean with better error handling"""
        try:
            cleaned_data = super().clean()
        except ValidationError as e:
            if 'invalid_login' in str(e.code):
                raise ValidationError('Invalid admin credentials. Access denied.')
            raise
        return cleaned_data


# ─────────────────────────────────────────────────────────────
# PROFILE UPDATE FORMS
# ─────────────────────────────────────────────────────────────

class UserProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'avatar_url']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'minlength': '10',
                'maxlength': '500'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. New York, USA',
                'maxlength': '100'
            }),
            'avatar_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/photo.jpg'
            }),
        }
    
    def clean_bio(self):
        """Validate bio"""
        bio = self.cleaned_data.get('bio', '').strip()
        if bio and len(bio) < 10:
            raise ValidationError('Bio must be at least 10 characters if provided')
        return bio
    
    def clean_avatar_url(self):
        """Validate avatar URL"""
        url = self.cleaned_data.get('avatar_url', '').strip()
        if url and not (url.startswith('http://') or url.startswith('https://')):
            raise ValidationError('Please provide a valid URL starting with http:// or https://')
        return url


class UserUpdateForm(forms.ModelForm):
    """Form for updating user account information"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name (optional)',
                'maxlength': '150'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name (optional)',
                'maxlength': '150'
            }),
        }
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('Email is required')
        
        # Check if email belongs to another user
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('This email is already in use')
        return email

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import LearningModule, Challenge


# ──────────────────────────────────────────────────────────────────────────────
#  Admin Content Forms
# ──────────────────────────────────────────────────────────────────────────────

class LearningModuleForm(forms.ModelForm):
    class Meta:
        model = LearningModule
        fields = ['title', 'description', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter module title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed content'}),
        }


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['title', 'description', 'points']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Challenge name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What is the challenge?'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# ──────────────────────────────────────────────────────────────────────────────
#  Sign-Up Form  (username + email + password → saved to PostgreSQL)
# ──────────────────────────────────────────────────────────────────────────────

class CustomUserCreationForm(UserCreationForm):
    """Signup: username, email, password1, password2 — all stored in PostgreSQL."""

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
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()   # saves username + email + hashed password to PostgreSQL
        return user


# ──────────────────────────────────────────────────────────────────────────────
#  User Login Form
#  caption = human verification code (any alphanumeric the user types back)
#  NOT stored in database — just used to verify human input
# ──────────────────────────────────────────────────────────────────────────────

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your username',
            'autocomplete': 'username',
        })
    )
    caption = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center fw-bold letter-spacing',
            'placeholder': 'Type the code shown above',
            'autocomplete': 'off',
            'style': 'letter-spacing: 4px; font-size: 1.2rem;',
        }),
        help_text='Enter the alphanumeric code shown on screen to verify you are human.'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your password',
            'autocomplete': 'current-password',
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        # Store request so view can access session-stored caption for validation
        self._request = request

    def clean_caption(self):
        """Validate that the typed code matches the session-stored code."""
        typed = self.cleaned_data.get('caption', '').strip().upper()
        if self._request:
            expected = self._request.session.get('login_caption_code', '')
            if not expected or typed != expected.upper():
                raise forms.ValidationError('Incorrect verification code. Please try again.')
        return typed


# ──────────────────────────────────────────────────────────────────────────────
#  Admin Login Form  (same caption verification logic — NOT stored in DB)
# ──────────────────────────────────────────────────────────────────────────────

class CustomAdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Admin username',
            'autocomplete': 'username',
        })
    )
    caption = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center fw-bold',
            'placeholder': 'Type the code shown above',
            'autocomplete': 'off',
            'style': 'letter-spacing: 4px; font-size: 1.2rem;',
        }),
        help_text='Enter the alphanumeric code shown on screen.'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Admin password',
            'autocomplete': 'current-password',
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self._request = request

    def clean_caption(self):
        """Validate that the typed code matches the session-stored code."""
        typed = self.cleaned_data.get('caption', '').strip().upper()
        if self._request:
            expected = self._request.session.get('admin_caption_code', '')
            if not expected or typed != expected.upper():
                raise forms.ValidationError('Incorrect verification code. Please try again.')
        return typed

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import LearningModule, Challenge, UserProfile

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

class CustomUserCreationForm(UserCreationForm):
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

    caption = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center fw-bold',
            'placeholder': 'Type the code shown above',
            'autocomplete': 'off',
            'style': 'letter-spacing: 4px; font-size: 1.2rem;',
        }),
        help_text='Enter the alphanumeric code shown on screen to verify you are human.'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_caption(self):
        typed = self.cleaned_data.get('caption', '').strip().upper()
        if self._request:
            expected = self._request.session.get('signup_caption_code', '')
            if not expected or typed != expected.upper():
                raise forms.ValidationError('Incorrect verification code. Please try again.')
        return typed

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

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

    def __init__(self, *args, **kwargs):
        self._request = kwargs.get('request')
        if not self._request and args:
            self._request = args[0]
        super().__init__(*args, **kwargs)

    def clean_caption(self):
        typed = self.cleaned_data.get('caption', '').strip().upper()
        if self._request:
            expected = self._request.session.get('login_caption_code', '')
            if not expected or typed != expected.upper():
                raise forms.ValidationError('Incorrect verification code. Please try again.')
        return typed

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

    def __init__(self, *args, **kwargs):
        self._request = kwargs.get('request')
        if not self._request and args:
            self._request = args[0]
        super().__init__(*args, **kwargs)

    def clean_caption(self):
        typed = self.cleaned_data.get('caption', '').strip().upper()
        if self._request:
            expected = self._request.session.get('admin_caption_code', '')
            if not expected or typed != expected.upper():
                raise forms.ValidationError('Incorrect verification code. Please try again.')

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'avatar_url']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about yourself...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. New York, USA'}),
            'avatar_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/photo.jpg'}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

import logging
import random
import string
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .models import LearningModule, Challenge, UserProfile
from .forms import (
    CustomUserCreationForm, CustomLoginForm, CustomAdminLoginForm,
    LearningModuleForm, ChallengeForm,
    UserProfileUpdateForm, UserUpdateForm
)

logger = logging.getLogger(__name__)


def _generate_captcha_code(request):
    code = ''.join(random.choices(string.ascii_uppercase, k=4)) + ''.join(random.choices(string.digits, k=4))
    request.session['captcha_expected'] = code
    return f"{code[:4]} {code[4:]}"


# ═══════════════════════════════════════════════════════════════
#  REGISTRATION FLOW  (Direct account creation without email OTP)
# ═══════════════════════════════════════════════════════════════

def register(request):
    """Collect user registration details and create an account."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Ensure database is migrated before creating user
            from django.core.management import call_command
            call_command('migrate', interactive=False, verbosity=0)
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to EcoLearn, {user.username}! Your account has been created.")
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below and try again.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'core/register.html', {'form': form})


# ═══════════════════════════════════════════════════════════════
#  USER LOGIN FLOW  (Direct credentials only, with a caption challenge)
# ═══════════════════════════════════════════════════════════════

def user_login(request):
    """Collect user login credentials and perform a caption challenge."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}! 🌿")
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the login errors and try again.')
    else:
        form = CustomLoginForm(request)

    captcha_text = _generate_captcha_code(request)
    return render(request, 'core/login.html', {'form': form, 'captcha_text': captcha_text})


# ═══════════════════════════════════════════════════════════════
#  ADMIN LOGIN FLOW  (Direct credentials + secret code)
# ═══════════════════════════════════════════════════════════════

def admin_login(request):
    """Collect admin login credentials and admin secret code."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('custom_admin_dashboard')

    if request.method == 'POST':
        form = CustomAdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_staff:
                messages.error(request, 'Access denied. You do not have administrator privileges.')
                return redirect('admin_login')

            login(request, user)
            messages.success(request, f"Admin access granted. Welcome, {user.username}! 🛡️")
            return redirect('custom_admin_dashboard')
        else:
            messages.error(request, 'Please fix the admin login errors and try again.')
    else:
        form = CustomAdminLoginForm(request)

    captcha_text = _generate_captcha_code(request)
    return render(request, 'core/admin_login.html', {
        'form': form,
        'captcha_text': captcha_text,
    })


# ═══════════════════════════════════════════════════════════════
#  HOME & DASHBOARD
# ═══════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
#  HOME & DASHBOARD
# ═══════════════════════════════════════════════════════════════

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')


@login_required
def dashboard(request):
    try:
        profile = request.user.userprofile
    except Exception:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    completed_modules = profile.completed_modules.all()
    completed_challenges = profile.completed_challenges.all()
    all_modules = LearningModule.objects.all()
    all_challenges = Challenge.objects.all()

    context = {
        'profile': profile,
        'completed_modules': completed_modules,
        'completed_challenges': completed_challenges,
        'module_progress': len(completed_modules) / len(all_modules) * 100 if all_modules else 0,
        'challenge_progress': len(completed_challenges) / len(all_challenges) * 100 if all_challenges else 0,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileUpdateForm(request.POST, instance=request.user.userprofile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = UserProfileUpdateForm(instance=request.user.userprofile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'core/profile.html', context)


# ═══════════════════════════════════════════════════════════════
#  MODULES & CHALLENGES
# ═══════════════════════════════════════════════════════════════

@login_required
def module_list(request):
    try:
        profile = request.user.userprofile
    except Exception:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
    modules = LearningModule.objects.all()
    completed_modules = profile.completed_modules.all()
    return render(request, 'core/module_list.html', {
        'modules': modules, 'completed_modules': completed_modules
    })


@login_required
def module_detail(request, pk):
    try:
        profile = request.user.userprofile
    except Exception:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
    module = get_object_or_404(LearningModule, pk=pk)
    is_completed = module in profile.completed_modules.all()
    return render(request, 'core/module_detail.html', {
        'module': module, 'is_completed': is_completed
    })


@login_required
def complete_module(request, pk):
    if request.method == 'POST':
        try:
            profile = request.user.userprofile
        except Exception:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
        module = get_object_or_404(LearningModule, pk=pk)
        profile.completed_modules.add(module)
        messages.success(request, f"Congratulations! You completed '{module.title}'.")
        return redirect('module_detail', pk=pk)
    return redirect('modules')


@login_required
def challenge_list(request):
    try:
        profile = request.user.userprofile
    except Exception:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
    challenges = Challenge.objects.all()
    completed_challenges = profile.completed_challenges.all()
    return render(request, 'core/challenge_list.html', {
        'challenges': challenges, 'completed_challenges': completed_challenges
    })


@login_required
def complete_challenge(request, pk):
    if request.method == 'POST':
        try:
            profile = request.user.userprofile
        except Exception:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
        challenge = get_object_or_404(Challenge, pk=pk)
        if challenge not in profile.completed_challenges.all():
            profile.completed_challenges.add(challenge)
            messages.success(request, f"Challenge completed! You earned {challenge.points} point(s).")
    return redirect('challenges')


# ═══════════════════════════════════════════════════════════════
#  ADMIN MANAGEMENT VIEWS
# ═══════════════════════════════════════════════════════════════

def is_staff(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff, login_url='admin_login')
def custom_admin_dashboard(request):
    modules = LearningModule.objects.all()
    challenges = Challenge.objects.all()
    users = User.objects.select_related('userprofile').all().order_by('-date_joined')
    context = {
        'modules': modules,
        'challenges': challenges,
        'users': users,
        'total_users': users.count(),
        'total_modules': modules.count(),
        'total_challenges': challenges.count(),
    }
    return render(request, 'core/custom_admin/dashboard.html', context)


@user_passes_test(is_staff, login_url='admin_login')
def custom_admin_module_create(request):
    if request.method == 'POST':
        form = LearningModuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Module created successfully.")
            return redirect('custom_admin_dashboard')
    else:
        form = LearningModuleForm()
    return render(request, 'core/custom_admin/form.html', {'form': form, 'title': 'Create Module'})


@user_passes_test(is_staff, login_url='admin_login')
def custom_admin_module_edit(request, pk):
    module = get_object_or_404(LearningModule, pk=pk)
    if request.method == 'POST':
        form = LearningModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, "Module updated successfully.")
            return redirect('custom_admin_dashboard')
    else:
        form = LearningModuleForm(instance=module)
    return render(request, 'core/custom_admin/form.html', {'form': form, 'title': 'Edit Module'})


@user_passes_test(is_staff, login_url='admin_login')
def custom_admin_module_delete(request, pk):
    module = get_object_or_404(LearningModule, pk=pk)
    if request.method == 'POST':
        module.delete()
        messages.success(request, "Module deleted successfully.")
        return redirect('custom_admin_dashboard')
    return render(request, 'core/custom_admin/confirm_delete.html', {'obj': module, 'title': 'Delete Module'})


@user_passes_test(is_staff, login_url='admin_login')
def custom_admin_challenge_create(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Challenge created successfully.")
            return redirect('custom_admin_dashboard')
    else:
        form = ChallengeForm()
    return render(request, 'core/custom_admin/form.html', {'form': form, 'title': 'Create Challenge'})


@user_passes_test(is_staff, login_url='admin_login')
def custom_admin_challenge_edit(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    if request.method == 'POST':
        form = ChallengeForm(request.POST, instance=challenge)
        if form.is_valid():
            form.save()
            messages.success(request, "Challenge updated successfully.")
            return redirect('custom_admin_dashboard')
    else:
        form = ChallengeForm(instance=challenge)
    return render(request, 'core/custom_admin/form.html', {'form': form, 'title': 'Edit Challenge'})


@user_passes_test(is_staff, login_url='admin_login')
def custom_admin_challenge_delete(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    if request.method == 'POST':
        challenge.delete()
        messages.success(request, "Challenge deleted successfully.")
        return redirect('custom_admin_dashboard')
    return render(request, 'core/custom_admin/confirm_delete.html', {'obj': challenge, 'title': 'Delete Challenge'})

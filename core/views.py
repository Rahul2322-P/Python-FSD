import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .models import LearningModule, Challenge, UserProfile
from .forms import (
    CustomUserCreationForm, CustomLoginForm, CustomAdminLoginForm,
    LearningModuleForm, ChallengeForm,
)


# ──────────────────────────────────────────────────────────────────────────────
#  Helper: generate a random alphanumeric caption code
# ──────────────────────────────────────────────────────────────────────────────

def _generate_caption_code(length=6):
    """Return a random uppercase alphanumeric string, e.g. 'A3K9BX'."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


# ──────────────────────────────────────────────────────────────────────────────
#  User Login  (caption = human-verification code, NOT stored in DB)
# ──────────────────────────────────────────────────────────────────────────────

class UserLoginView(LoginView):
    template_name = 'core/login.html'
    authentication_form = CustomLoginForm

    def get(self, request, *args, **kwargs):
        # Generate a fresh code on every GET and store it in session
        code = _generate_caption_code()
        request.session['login_caption_code'] = code
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['caption_code'] = self.request.session.get('login_caption_code', '')
        return ctx

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        # Clear the used caption code from session — not storing it in DB
        self.request.session.pop('login_caption_code', None)
        messages.success(self.request, f"Welcome back, {user.username}!")
        return redirect('dashboard')

    def form_invalid(self, form):
        # Regenerate code on failed attempt
        code = _generate_caption_code()
        self.request.session['login_caption_code'] = code
        return super().form_invalid(form)


# ──────────────────────────────────────────────────────────────────────────────
#  Admin Login  (caption = human-verification code, NOT stored in DB)
# ──────────────────────────────────────────────────────────────────────────────

class AdminLoginView(LoginView):
    template_name = 'core/admin_login.html'
    authentication_form = CustomAdminLoginForm

    def get(self, request, *args, **kwargs):
        code = _generate_caption_code()
        request.session['admin_caption_code'] = code
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['caption_code'] = self.request.session.get('admin_caption_code', '')
        return ctx

    def form_valid(self, form):
        user = form.get_user()
        if user.is_staff:
            login(self.request, user)
            self.request.session.pop('admin_caption_code', None)
            messages.success(self.request, f"Admin access granted. Welcome, {user.username}!")
            return redirect('custom_admin_dashboard')
        else:
            messages.error(self.request, "Access denied. You do not have administrator privileges.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        code = _generate_caption_code()
        self.request.session['admin_caption_code'] = code
        return super().form_invalid(form)


# ──────────────────────────────────────────────────────────────────────────────
#  Home
# ──────────────────────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')


# ──────────────────────────────────────────────────────────────────────────────
#  Register  (stores username + email + password in PostgreSQL)
# ──────────────────────────────────────────────────────────────────────────────

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created! Welcome, {user.username}!")
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})


# ──────────────────────────────────────────────────────────────────────────────
#  Dashboard
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    profile = request.user.userprofile
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


# ──────────────────────────────────────────────────────────────────────────────
#  Modules
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def module_list(request):
    modules = LearningModule.objects.all()
    profile = request.user.userprofile
    completed_modules = profile.completed_modules.all()
    return render(request, 'core/module_list.html', {
        'modules': modules, 'completed_modules': completed_modules
    })


@login_required
def module_detail(request, pk):
    module = get_object_or_404(LearningModule, pk=pk)
    profile = request.user.userprofile
    is_completed = module in profile.completed_modules.all()
    return render(request, 'core/module_detail.html', {
        'module': module, 'is_completed': is_completed
    })


@login_required
def complete_module(request, pk):
    if request.method == 'POST':
        module = get_object_or_404(LearningModule, pk=pk)
        profile = request.user.userprofile
        profile.completed_modules.add(module)
        messages.success(request, f"Congratulations! You completed '{module.title}'.")
        return redirect('module_detail', pk=pk)
    return redirect('modules')


# ──────────────────────────────────────────────────────────────────────────────
#  Challenges
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def challenge_list(request):
    challenges = Challenge.objects.all()
    profile = request.user.userprofile
    completed_challenges = profile.completed_challenges.all()
    return render(request, 'core/challenge_list.html', {
        'challenges': challenges, 'completed_challenges': completed_challenges
    })


@login_required
def complete_challenge(request, pk):
    if request.method == 'POST':
        challenge = get_object_or_404(Challenge, pk=pk)
        profile = request.user.userprofile
        if challenge not in profile.completed_challenges.all():
            profile.completed_challenges.add(challenge)
            messages.success(request, f"Challenge completed! You earned {challenge.points} point(s).")
    return redirect('challenges')


# ──────────────────────────────────────────────────────────────────────────────
#  Custom Admin Views
# ──────────────────────────────────────────────────────────────────────────────

def is_staff(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff, login_url='admin_login')
def custom_admin_dashboard(request):
    modules = LearningModule.objects.all()
    challenges = Challenge.objects.all()
    # Fetch all users with their profiles for display in admin dashboard
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

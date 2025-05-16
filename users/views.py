from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
# Create your views here.
from django.contrib.auth.views import LoginView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from PIL import Image

from .forms import UpdateUserForm, UpdateProfileForm

from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView

from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin

from django.contrib.auth.views import LogoutView
from .forms import RegisterForm


class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, _('Вітаю %(user)s') % {'user': user})
        return super().form_valid(form)




class UserLogoutView(LogoutView):
    def get(self, request):
        logout(request)
        return redirect('users:login')


def users_home(request):
    # Очистити старі повідомлення, якщо треба
    storage = messages.get_messages(request)
    list(storage)  # Цей рядок "витягує" всі повідомлення і очищає чергу
    return render(request, 'registration/users_home.html')



class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'registration/register.html'
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, _('Створений акаунт для %(username)s') % {'username': username})
            return redirect('users:users_home')
        return render(request, self.template_name, {'form': form})




@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Твій акаунт оновлено успішно!'))
            return redirect(to='users:users_profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
    return render(request, 'registration/profile.html', {'user_form': user_form, 'profile_form': profile_form})




class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_message = _(
        "Ми щойно надіслали інструкції для зміни пароля (якщо акаунт з цією адресою "
        "існує). Лист має прийти незабаром. Якщо його не буде — перевір спам і "
        "чи правильно введено електронну адресу."
    )
    success_url = reverse_lazy('users:users_home')



class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'registration/change_password.html'
    success_message = _("Ваш пароль успішно змінено!")
    success_url = reverse_lazy('users:users_home')



class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')




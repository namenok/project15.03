from django.contrib.auth import logout
from django.shortcuts import render, redirect

# Create your views here.
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages


class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f'Welcome {user}')
        return super().form_valid(form)



from django.contrib.auth.views import LogoutView
class UserLogoutView(LogoutView):
    def get(self, request):
        logout(request)
        return redirect('login')



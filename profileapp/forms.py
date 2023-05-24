from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class PasswordChangeForm(UserCreationForm):
    class Meta:
            model = User
            fields = ["password"]

# from django.shortcuts import render,
# from django.http import HttpResponse,Http404
# from .forms import RegisterUserForm
# from django.contrib.auth.models import User
# 
# def register(request):
# form=RegisterUserForm
# context={'form':form}
# return render(request,'register.html',context)\n

# class RegisterUserForm(UserCreationForm):
#     email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')\n class Meta:\n model = User\n fields = ('username', 'email', 'password1', 'password2')

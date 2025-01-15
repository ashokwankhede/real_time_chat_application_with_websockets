from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import AppUserRegistrationForm, UserLoginForm
from django.contrib.auth import authenticate, login
from .models import AppUsers, ChatGroup



def register_user_view(request):
    if request.method == "POST":
        print(f"Request: {request.POST}")
        form = AppUserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            print("form Validation done")
            form.save()
            return redirect('login')
        else:
            print("Form validation failed")
            print(form.errors) 
        
    form = AppUserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})



def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = UserLoginForm()
    
    return render(request, 'auth/login.html', {'form':form})


@csrf_exempt
def chat_page(request):
    users = AppUsers.objects.all().order_by('-date_joined')
    groups = ChatGroup.objects.all().order_by('-created_at')
    return render(request, 'chat_app/chat.html', {'users': users, 'groups':groups})
    



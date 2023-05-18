from django.shortcuts import render, redirect
from .forms import NewUserForm, ProfileUpdateForm
from .models import Profile
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

def index(request): 
    if request.user.is_authenticated:
        userform = Profile.objects.get_or_create(user=request.user)
        form = ProfileUpdateForm(request.POST)
        all_profile = Profile.objects.all()
        profile = Profile.objects.get(user=request.user)
        verified = profile.verified
        verify_applied = profile.verify_applied
        if not(verified):
            if form.is_valid():
                fullname = form.cleaned_data.get('fullname')
                regid = form.cleaned_data.get('regid')
                acayear = form.cleaned_data.get('acayear')
                dept = form.cleaned_data.get('dept')
                email = form.cleaned_data.get('email')
                mobno = form.cleaned_data.get('mobno')
                usertype = form.cleaned_data.get('usertype')
                Profile.objects.filter(user_id=request.user.id).update(fullname=fullname)
                Profile.objects.filter(user_id=request.user.id).update(regid=regid)
                Profile.objects.filter(user_id=request.user.id).update(acayear=acayear)
                Profile.objects.filter(user_id=request.user.id).update(dept=dept)
                Profile.objects.filter(user_id=request.user.id).update(email=email)
                Profile.objects.filter(user_id=request.user.id).update(mobno=mobno)
                Profile.objects.filter(user_id=request.user.id).update(usertype=usertype)
                Profile.objects.filter(user_id=request.user.id).update(verify_applied=True)
        else:
            usertype = profile.usertype
            if usertype=='ad':
                return redirect("/user/admin")
            elif usertype=='fa':
                return redirect("/user/faculty")
            else:
                return redirect("/user/student")
        if request.method == "POST":
            req_origin = request.POST.getlist('button-action')
            if ('edit_profile' in req_origin):
                verify_applied = False
        return render(request, 'login/index.html', {"uname":request.user.username,"form":form, 'verified':verified, "applied":verify_applied})
    else:
        return redirect("/login")

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("login")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request=request, template_name="login/register.html", context={"register_form":form})

def login_request(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.info(request, f"You are now logged in as {username}.")
                    return redirect("/")
                else:
                    messages.error(request,"Invalid username or password.")
            else:
                messages.error(request,"Invalid username or password.")
        form = AuthenticationForm()
        return render (request=request, template_name="login/login.html", context={"login_form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("/login")

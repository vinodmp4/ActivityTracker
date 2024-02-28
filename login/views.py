from django.shortcuts import render, redirect
from .forms import NewUserForm, ProfileUpdateForm, newotp
from .models import Profile, OTP
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.middleware import csrf
import random, string
from django.http import HttpRequest


def generateOTP(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(n))

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

def password_reset_request(request):
    csrf_token = csrf.get_token(request)
    form = '<form action="" method="POST"><input type="hidden" name="csrfmiddlewaretoken" value="'+csrf_token+'">'+'<tr><td>Registration ID</td><td><input name="regid"></td></tr></form>'
    form = format_html(form)
    reset_text = "Request Password Reset"
    if request.method == "POST":
        users = request.POST.getlist('regid')
        if len(users)>0:regid = users[0]
        password1 = request.POST.getlist('password1')
        password2 = request.POST.getlist('password2')
        if len(password1)>0:
            if len(password2)>0:
                if password1[0] == password2[0]:
                    try:
                        user_ref = request.POST.getlist('otpref')
                        if len(user_ref)>0:
                            otpobj = OTP.objects.get(owner=user_ref[0])
                            otpobj.delete()
                        user = Profile.objects.filter(regid=regid)
                        this_user = User.objects.get(pk=user.values('user')[0]['user'])
                        this_user.set_password(password1[0])
                        this_user.save()
                    except Profile.DoesNotExist:
                        return redirect("/login")
                    return redirect("/login")
        try:
            user = Profile.objects.filter(regid=regid)
            otp = request.POST.getlist('otp')
            if len(otp)>0:
                query_otp = otp[0] #AE0PGQ
                try:
                    reference_otp = OTP.objects.get(owner=user.values('id')[0]['id'])
                except OTP.DoesNotExist:
                    reference_otp = OTP(owner= user.values('id')[0]['id'], text= generateOTP(6), verified=False)
                    reference_otp.save()
                if (query_otp == reference_otp.text):
                    form = '<form action="" method="POST"><input type="hidden" name="csrfmiddlewaretoken" value="'+csrf_token+'"><input type="hidden" name="regid" value="'+regid+'">'+'<input type="hidden" name="otpref" value="'+str(user.values('id')[0]['id'])+'">'+'<td>New Password</td><td><input type="password" name="password1"></td></tr><tr><td>Confirm Password</td><td><input type="password" name="password2"></td></tr></form>'
                    form = format_html(form)
                    reset_text = "Change Password"
                else:
                    form = '<center>Wrong OTP</br>Contact your Mentor for OTP.</br>Bring your ID Card for Verification.</center></br><form action="" method="POST"><input type="hidden" name="csrfmiddlewaretoken" value="'+csrf_token+'"><input type="hidden" name="regid" value="'+regid+'">'+'<tr><td>OTP</td><td><input name="otp"></td></tr></form>'
                    form = format_html(form)
                    reset_text = "Verify"
            else:
                try:
                    reference_otp = OTP.objects.get(owner=user.values('id')[0]['id'])
                except OTP.DoesNotExist:
                    reference_otp = OTP(owner= user.values('id')[0]['id'], text= generateOTP(6), verified=False)
                    reference_otp.save()
                    
                form = '<center>Contact your Administrator for OTP.</br>Bring your ID Card for Verification.</center></br><form action="" method="POST"><input type="hidden" name="csrfmiddlewaretoken" value="'+csrf_token+'"><input type="hidden" name="regid" value="'+regid+'">'+'<tr><td>OTP</td><td><input name="otp"></td></tr></form>'
                form = format_html(form)
                reset_text = "Verify"
        except Profile.DoesNotExist:
            form = '<form action="" method="POST"><input type="hidden" name="csrfmiddlewaretoken" value="'+csrf_token+'">'+'<tr><td>Registration ID</td><td><input name="regid" value="'+regid+'">\
</td></tr></form><tr><td><font style="color:red;">Invalid Registration ID</font></td><td><font style="color:red;">'+regid+'</font></td></tr>'
            form = format_html(form)
    return render(request=request, template_name="login/reset_password.html", context={"reset_form":form, "reset_text":reset_text})

def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("/login")

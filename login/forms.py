from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class NewUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "password1","password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    fullname = forms.CharField(max_length=50, label=("Full Name"))
    regid = forms.CharField(max_length=15, label=("Registration ID"))
    acayear = forms.CharField(max_length=20, label=("Academic/ Joining Year"))
    dept = forms.CharField(max_length=50, label=("Department"))
    email = forms.CharField(max_length=50, label=("E Mail"))
    mobno = forms.CharField(max_length=10, label=("Mobile"))
    usertype = forms.ChoiceField(choices=(('st','Student'),('fa','Faculty'),('ad','Administrator')))
    fullname.widget.attrs.update({'class':'regfield'})
    regid.widget.attrs.update({'class':'regfield'})
    acayear.widget.attrs.update({'class':'regfield'})
    dept.widget.attrs.update({'class':'regfield'})
    email.widget.attrs.update({'class':'regfield'})
    mobno.widget.attrs.update({'class':'regfield'})
    usertype.widget.attrs.update({'class':'regfield'})
    class Meta:
        model = Profile
        fields = ['fullname','regid','acayear','dept','email','mobno','usertype']

        
    

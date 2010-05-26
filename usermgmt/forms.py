from usermgmt.models import *
from django import forms

class UserProfileForm(forms.ModelForm):
    interests = forms.CharField(widget = forms.Textarea)
    class Meta:
        model = Profile

class ContactForm(forms.Form):
    subject = forms.CharField(max_length = 120, label = 'Subject')
    message = forms.CharField(label = 'Message', widget = forms.Textarea)
    sender = forms.EmailField(label = 'Your email address')

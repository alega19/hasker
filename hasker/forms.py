import re

from django import forms
from django.contrib.auth import authenticate

from . import models


class SignupForm(forms.ModelForm):

    password = forms.CharField(min_length=8, max_length=32, widget=forms.PasswordInput(), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(), label='Repeat password')

    def clean_password(self):
        password = self.cleaned_data['password']
        has_letter = bool(re.search('[A-Za-z]', password))
        has_digit = bool(re.search('\d', password))
        has_special = bool(re.search("[#$%'^,()*+.:|=?@/\[\]_`{}!;\-~]", password))
        if has_letter + has_digit + has_special < 2:
            raise forms.ValidationError(u"Password must include at least two of the following elements: "
                                        u"a letter, a digit, a special character (#$%'^,()*+.:|=?@/[]_`{}!;-~)")
        return password

    def clean(self):
        super(SignupForm, self).clean()
        password = self.cleaned_data.get('password')
        if password:
            if password != self.cleaned_data.get('password2'):
                raise forms.ValidationError(u'Passwords do not match')
            if password == self.cleaned_data.get('username'):
                raise forms.ValidationError(u'Password and username must not match')

    def save(self, commit=True):
        raw_password = self.cleaned_data.get('password')
        self.instance.set_password(raw_password)
        super(SignupForm, self).save(commit)

    class Meta:
        model = models.User
        fields = ('username', 'email', 'password', 'password2', 'avatar')
        widgets = {'password': forms.PasswordInput()}
        help_texts = {'username': u'Letters, digits and @/./+/-/_ only'}


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, req=None, *args, **kwargs):
        self._req = req
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        self.user = authenticate(self._req, username=username, password=password)
        if not self.user:
            raise forms.ValidationError(u'Incorrect username/password')


class SettingsForm(forms.Form):
    email = forms.EmailField()
    avatar = forms.ImageField(required=False)

    def __init__(self, user=None, *args, **kwargs):
        self._user = user
        super(SettingsForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if email != self._user.email and models.User.objects.filter(email=email).exists():
            raise forms.ValidationError(u'A user with that email already exists')
        return email


class AskForm(forms.Form):
    title = forms.CharField()
    text = forms.CharField(widget=forms.Textarea())
    tags = forms.CharField(required=False)

    def clean_tags(self):
        tags = self.cleaned_data['tags'].split(',')
        tags = [tag.strip().lower() for tag in tags if tag.strip()]
        if len(tags) > 3:
            raise forms.ValidationError('There should be no more than three tags')
        return tags


class AnswerForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(), label='')

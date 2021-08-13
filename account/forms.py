from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm
from django import forms
from django.forms import widgets
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class RegisterForm(UserCreationForm):
    username = forms.CharField(widget = forms.TextInput(attrs={
         "class":"input",
         "type":"username",
         "placeholder":"id",
     }),label="Username", error_messages={'unique' : '입력하신 이름을 사용하는 유저가 이미 존재합니다',
                                            'max_length' : '이름은 최대 150글자까지 작성할 수 있습니다'})

    password1 = forms.CharField(widget = forms.TextInput(attrs={
         "class":"input",
         "type":"password",
         "placeholder":"enter password",
     }),label="password")

    password2 = forms.CharField(widget = forms.TextInput(attrs={
         "class":"input",
         "type":"password",
         "placeholder":"confirm password",
     }),label="password")

    nickname = forms.CharField(widget = forms.TextInput(attrs={
         "class":"input",
         "type":"nickname",
         "placeholder":"nickname",
     }),label="enter nickname", error_messages={'unique' : '입력하신 닉네임을 사용하는 유저가 이미 존재합니다'})

    email = forms.CharField(widget = forms.TextInput(attrs={
         "class":"input",
         "type":"email",
         "placeholder":"email",
     }),label="enter email")

    error_messages = {
        'password_mismatch': '입력하신 두 비밀번호가 같지 않습니다',
    }

    profile = forms.ImageField(widget = forms.FileInput(attrs={
         "class":"input",
         "type":"file",
     }),label="upload profile", required=False)

    class Meta:
        model = CustomUser
        fields = ['username','password1','password2','nickname','email', 'profile']
    
    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        users = CustomUser.objects.all()
        for user in users:
            if user.nickname == nickname:
                raise ValidationError("이미 같은 닉네임을 사용하는 유저가 있습니다")
        return nickname
    
    # def clean_password2(self):
    #     password = self.cleaned_data.get('password2')
    #     if len(password) < 8:
    #         raise ValidationError("비밀번호는 최소 8글자 이상이어야 합니다")
    #     return password

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = '기존 비밀번호'
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'autofocus': False,
            'placeholder':"old password"
        })
        self.fields['new_password1'].label = '새 비밀번호'
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder':"new password"
        })
        self.fields['new_password2'].label = '새 비밀번호 확인'
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder':"confirm new password"
        })

    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']

class CustomUserChangeForm(UserChangeForm):
    password=None
    class Meta:
        model = get_user_model()
        fields = ['nickname', 'profile']

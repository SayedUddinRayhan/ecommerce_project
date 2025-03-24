from django import forms
from django.contrib.auth.models import User
from .models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False  # Set inactive until email verification
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),  # Email is read-only
        }

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class PasswordChangeFormCustom(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
User = get_user_model()


class RegistrationForm(forms.ModelForm):
    """Registration form with password confirmation, role and profile image"""
    ROLE_CHOICES = (
        ('writer', 'Writer'),
        ('reader', 'Reader'),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'required': True
        }),
        min_length=8,
        label='Password'
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': True
        }),
        label='Confirm Password'
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Register As'
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('name', 'email')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'required': True
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        email = cleaned_data.get('email')

        # Check if email already exists
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered.')

        # Check if passwords match
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match.')

        return cleaned_data

    def save(self, commit=True):
        from .models import Role, UserRole, Permission, RolePermission

        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        # assign profile picture if provided
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            user.profile_image = picture

        if commit:
            user.save()

            # assign role
            role_name = self.cleaned_data.get('role') or 'reader'
            role_obj, _ = Role.objects.get_or_create(name=role_name)
            UserRole.objects.get_or_create(user=user, role=role_obj)

            # ensure basic permissions exist and assign to role
            if role_name == 'writer':
                perm_write, _ = Permission.objects.get_or_create(name='can_write')
                perm_read, _ = Permission.objects.get_or_create(name='can_read')
                perm_comment, _ = Permission.objects.get_or_create(name='can_comment')
                RolePermission.objects.get_or_create(role=role_obj, permission=perm_write)
                RolePermission.objects.get_or_create(role=role_obj, permission=perm_read)
                RolePermission.objects.get_or_create(role=role_obj, permission=perm_comment)
            else:
                perm_read, _ = Permission.objects.get_or_create(name='can_read')
                perm_comment, _ = Permission.objects.get_or_create(name='can_comment')
                RolePermission.objects.get_or_create(role=role_obj, permission=perm_read)
                RolePermission.objects.get_or_create(role=role_obj, permission=perm_comment)

        return user



class LoginForm(forms.Form):
    """Login form"""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'required': True
        }),
        label='Email Address'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': True
        }),
        label='Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise ValidationError('Invalid email or password.')
                if not user.is_active:
                    raise ValidationError('This account is inactive.')
            except User.DoesNotExist:
                raise ValidationError('Invalid email or password.')

        return cleaned_data

    def get_user(self):
        """Get the user object for this login"""
        email = self.cleaned_data.get('email')
        return User.objects.get(email=email)

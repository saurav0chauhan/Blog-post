from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
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


class SuperAdminCreateForm(forms.Form):
    """Form to create a new SuperAdmin"""
    
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter superadmin name',
            'required': True
        }),
        label='Full Name',
        max_length=100
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address',
            'required': True
        }),
        label='Email Address'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'required': True
        }),
        label='Password',
        min_length=8
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': True
        }),
        label='Confirm Password',
        min_length=8
    )

    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        email = cleaned_data.get('email')

        # Check if email already exists
        from .models import SuperAdmin
        if email and SuperAdmin.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered as SuperAdmin.')

        # Check if passwords match
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match.')

        return cleaned_data

    def save(self):
        from .models import SuperAdmin
        email = self.cleaned_data.get('email')
        name = self.cleaned_data.get('name')
        password = self.cleaned_data.get('password')
        profile_image = self.cleaned_data.get('profile_image')

        superadmin = SuperAdmin(
            email=email,
            name=name,
            password_hash=make_password(password),
            profile_image=profile_image
        )
        superadmin.save()
        return superadmin


class SuperAdminLoginForm(forms.Form):
    """Form for SuperAdmin login"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter superadmin email',
            'required': True
        }),
        label='Email Address'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'required': True
        }),
        label='Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            from .models import SuperAdmin
            from django.contrib.auth.hashers import check_password
            try:
                superadmin = SuperAdmin.objects.get(email=email)
                if not check_password(password, superadmin.password_hash):
                    raise ValidationError('Invalid email or password.')
                if not superadmin.is_active:
                    raise ValidationError('This superadmin account is inactive.')
            except SuperAdmin.DoesNotExist:
                raise ValidationError('Invalid email or password.')

        return cleaned_data

    def get_superadmin(self):
        """Get the superadmin object for this login"""
        email = self.cleaned_data.get('email')
        from .models import SuperAdmin
        return SuperAdmin.objects.get(email=email)


class SuperAdminRegisterForm(forms.Form):
    """Form to register a new SuperAdmin with approval"""
    
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'required': True
        }),
        label='Full Name',
        max_length=100
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'required': True
        }),
        label='Email Address'
    )

    company = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your company name',
            'required': False
        }),
        label='Company Name',
        max_length=255,
        required=False
    )

    admin_type = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='Admin Type',
        help_text='Select your administrative role'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password (minimum 8 characters)',
            'required': True
        }),
        label='Password',
        min_length=8
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': True
        }),
        label='Confirm Password',
        min_length=8
    )

    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import SuperAdminType
        self.fields['admin_type'].queryset = SuperAdminType.objects.all().order_by('permissions_level')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        email = cleaned_data.get('email')
        admin_type = cleaned_data.get('admin_type')

        # Check if email already exists
        from .models import SuperAdmin
        if email and SuperAdmin.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered as SuperAdmin.')

        # Check if admin_type is selected
        if not admin_type:
            raise ValidationError('Please select an admin type.')

        # Check if passwords match
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match.')

        return cleaned_data

    def save(self):
        from .models import SuperAdmin
        email = self.cleaned_data.get('email')
        name = self.cleaned_data.get('name')
        company = self.cleaned_data.get('company')
        admin_type = self.cleaned_data.get('admin_type')
        password = self.cleaned_data.get('password')
        profile_image = self.cleaned_data.get('profile_image')

        # Create inactive superadmin pending approval
        superadmin = SuperAdmin(
            email=email,
            name=name,
            company=company,
            admin_type=admin_type,
            password_hash=make_password(password),
            profile_image=profile_image,
            is_active=False  # Pending approval
        )
        superadmin.save()
        return superadmin


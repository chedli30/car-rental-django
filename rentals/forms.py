from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UserRegistrationForm(forms.ModelForm):
    """Form for user registration with email verification."""
    
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre mot de passe',
        }),
        validators=[validate_password],
        help_text='Le mot de passe doit contenir au moins 8 caractères.'
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre mot de passe',
        }),
        help_text='Entrez le même mot de passe pour vérification.'
    )
    role = forms.ChoiceField(
        label='Rôle',
        choices=[('user', 'Client'), ('admin', 'Demande Admin')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='user'
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choisissez un nom d\'utilisateur',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre adresse email',
            }),
        }

    def clean_username(self):
        """Validate that username doesn't already exist."""
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Ce nom d\'utilisateur existe déjà.')
        if len(username) < 3:
            raise ValidationError('Le nom d\'utilisateur doit contenir au moins 3 caractères.')
        if len(username) > 30:
            raise ValidationError('Le nom d\'utilisateur ne peut pas dépasser 30 caractères.')
        return username

    def clean_email(self):
        """Validate that email doesn't already exist."""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Cette adresse email est déjà enregistrée.')
        return email

    def clean(self):
        """Validate that passwords match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Les mots de passe ne correspondent pas.')
        
        return cleaned_data


class AdminRegistrationForm(forms.Form):
    """Form for admin registration requests."""
    
    username = forms.CharField(
        label='Nom d\'utilisateur',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choisissez un nom d\'utilisateur',
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre adresse email professionnel',
        })
    )
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre mot de passe',
        }),
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre mot de passe',
        }),
    )
    reason = forms.CharField(
        label='Raison de la demande',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Expliquez pourquoi vous demandez l\'accès administrateur...',
            'rows': 3,
        }),
        required=False
    )

    def clean_password2(self):
        """Validate that passwords match."""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Les mots de passe ne correspondent pas.')
        return password2

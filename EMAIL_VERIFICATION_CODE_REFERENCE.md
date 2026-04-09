# Email Verification - Complete Code Reference

## 🔑 Core Implementation Snippets

### 1. Registration Flow (views.py)

```python
def register(request):
    """Handle user registration with email verification."""
    if request.user.is_authenticated:
        return redirect('/vehicles/')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            if role == 'user':
                # ✅ Create INACTIVE user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=False  # Important!
                )
                
                # ✅ Generate secure token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # ✅ Build verification URL
                verification_url = request.build_absolute_uri(
                    reverse('verify_email_token', 
                            kwargs={'uidb64': uid, 'token': token})
                )
                
                # ✅ Send email
                try:
                    send_verification_email(user, verification_url, request)
                    return redirect('email_sent', email=email)
                except Exception as e:
                    user.delete()
                    messages.error(request, f'Email error: {str(e)}')
                    return render(request, 'register.html', {'form': form})
            
            else:  # Admin registration
                RegistrationRequest.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password),
                    role='admin'
                )
                messages.success(request, 'Demande envoyée!')
                return redirect('register')
    
    form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})
```

### 2. Send Email Function (views.py)

```python
def send_verification_email(user, verification_url, request):
    """Send verification email with token link."""
    subject = '🚗 AutoLux - Vérifiez votre adresse email'
    
    # ✅ Render HTML template
    html_message = render_to_string('emails/verify_email.html', {
        'user': user,
        'verification_url': verification_url,
        'unsubscribe_url': request.build_absolute_uri('/'),
        'site_name': 'AutoLux',
    })
    
    # ✅ Plain text fallback
    plain_message = f"""
Bienvenue sur AutoLux!

Veuillez vérifier votre adresse email:
{verification_url}

Ce lien expire dans 24 heures.

Si vous n'avez pas créé de compte, ignorez cet email.
    """.strip()
    
    # ✅ Send email
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )
```

### 3. Verification View (views.py)

```python
def verify_email_token(request, uidb64, token):
    """
    Verify email token and activate user.
    
    Token format: /verify-email/<uidb64>/<token>/
    Example: /verify-email/MQ/abc-123-def/
    """
    try:
        # ✅ Decode base64 UID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        # Invalid UID
        context = {'error_type': 'invalid', 'email': None}
        return render(request, 'email_verification_error.html', 
                     context, status=400)

    # ✅ Validate token (checks expiration too)
    if not default_token_generator.check_token(user, token):
        context = {'error_type': 'expired', 'email': user.email}
        return render(request, 'email_verification_error.html', 
                     context, status=400)

    # ✅ Check if already verified
    if user.is_active:
        context = {'error_type': 'already_verified', 'email': user.email}
        return render(request, 'email_verification_error.html', context)

    # ✅ Activate user account
    user.is_active = True
    user.save()
    
    # ✅ Auto-login user
    user = User.objects.get(pk=user.pk)
    login(request, user)

    return render(request, 'email_verification_success.html', {'user': user})
```

### 4. Token Generation Explanation

```python
# Token generation process:
token = default_token_generator.make_token(user)

# What happens internally:
# 1. Gets current timestamp
# 2. Gets user's password hash  
# 3. Combines: user_id + timestamp + password_hash
# 4. Signs with HMAC-SHA256 using SECRET_KEY
# 5. Result: Something like "abc-123-def-456"

# Token validation:
if default_token_generator.check_token(user, token):
    # Checks:
    # 1. HMAC signature is valid
    # 2. Timestamp is within PASSWORD_RESET_TIMEOUT (24 hours)
    # 3. User's password_hash hasn't changed
    # 4. User exists
    
# Why this is secure:
# - HMAC prevents tampering
# - Timestamp prevents old tokens
# - Password hash prevents use after password change
# - Comparison is constant-time (no timing attacks)
```

---

## 📧 Email Template Key Sections

### Email Subject Line
```
🚗 AutoLux - Vérifiez votre adresse email
```

### Email Button HTML
```html
<div class="button-container">
    <a href="{{ verification_url }}" class="cta-button">
        Vérifier votre email
    </a>
</div>
```

### Fallback Link Section
```html
<div class="fallback-link">
    <strong>Si le bouton ne fonctionne pas:</strong>
    {{ verification_url }}
</div>
```

### Email Expiration Warning
```html
<div class="info-box">
    <strong>⏱️ Attention :</strong> Ce lien expire dans <strong>24 heures</strong>.
</div>
```

---

## 🔐 URL Patterns

```python
# rentals/urls.py

# Registration page (form)
path('register/', views.register, name='register'),

# After registration (confirmation page)
path('email-sent/', views.email_sent, name='email_sent'),

# Verification link (user clicks from email)
path('verify-email/<str:uidb64>/<str:token>/', 
     views.verify_email_token, name='verify_email_token'),

# Resend email (user requests new link)
path('resend-verification/', 
     views.resend_verification_email, name='resend_verification_email'),
```

### URL Examples

| Action | URL |
|--------|-----|
| Register | `/accounts/register/` |
| Check Email | `/accounts/email-sent/?email=user@example.com` |
| Verify (from email) | `/accounts/verify-email/MQ/abc123...def/` |
| Resend Email | `/accounts/resend-verification/` (POST) |

---

## ⚙️ Settings Configuration

### Development (DEBUG=True)
```python
# settings.py

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Outputs: ✅ Emails print to console

DEFAULT_FROM_EMAIL = 'noreply@autolux.local'
SERVER_EMAIL = 'noreply@autolux.local'

# Token expires in 24 hours
PASSWORD_RESET_TIMEOUT = 86400
```

### Production (DEBUG=False)
```python
# settings.py - update these values

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Change for your provider
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Use environment variables (NEVER hardcode credentials!)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = 'noreply@autolux.local'
```

### Environment Variables (Production)
```bash
# .env file or system environment
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="16-char-app-password"

# In Python:
import os
os.environ.get('EMAIL_HOST_USER')  # Retrieves value
```

---

## 📋 Forms Structure

### Form Fields
```python
class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label='Nom d\'utilisateur',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password],
    )
    
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    
    role = forms.ChoiceField(
        label='Rôle',
        choices=[('user', 'Client'), ('admin', 'Administrateur')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
```

### Form Validation
```python
def clean_username(self):
    username = self.cleaned_data['username']
    if User.objects.filter(username=username).exists():
        raise ValidationError('Ce nom d\'utilisateur existe déjà.')
    if len(username) < 3:
        raise ValidationError('Minimum 3 caractères.')
    return username

def clean_email(self):
    email = self.cleaned_data['email']
    if User.objects.filter(email=email).exists():
        raise ValidationError('Cet email est déjà enregistré.')
    return email

def clean(self):
    cleaned_data = super().clean()
    if (cleaned_data.get('password1') and 
        cleaned_data.get('password2')):
        if cleaned_data['password1'] != cleaned_data['password2']:
            raise ValidationError('Les mots de passe ne correspondent pas.')
```

---

## 🎨 Template Rendering in Views

### Register Template
```python
return render(request, 'register.html', {'form': form})

# Template accesses form fields:
{{ form.username }}  # Renders: <input type="text" class="form-control" ...>
{{ form.username.errors }}  # Shows any validation errors
{{ form.username.help_text }}  # Shows "Minimum 3 characters"
```

### Email Sent Template
```python
context = {'email': email}
return render(request, 'email_sent.html', context)

# Template shows:
{{ email }}  # User's email address
```

### Verification Success Template
```python
context = {'user': user}
return render(request, 'email_verification_success.html', context)

# Template shows:
{{ user.username }}  # Username
{{ user.email }}  # Email address
{{ user.first_name }}  # First name (if filled)
```

### Error Template
```python
context = {
    'error_type': 'expired',  # or 'invalid' or 'already_verified'
    'email': user.email,
}
return render(request, 'email_verification_error.html', context, status=400)

# Template shows different content based on error_type
```

---

## 🧪 Testing Snippets

### Manual Token Generation (For Testing)
```python
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

user = User.objects.get(username='testuser')
token = default_token_generator.make_token(user)
uid = urlsafe_base64_encode(force_bytes(user.pk))

# Manually create verification URL
verify_url = f'/accounts/verify-email/{uid}/{token}/'
print(verify_url)  # Copy and paste in browser
```

### Check Token Validity
```python
from django.contrib.auth.tokens import default_token_generator

user = User.objects.get(username='testuser')
token = 'token_from_email'

# Check if token is valid
is_valid = default_token_generator.check_token(user, token)
print(f"Token valid: {is_valid}")
```

### Console Backend Email Output
```
# When DEBUG=True, emails appear in console as:

"Content-Type: text/html; charset=\"utf-8\"\nMIME-Version: 1.0\nSubject: 🚗 AutoLux - Vérifiez votre adresse email\n\n<html>...<a href=\"http://localhost:8000/accounts/verify-email/MQ/abc-123def456/\">..."

# Extract the link:
# http://localhost:8000/accounts/verify-email/MQ/abc-123def456/
```

---

## 🔍 Database Checks

### Verify User Creation
```python
from django.contrib.auth.models import User

# Check if user was created with is_active=False
user = User.objects.get(username='newuser')
print(f"Active: {user.is_active}")  # Should be False

# After verification, should be True
print(f"Active: {user.is_active}")  # Should be True
```

### Check No Migrations Needed
```bash
$ python manage.py makemigrations --no-input
# Output: No changes detected
# This is correct - uses existing User model

$ python manage.py migrate
# Output: (no migrations to apply)
# This is correct - no new models, no new fields
```

---

## 📊 Flow Control Examples

### Decision Tree: Verification URL Click
```python
# User clicks link from email: /verify-email/<uidb64>/<token>/

if invalid_uidb64_format:
    # → error_type='invalid'
    # Show: "Link is corrupted"
    
elif user_with_uid_not_found:
    # → error_type='invalid'
    # Show: "User not found"
    
elif token_is_expired:
    # → error_type='expired'
    # Show: "Link expired, request new one"
    
elif token_is_invalid:
    # → error_type='expired'
    # Show: "Link is invalid"
    
elif user_already_active:
    # → error_type='already_verified'
    # Show: "Already verified, go to login"
    
else:
    # ✅ All checks pass
    # → Activate user (set is_active=True)
    # → Auto-login
    # → Show success page
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
```python
# ✅ Check DEBUG setting
DEBUG = False  # or check environment variable

# ✅ Check EMAIL_BACKEND
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# ✅ Check SMTP credentials
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# ✅ Run checks
python manage.py check  # Should show 0 issues

# ✅ Test email sending
python manage.py shell
# from django.core.mail import send_mail
# send_mail('Test', 'Test email', 'noreply@autolux.local', ['your@email.com'])
```

### Post-Deployment
```python
# ✅ Monitor email delivery
# Check logs for: "Email sent to user@email.com"

# ✅ Monitor verification completion
# Track: % of users who verify within 24 hours

# ✅ Monitor errors
# Track: Expired tokens, resend requests, failures

# ✅ Check bounce handling
# Setup: Email bounce notifications
```

---

## 📝 Key Variables Glossary

| Variable | Type | Purpose |
|----------|------|---------|
| `user` | User | Django User object |
| `token` | str | Email verification token |
| `uidb64` | str | Base64-encoded user ID for URL |
| `uid` | int | User ID (decoded from uidb64) |
| `verification_url` | str | Full URL for user to click |
| `email` | str | User's email address |
| `is_active` | bool | Account activation status |
| `PASSWORD_RESET_TIMEOUT` | int | Token expiration in seconds |
| `DEFAULT_FROM_EMAIL` | str | Sender email address |

---

## ✨ Pro Tips

1. **Token Debugging**
   ```python
   # See what token contains (don't deploy this debug code)
   import hashlib
   print(f"Token: {token}")
   print(f"UID: {uid}")
   ```

2. **Email Testing in Production**
   ```python
   # Send test email to yourself
   send_verification_email(user, verification_url, request)
   # Check: Delivery, rendering, link validity
   ```

3. **Resend Rate Limiting**
   ```python
   # Add rate limiting in production
   from django_ratelimit import ratelimit
   
   @ratelimit(key='user', rate='3/h')
   def resend_verification_email(request):
       # Max 3 resends per hour
   ```

4. **Monitor Verification Rates**
   ```python
   # Track which users completed verification
   verified_users = User.objects.filter(is_active=True)
   
   # Track which didn't
   unverified_users = User.objects.filter(is_active=False)
   ```

---

## 🎓 Further Learning

- Django tokens: https://github.com/django/django/blob/main/django/contrib/auth/tokens.py
- Email backends: https://docs.djangoproject.com/en/6.0/topics/email/
- Security: https://owasp.org/www-project-web-security-testing-guide/


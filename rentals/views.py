from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from .models import Rental, RegistrationRequest, Profile, Review
from .forms import UserRegistrationForm, AdminRegistrationForm
from vehicles.models import Vehicle
from datetime import datetime
from django.db import transaction
from django.contrib import messages
from django.db.models import Q

@login_required
def book_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Format de date invalide. Utilisez YYYY-MM-DD.')
            return render(request, 'rental_form.html', {'vehicle': vehicle})
        
        if start_date >= end_date:
            messages.error(request, 'La date de début doit être avant la date de fin.')
            return render(request, 'rental_form.html', {'vehicle': vehicle})
        
        if start_date < datetime.now().date():
            messages.error(request, 'La date de début ne peut pas être dans le passé.')
            return render(request, 'rental_form.html', {'vehicle': vehicle})
        
        with transaction.atomic():
            if not vehicle.is_available_for_dates(start_date, end_date):
                messages.error(request, 'Le véhicule n\'est pas disponible pour ces dates.')
                return render(request, 'rental_form.html', {'vehicle': vehicle})
            
            Rental.objects.create(
                customer=request.user,
                vehicle=vehicle,
                start_date=start_date,
                end_date=end_date
            )
            # Note: No longer setting vehicle.available = False, using date-based logic
        
        messages.success(request, 'Réservation confirmée!')
        return redirect('/rentals/history/')
    return render(request, 'rental_form.html', {'vehicle': vehicle})

@login_required
def rental_history(request):
    rentals = Rental.objects.filter(customer=request.user).order_by('-start_date')
    return render(request, 'rental_history.html', {'rentals': rentals})

@login_required
def user_dashboard(request):
    user_rentals = Rental.objects.filter(customer=request.user).order_by('-start_date')
    
    # Separate active and completed rentals
    active_rentals = user_rentals.filter(is_active=True, start_date__lte=datetime.now().date(), end_date__gte=datetime.now().date())
    upcoming_rentals = user_rentals.filter(is_active=True, start_date__gt=datetime.now().date())
    completed_rentals = user_rentals.filter(Q(is_active=False) | Q(end_date__lt=datetime.now().date()))
    
    # Calculate total spent
    total_spent = sum(rental.total_price for rental in completed_rentals if rental.total_price)
    
    context = {
        'active_rentals': active_rentals,
        'upcoming_rentals': upcoming_rentals,
        'completed_rentals': completed_rentals[:5],  # Show last 5
        'total_spent': total_spent,
        'total_rentals': user_rentals.count(),
    }
    
    return render(request, 'user_dashboard.html', context)

@login_required
def cancel_rental(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, customer=request.user)
    
    if rental.start_date <= datetime.now().date():
        messages.error(request, 'Impossible d\'annuler une location déjà commencée.')
        return redirect('/rentals/dashboard/')
    
    rental.is_active = False
    rental.save()
    messages.success(request, 'Location annulée avec succès.')
    return redirect('/rentals/dashboard/')

@login_required
def modify_rental(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, customer=request.user, is_active=True)
    
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Format de date invalide.')
            return redirect(f'/rentals/modify/{rental_id}/')
        
        if start_date >= end_date:
            messages.error(request, 'La date de début doit être avant la date de fin.')
            return redirect(f'/rentals/modify/{rental_id}/')
        
        if start_date < datetime.now().date():
            messages.error(request, 'La date de début ne peut pas être dans le passé.')
            return redirect(f'/rentals/modify/{rental_id}/')
        
        # Check if vehicle is available for new dates (excluding current rental)
        conflicting_rentals = Rental.objects.filter(
            vehicle=rental.vehicle,
            is_active=True
        ).exclude(id=rental_id).filter(
            Q(start_date__lt=end_date, end_date__gt=start_date)
        )
        
        if conflicting_rentals.exists():
            messages.error(request, 'Le véhicule n\'est pas disponible pour ces nouvelles dates.')
            return redirect(f'/rentals/modify/{rental_id}/')
        
        # Update rental
        rental.start_date = start_date
        rental.end_date = end_date
        rental.total_price = None  # Reset to force recalculation
        rental.save()  # This will recalculate total_price
        
        messages.success(request, 'Location modifiée avec succès.')
        return redirect('/rentals/dashboard/')
    
    return render(request, 'modify_rental.html', {'rental': rental})

@login_required
def review_rental(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, customer=request.user)
    
    # Check if rental is completed and no review exists
    if rental.is_active or rental.end_date > datetime.now().date():
        messages.error(request, 'Vous ne pouvez noter que les locations terminées.')
        return redirect('/rentals/dashboard/')
    
    if hasattr(rental, 'review'):
        messages.info(request, 'Vous avez déjà noté cette location.')
        return redirect('/rentals/dashboard/')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if not rating or not rating.isdigit() or int(rating) not in range(1, 6):
            messages.error(request, 'Veuillez sélectionner une note valide.')
            return redirect(f'/rentals/review/{rental_id}/')
        
        Review.objects.create(
            rental=rental,
            customer=request.user,
            vehicle=rental.vehicle,
            rating=int(rating),
            comment=comment
        )
        
        messages.success(request, 'Merci pour votre avis!')
        return redirect('/rentals/dashboard/')
    
    return render(request, 'review_rental.html', {'rental': rental})

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('/rentals/dashboard/')
    
    from vehicles.models import Vehicle
    from django.db.models import Sum, Count, Avg, Q
    from django.utils import timezone
    from django.contrib.auth.models import User
    import json
    from datetime import date, timedelta
    
    now_date = timezone.now().date()

    # ── Core KPIs ──────────────────────────────────────────────
    total_vehicles    = Vehicle.objects.count()
    total_rentals     = Rental.objects.count()
    active_rentals    = Rental.objects.filter(is_active=True, start_date__lte=now_date, end_date__gte=now_date).count()
    upcoming_rentals  = Rental.objects.filter(is_active=True, start_date__gt=now_date).count()
    total_users       = User.objects.filter(is_staff=False).count()
    pending_requests  = RegistrationRequest.objects.filter(approved=False).count()

    # ── Revenue ─────────────────────────────────────────────────
    all_completed = Rental.objects.filter(Q(is_active=False) | Q(end_date__lt=now_date)).select_related('vehicle')
    total_revenue = 0
    for r in all_completed:
        if r.total_price:
            total_revenue += r.total_price
        else:
            days = (r.end_date - r.start_date).days
            total_revenue += days * r.vehicle.price_per_day

    # ── Monthly Revenue (last 6 months) ─────────────────────────
    monthly_labels = []
    monthly_data   = []
    month_names_fr = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
    for i in range(5, -1, -1):
        # First day of month i months ago
        first_of_month = (now_date.replace(day=1) - timedelta(days=i*28)).replace(day=1)
        if first_of_month.month == 12:
            last_of_month = first_of_month.replace(year=first_of_month.year+1, month=1, day=1) - timedelta(days=1)
        else:
            last_of_month = first_of_month.replace(month=first_of_month.month+1, day=1) - timedelta(days=1)
        
        month_rentals = Rental.objects.filter(
            Q(is_active=False) | Q(end_date__lt=now_date),
            start_date__gte=first_of_month,
            start_date__lte=last_of_month
        ).select_related('vehicle')
        
        rev = 0
        for r in month_rentals:
            if r.total_price:
                rev += float(r.total_price)
            else:
                days = (r.end_date - r.start_date).days
                rev += days * float(r.vehicle.price_per_day)
        
        monthly_labels.append(month_names_fr[first_of_month.month - 1])
        monthly_data.append(round(rev, 2))

    # ── Rental status for donut chart ────────────────────────────
    completed_count = Rental.objects.filter(Q(is_active=False) | Q(end_date__lt=now_date)).count()
    status_data = [active_rentals, upcoming_rentals, completed_count]

    # ── Recent Rentals ───────────────────────────────────────────
    recent_rentals = Rental.objects.select_related('customer', 'vehicle').order_by('-start_date')[:10]

    # ── Top Vehicles ─────────────────────────────────────────────
    top_vehicles = Vehicle.objects.annotate(
        rental_count=Count('rental'),
        avg_rating=Avg('review__rating')
    ).order_by('-rental_count')[:5]
    if top_vehicles:
        max_count = top_vehicles[0].rental_count or 1
        for v in top_vehicles:
            v.percentage = int((v.rental_count / max_count) * 100)

    # ── Recent Users ─────────────────────────────────────────────
    recent_users = User.objects.filter(is_staff=False).order_by('-date_joined')[:8]

    # ── Pending Registration Requests ────────────────────────────
    pending_reqs = RegistrationRequest.objects.filter(approved=False).order_by('-created_at')[:8]

    context = {
        'total_vehicles':   total_vehicles,
        'total_rentals':    total_rentals,
        'active_rentals':   active_rentals,
        'upcoming_rentals': upcoming_rentals,
        'total_revenue':    total_revenue,
        'total_users':      total_users,
        'pending_requests': pending_requests,
        'recent_rentals':   recent_rentals,
        'top_vehicles':     top_vehicles,
        'recent_users':     recent_users,
        'pending_reqs':     pending_reqs,
        # JSON for charts
        'monthly_labels_json': json.dumps(monthly_labels),
        'monthly_data_json':   json.dumps(monthly_data),
        'status_data_json':    json.dumps(status_data),
    }
    
    return render(request, 'admin_dashboard.html', context)


@login_required
def support(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you could send an email or save to database
        # For now, just show success message
        messages.success(request, 'Votre message a été envoyé. Nous vous répondrons bientôt!')
        return redirect('/rentals/support/')
    
    return render(request, 'support.html')

def register(request):
    """Handle user registration with email verification for regular users."""
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
                # Create inactive user for email verification
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=False  # 👈 Account inactive until email verified
                )
                
                # Generate verification token and link
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                verification_url = request.build_absolute_uri(
                    reverse('verify_email_token', kwargs={'uidb64': uid, 'token': token})
                )
                
                # Send verification email
                try:
                    send_verification_email(user, verification_url, request)
                    return redirect(f'/rentals/email-sent/?email={email}')
                except Exception as e:
                    # If email fails, delete user and show error
                    user.delete()
                    messages.error(request, f'Erreur lors de l\'envoi de l\'email: {str(e)}')
                    return render(request, 'register.html', {'form': form})

            else:  # role == 'admin'
                # Create registration request for admin approval
                RegistrationRequest.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password),
                    role='admin'
                )
                messages.success(request, 'Demande envoyée! Attendez l\'approbation de l\'administrateur.')
                return redirect('register')
        else:
            # Form errors will be displayed in template
            return render(request, 'register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def send_verification_email(user, verification_url, request):
    """
    Send email verification link to user.
    
    Args:
        user: User object to verify
        verification_url: Full URL for verification link
        request: Current request object for building absolute URLs
    """
    subject = '🚗 AutoLux - Vérifiez votre adresse email'
    
    # Render HTML email template
    html_message = render_to_string('emails/verify_email.html', {
        'user': user,
        'verification_url': verification_url,
        'unsubscribe_url': request.build_absolute_uri('/'),  # Placeholder
        'site_name': 'AutoLux',
    })
    
    # Plain text fallback
    plain_message = f"""
Bienvenue sur AutoLux!

Veuillez vérifier votre adresse email en cliquant sur ce lien:
{verification_url}

Ce lien expire dans 24 heures.

Si vous n'avez pas créé de compte, ignorez cet email.

Cordialement,
L'équipe AutoLux
    """.strip()
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def email_sent(request):
    """
    Show confirmation page after registration email sent.
    """
    email = request.GET.get('email', '')
    
    # Check if this is a resend request
    if request.method == 'POST':
        email = request.POST.get('email', '')
        try:
            # Find user by email (should be inactive)
            user = User.objects.get(email=email, is_active=False)
            
            # Generate new token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_url = request.build_absolute_uri(
                reverse('verify_email_token', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Send verification email
            send_verification_email(user, verification_url, request)
            messages.success(request, 'Email de vérification renvoyé avec succès!')
            
        except User.DoesNotExist:
            messages.error(request, 'Aucun compte en attente de vérification avec cet email.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'envoi: {str(e)}')
    
    context = {
        'email': email,
    }
    return render(request, 'email_sent.html', context)


def verify_email_token(request, uidb64, token):
    """
    Verify email token and activate user account.
    
    Args:
        request: Current request object
        uidb64: Base64 encoded user ID
        token: Verification token
    """
    try:
        # Decode UID from base64
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        # Invalid UID
        context = {
            'error_type': 'invalid',
            'email': None,
        }
        return render(request, 'email_verification_error.html', context, status=400)

    # Check token validity
    if not default_token_generator.check_token(user, token):
        # Token expired or invalid
        context = {
            'error_type': 'expired',
            'email': user.email,
        }
        return render(request, 'email_verification_error.html', context, status=400)

    # Check if already verified
    if user.is_active:
        context = {
            'error_type': 'already_verified',
            'email': user.email,
        }
        return render(request, 'email_verification_error.html', context)

    # ✅ Activate user
    user.is_active = True
    user.save()
    
    # Auto-login user
    user = authenticate(username=user.username, password=None)
    if user is not None:
        # For auto-login without password, we manually set the session
        user = User.objects.get(pk=user.pk) if user else None
        if user:
            login(request, user)

    # Show success page
    context = {
        'user': user,
    }
    return render(request, 'email_verification_success.html', context)


def resend_verification_email(request):
    """
    Let users resend verification email if they didn't receive it.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '')
        
        if not email:
            messages.error(request, 'Veuillez entrer votre adresse email.')
            return redirect('/rentals/email-sent/')
        
        try:
            # Find inactive user with this email
            user = User.objects.get(email=email, is_active=False)
            
            # Generate new token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_url = request.build_absolute_uri(
                reverse('verify_email_token', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Send verification email
            send_verification_email(user, verification_url, request)
            messages.success(request, '✅ Email de vérification renvoyé! Vérifiez votre boîte de réception.')
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.info(request, 'Si ce compte existe et n\'est pas vérifié, un email a été envoyé.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'envoi: {str(e)}')
        
        return redirect(f'/rentals/email-sent/?email={email}')
    
    # GET request - redirect to email_sent page
    return redirect('/rentals/email-sent/')


@login_required
def profile(request):
    prof, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        if 'photo' in request.FILES:
            prof.photo = request.FILES['photo']
            prof.save()

        messages.success(request, 'Profil mis à jour avec succès!')
        return redirect('/rentals/profile/')

    # Pre-compute stats so templates don't call methods with args
    all_rentals = Rental.objects.filter(customer=request.user)
    active_count = all_rentals.filter(is_active=True).count()
    past_count   = all_rentals.filter(is_active=False).count()
    total_rentals = all_rentals.count()
    total_spent = sum(
        r.total_price for r in all_rentals.filter(is_active=False)
        if r.total_price is not None
    )

    context = {
        'profile': prof,
        'total_rentals': total_rentals,
        'active_rentals_count': active_count,
        'past_rentals_count': past_count,
        'total_spent': total_spent,
    }
    return render(request, 'profile.html', context)


@login_required
def payments(request):
    """Display payment history for the user"""
    user_rentals = Rental.objects.filter(customer=request.user).order_by('-start_date')
    context = {
        'rentals': user_rentals,
        'total_spent': sum(r.total_price for r in user_rentals if r.total_price),
    }
    return render(request, 'payments.html', context)
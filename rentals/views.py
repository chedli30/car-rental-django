from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from .models import Rental, RegistrationRequest, Profile, Review
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
    
    # Basic analytics
    total_vehicles = Vehicle.objects.count()
    total_rentals = Rental.objects.count()
    now_date = timezone.now().date()
    active_rentals = Rental.objects.filter(is_active=True).count()

    # Revenue based on completed rentals (ended date before today or explicitly ended)
    completed_rentals = Rental.objects.filter(Q(is_active=False) | Q(end_date__lt=now_date))

    total_revenue = 0
    for rental in completed_rentals:
        if rental.total_price is None:
            days = (rental.end_date - rental.start_date).days
            rental.total_price = days * rental.vehicle.price_per_day
            # Optional: do not save every time in dashboard, only calculated value
        total_revenue += rental.total_price

    # Ensure we have stable casting
    if total_revenue is None:
        total_revenue = 0
    
    # Recent rentals
    recent_rentals = Rental.objects.select_related('customer', 'vehicle').order_by('-start_date')[:10]
    
    # Top vehicles
    top_vehicles = Vehicle.objects.annotate(
        rental_count=Count('rental'),
        avg_rating=Avg('review__rating')
    ).order_by('-rental_count')[:5]
    
    # Calculate percentage for progress bars
    if top_vehicles:
        max_count = top_vehicles[0].rental_count
        for vehicle in top_vehicles:
            vehicle.percentage = int((vehicle.rental_count / max_count) * 100) if max_count > 0 else 0
    
    context = {
        'total_vehicles': total_vehicles,
        'total_rentals': total_rentals,
        'active_rentals': active_rentals,
        'total_revenue': total_revenue,
        'recent_rentals': recent_rentals,
        'top_vehicles': top_vehicles,
    }
    
    return render(request, 'admin_dashboard.html', context)

def support(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you could send an email or save to database
        # For now, just show success message
        messages.success(request, 'Votre message a été envoyé. Nous vous répondrons bientôt!')
        return redirect('/support/')
    
    return render(request, 'support.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'user')
        
        if role not in ['user', 'admin']:
            messages.error(request, 'Rôle invalide.')
            return render(request, 'register.html')

        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas!')
            return render(request, 'register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà!')
            return render(request, 'register.html')
        if RegistrationRequest.objects.filter(username=username).exists():
            messages.error(request, 'Une demande existe déjà pour ce nom!')
            return render(request, 'register.html')

        if role == 'user':
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            return redirect('/vehicles/')
        else:
            RegistrationRequest.objects.create(
                username=username,
                email=email,
                password=make_password(password1),
                role='admin'
            )
            messages.success(request, 'Demande envoyée! Attendez l\'approbation de l\'admin.')
            return render(request, 'register.html')

    return render(request, 'register.html')

@login_required
def profile(request):
    prof, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update user info
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Update profile photo
        if 'photo' in request.FILES:
            prof.photo = request.FILES['photo']
            prof.save()
        
        messages.success(request, 'Profil mis à jour avec succès!')
        return redirect('/rentals/profile/')
    
    return render(request, 'profile.html', {'profile': prof})
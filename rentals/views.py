from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Rental, RegistrationRequest, Profile
from vehicles.models import Vehicle

@login_required
def book_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        Rental.objects.create(
            customer=request.user,
            vehicle=vehicle,
            start_date=start_date,
            end_date=end_date
        )
        vehicle.available = False
        vehicle.save()
        return redirect('/rentals/history/')
    return render(request, 'rental_form.html', {'vehicle': vehicle})

@login_required
def rental_history(request):
    rentals = Rental.objects.filter(customer=request.user)
    return render(request, 'rental_history.html', {'rentals': rentals})

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role = request.POST['role']

        if password1 != password2:
            return render(request, 'register.html', {'error': 'Les mots de passe ne correspondent pas!'})
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Ce nom d\'utilisateur existe déjà!'})
        if RegistrationRequest.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Une demande existe déjà pour ce nom!'})

        if role == 'user':
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            return redirect('/vehicles/')
        else:
            RegistrationRequest.objects.create(
                username=username,
                email=email,
                password=password1,
                role='admin'
            )
            return render(request, 'register.html', {'success': 'Demande envoyée! Attendez l\'approbation de l\'admin.'})

    return render(request, 'register.html')

@login_required
def profile(request):
    prof, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        if 'photo' in request.FILES:
            prof.photo = request.FILES['photo']
            prof.save()
        return redirect('/rentals/profile/')
    return render(request, 'profile.html', {'profile': prof})
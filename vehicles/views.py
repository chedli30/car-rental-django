from django.shortcuts import render, redirect
from .models import Vehicle

def vehicle_list(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if request.user.is_staff:
        return redirect('/admin/')
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicles.html', {'vehicles': vehicles})
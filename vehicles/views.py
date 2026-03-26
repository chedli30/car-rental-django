from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Vehicle
from datetime import datetime

def vehicle_list(request):
    if not request.user.is_authenticated:
        # Show home page for non-authenticated users
        return render(request, 'home.html')
    if request.user.is_staff:
        return redirect('/rentals/admin-dashboard/')

    # Get all vehicles
    vehicles = Vehicle.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        vehicles = vehicles.filter(
            Q(brand__icontains=search_query) |
            Q(model__icontains=search_query)
        )

    # Price filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            vehicles = vehicles.filter(price_per_day__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            vehicles = vehicles.filter(price_per_day__lte=float(max_price))
        except ValueError:
            pass

    # Availability filtering
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    available_only = request.GET.get('available_only')

    if available_only and start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            if start_date < end_date:
                # Filter vehicles that are available for these dates
                available_vehicles = []
                for vehicle in vehicles:
                    if vehicle.is_available_for_dates(start_date, end_date):
                        available_vehicles.append(vehicle.id)
                vehicles = vehicles.filter(id__in=available_vehicles)
        except ValueError:
            pass

    # Sorting
    sort_by = request.GET.get('sort', 'price_per_day')
    if sort_by == 'price_asc':
        vehicles = vehicles.order_by('price_per_day')
    elif sort_by == 'price_desc':
        vehicles = vehicles.order_by('-price_per_day')
    elif sort_by == 'brand':
        vehicles = vehicles.order_by('brand', 'model')
    else:
        vehicles = vehicles.order_by('price_per_day')

    # Pagination
    paginator = Paginator(vehicles, 9)  # 9 vehicles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'available_only': available_only,
        'sort_by': sort_by,
    }

    return render(request, 'vehicles.html', context)
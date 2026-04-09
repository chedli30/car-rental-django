from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from .models import Vehicle
from datetime import datetime
from django.contrib.auth.decorators import login_required


def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    from rentals.models import Review
    reviews = Review.objects.filter(vehicle=vehicle).select_related('customer').order_by('-created_at')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    
    # Check availability for requested dates
    start_date_str = request.GET.get('start_date', '')
    end_date_str   = request.GET.get('end_date', '')
    is_available   = None
    if start_date_str and end_date_str:
        try:
            sd = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            ed = datetime.strptime(end_date_str,   '%Y-%m-%d').date()
            if sd < ed:
                is_available = vehicle.is_available_for_dates(sd, ed)
        except ValueError:
            pass

    context = {
        'vehicle':        vehicle,
        'reviews':        reviews,
        'avg_rating':     round(avg_rating, 1) if avg_rating else None,
        'review_count':   reviews.count(),
        'is_available':   is_available,
        'start_date':     start_date_str,
        'end_date':       end_date_str,
    }
    return render(request, 'vehicle_detail.html', context)


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
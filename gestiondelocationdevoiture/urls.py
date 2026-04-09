from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView, TemplateView
from vehicles.views import vehicle_list
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_url = '/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', vehicle_list, name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('vehicles/', include('vehicles.urls')),
    path('rentals/', include('rentals.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    # Convenience redirects so /support/ and /register/ don't 404
    path('support/', RedirectView.as_view(url='/rentals/support/', permanent=False)),
    path('register/', RedirectView.as_view(url='/rentals/register/', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
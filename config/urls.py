from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from reservations import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # --- Administrative Portal ---
    # We use 'dashboard/' to access our Tailwind-styled Unfold Admin
    path('dashboard/', admin.site.urls),
    path('login-success/', views.login_success, name='login_success'),

    # --- Public Customer Views ---
    path('', views.index, name='index'),
    path('check-booking/', views.check_booking, name='check_booking'),
    
    # --- Booking Flow ---
    path('book/<int:service_id>/', views.book_service, name='book_service'),
    path('cancel-booking/<int:appointment_id>/', views.cancel_booking, name='cancel_booking'),
    
    # --- API Endpoints (AJAX) ---
    path('api/available-slots/', views.get_available_slots, name='get_available_slots'),

    # --- Staff & User Account Management ---
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

    path('staff/jobs/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/update-status/<int:appointment_id>/<str:new_status>/', views.update_job_status, name='update_job_status'),

    path('locator/', views.locator, name='locator'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
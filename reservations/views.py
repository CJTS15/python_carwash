from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from .models import Service, Appointment, AddOn
import datetime

def index(request):
    # If a staff member (but not admin) accidentally lands on the home page
    if request.user.is_authenticated and request.user.is_staff and not request.user.is_superuser:
        return redirect('staff_dashboard')
    
    services = Service.objects.all()
    return render(request, 'reservations/index.html', {'services': services})

def book_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    add_ons = AddOn.objects.all()
    
    # AJAX now handles the available_slots, so we don't need the GET logic here anymore
    # but we keep the variables to avoid template errors
    selected_date_str = request.GET.get('date')
    available_slots = []

    if request.method == 'POST':
        try:
            # 1. Capture Form Data
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            plate = request.POST.get('plate')
            model = request.POST.get('model')
            date_val = request.POST.get('date')  # String: "2023-12-25"
            time_val = request.POST.get('time')  # String: "08:00:00"
            selected_addons = request.POST.getlist('add_ons')

            # --- CRITICAL FIX: Convert Strings to Python Objects ---
            # This prevents the 'TypeError' in your model's clean() method
            final_date = datetime.datetime.strptime(date_val, '%Y-%m-%d').date()
            final_time = datetime.datetime.strptime(time_val, '%H:%M:%S').time()

            # 2. Create the Appointment object (but don't save to DB yet)
            appointment = Appointment(
                customer_name=name,
                customer_phone=phone,
                customer_address=address,
                car_plate=plate,
                car_model=model,
                service=service,
                date=final_date, # Use object
                time_slot=final_time, # Use object
                user=request.user if request.user.is_authenticated else None 
            )
            
            # 3. Trigger validation and save
            appointment.full_clean() 
            appointment.save()

            if selected_addons:
                appointment.add_ons.set(selected_addons)

            messages.success(request, f"Thank you, {name}! Your booking is received.")
            return redirect('index')
            
        except Exception as e:
            # Print to terminal so you can see exactly what went wrong
            print(f"DEBUG ERROR: {e}") 
            messages.error(request, f"Booking Error: {e}")

    return render(request, 'reservations/booking_form.html', {
        'service': service, 
        'add_ons': add_ons, 
        'available_slots': available_slots, 
        'selected_date': selected_date_str
    })

@login_required
def cancel_booking(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    if appointment.can_cancel:
        # Fixed typo: 'cancelled' -> 'canceled' (must match models.py choices)
        appointment.status = 'canceled' 
        appointment.save()
        messages.success(request, f"Your booking for {appointment.service.name} has been canceled.")
    else:
        messages.error(request, "This booking cannot be canceled as it is too close to the appointment time.")
        
    return redirect('my_bookings')

@login_required
def my_bookings(request):
    bookings = Appointment.objects.filter(user=request.user).order_by('-date', '-time_slot')
    return render(request, 'reservations/my_bookings.html', {'bookings': bookings})

def check_booking(request):
    query = request.GET.get('plate')
    results = []
    if query:
        results = Appointment.objects.filter(car_plate__iexact=query).order_by('-date')
    return render(request, 'reservations/check_booking.html', {'results': results, 'query': query})

def get_available_slots(request):
    date_str = request.GET.get('date')
    service_id = request.GET.get('service_id')
    
    if not date_str:
        return JsonResponse({'slots': []})

    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        # Find taken slots
        booked = Appointment.objects.filter(
            date=date_obj, 
            status__in=['pending', 'confirmed']
        ).values_list('time_slot', flat=True)
        
        # Format the available slots for the frontend
        available = []
        for val, label in Appointment.TIME_CHOICES:
            if val not in booked:
                # We format the value so JS can read it easily
                available.append({
                    'value': val.strftime('%H:%M:%S'),
                    'label': label
                })
        return JsonResponse({'slots': available})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@staff_member_required
def staff_dashboard(request):
    my_jobs = Appointment.objects.filter(
        assigned_staff=request.user
    ).exclude(status__in=['canceled'])
    
    # Calculate Total Commission for Today
    total_earned_today = sum(job.commission_earned for job in my_jobs if job.status == 'completed')
    
    return render(request, 'reservations/staff_dashboard.html', {
        'jobs': my_jobs,
        'total_earned_today': total_earned_today
    })

@staff_member_required
def update_job_status(request, appointment_id, new_status):
    appointment = get_object_or_404(Appointment, id=appointment_id, assigned_staff=request.user)
    
    if new_status == 'completed':
        # Get the price entered by the staff from the form
        price_paid = request.POST.get('final_price', 0)
        appointment.final_price = price_paid
        appointment.status = 'completed'
        appointment.save() # This triggers our calculate_commission logic
        messages.success(request, f"Job done! You earned ₱{appointment.commission_earned:,.2f}")
    elif new_status == 'progress':
        appointment.status = 'progress'
        appointment.save()

    return redirect('staff_dashboard')

@login_required
def login_success(request):
    """
    Redirects users to the appropriate dashboard based on their role 
    immediately after logging in.
    """
    if request.user.is_superuser:
        # The Boss goes to the Admin Panel
        return redirect('/dashboard/')
    elif request.user.is_staff:
        # The Washer goes to their Job List
        return redirect('staff_dashboard')
    else:
        # Normal customers (if any) go to the home page
        return redirect('index')
    
def locator(request):
    return render(request, 'reservations/locator.html')
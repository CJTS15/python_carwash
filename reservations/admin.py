from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Service, Appointment, AddOn

# --- Customizing the Admin Interface ---
admin.site.site_header = "Velez Carwash Admin Portal"
admin.site.site_title = "Velez Carwash | Management" 
admin.site.index_title = "Welcome to the Velez Carwash Dashboard"
# ----------------------------------------

@admin.register(Service)
class ServiceAdmin(ModelAdmin): # Using Unfold ModelAdmin
    list_display = ('name', 'min_price', 'max_price', 'duration_minutes')
    search_fields = ('name',)

@admin.register(AddOn)
class AddOnAdmin(ModelAdmin):
    list_display = ('name', 'price')

@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    # We remove 'user' and replace it with a custom 'booked_by' method
    list_display = ('customer_name', 'assigned_staff', 'final_price', 'commission_earned', 'status')
    # Use 'list_editable' so the Boss can correct prices quickly if the washer makes a mistake
    list_editable = ('status', 'final_price')
    
    def booked_by(self, obj):
        if obj.user:
            return obj.user.username
        return "Guest" # Shows 'Guest' instead of blank or admin
    
    booked_by.short_description = 'Account'

    
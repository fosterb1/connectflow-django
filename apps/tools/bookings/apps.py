from django.apps import AppConfig

class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tools.bookings'
    label = 'tools_bookings'
    verbose_name = 'Resource Booking'

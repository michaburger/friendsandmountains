from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import GeneralEventInfo, Event, GalleryImage, EventProgram, AccommodationImage, SurroundingsImage, Registration, Coupon
from import_export import resources, fields
from import_export.admin import ExportMixin
from import_export.formats import base_formats

# Define a resource class for the Registration model
class RegistrationResource(resources.ModelResource):
    event_title = fields.Field(column_name='Event', attribute='event__title')
    country_name = fields.Field(column_name='Country', attribute='country__name')
    registered_date = fields.Field(column_name='Registration Date', attribute='registered_at')
    friend_info = fields.Field(column_name='Bringing Friend', attribute='bring_a_friend')
    friend = fields.Field(column_name="Friend's Name", attribute='friend_name')
    coupon_info = fields.Field(column_name='Coupon Used', attribute='coupon__code')
    
    class Meta:
        model = Registration
        fields = ('id', 'first_name', 'last_name', 'email', 'phone', 
                 'address', 'country_name', 'friend_info', 'friend',
                 'special_diets', 'potluck', 'activity_idea', 'other_comments', 
                 'coupon_info', 'original_price', 'final_price',
                 'registered_date', 'payment_status', 'event_title')
        export_order = fields

# Inline models for displaying related models inside Event
class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1

class EventProgramInline(admin.TabularInline):
    model = EventProgram
    extra = 1

class AccommodationImageInline(admin.TabularInline):
    model = AccommodationImage
    extra = 1

class SurroundingsImageInline(admin.TabularInline):
    model = SurroundingsImage
    extra = 1

# Event admin with inline images
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'town_name', 'registration_state')
    list_filter = ('registration_state', 'start_date')
    search_fields = ('title', 'town_name', 'house_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    inlines = [
        GalleryImageInline,
        EventProgramInline,
        AccommodationImageInline,
        SurroundingsImageInline,
    ]

# Registration admin with export functionality
@admin.register(Registration)
class RegistrationAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = RegistrationResource
    list_display = ('first_name', 'last_name', 'email', 'event', 'registered_at', 'payment_status', 'bring_a_friend')
    list_filter = ('event', 'payment_status', 'registered_at', 'bring_a_friend')
    search_fields = ('first_name', 'last_name', 'email', 'friend_name', 'coupon_code')
    date_hierarchy = 'registered_at'
    
    # Specify which export formats to offer
    formats = [base_formats.XLSX, base_formats.CSV]
    
    # Add custom action for exporting selected registrations
    actions = ['export_selected_as_xlsx']
    
    def export_selected_as_xlsx(self, request, queryset):
        """Export selected registrations as Excel"""
        dataset = self.resource_class().export(queryset)
        response = HttpResponse(
            dataset.xlsx,  #pylint: disable=no-member
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="registrations.xlsx"'
        return response
    
    export_selected_as_xlsx.short_description = "Export selected registrations as Excel"
    
    # Fields to display in detail view
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'country')
        }),
        ('Friend Information', {
            'fields': ('bring_a_friend', 'friend_name'),
            'classes': ('collapse',),
        }),
        ('Event Preferences', {
            'fields': ('special_diets', 'potluck', 'activity_idea', 'other_comments')
        }),
        ('Agreements', {
            'fields': ('checkbox1', 'checkbox2', 'checkbox3', 'checkbox4', 'checkbox5')
        }),
        ('Pricing', {
            'fields': ('original_price', 'coupon', 'coupon_code', 'final_price'),
        }),
        ('Status', {
            'fields': ('payment_status', 'stripe_payment_intent_id', 'registered_at')
        }),
    )
    readonly_fields = ('registered_at', 'original_price', 'final_price')

# Add Coupon admin
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'expiry_date', 'is_active', 'is_valid')
    list_filter = ('is_active', 'expiry_date')
    search_fields = ('code', 'description')
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = "Valid"

# Register models with custom admin classes
admin.site.register(Event, EventAdmin)
admin.site.register(GeneralEventInfo)

# Optional: Create admin site groups
class FriendsAndMountainsAdminSite(admin.AdminSite):
    site_header = 'Friends & Mountains Admin'
    site_title = 'Friends & Mountains Admin Portal'
    index_title = 'Welcome to Friends & Mountains Admin Portal'

admin_site = FriendsAndMountainsAdminSite(name='fnm_admin')

# Register models with the custom admin site
admin_site.register(Event, EventAdmin)
admin_site.register(Registration, RegistrationAdmin)
admin_site.register(GeneralEventInfo)
admin_site.register(Coupon)

# Note: If using the custom admin site, you'll need to update urls.py
# from django.urls import path
# from web.admin import admin_site
# urlpatterns = [
#     path('admin/', admin_site.urls),
#     # other URL patterns...
# ]

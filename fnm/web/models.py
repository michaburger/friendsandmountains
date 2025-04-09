from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

# Create your models here.

class GeneralEventInfo(models.Model):
    """Model to store general event information displayed for every event"""
    general_description = models.TextField(help_text="Enter in markdown format", blank=True)
    food_description = models.TextField(help_text="Enter in markdown format", blank=True)
    registration_description = models.TextField(help_text="Enter in markdown format", blank=True)

    def save(self, *args, **kwargs):
        # Clear any existing entries if this is a new instance
        if not self.pk:
            GeneralEventInfo.objects.all().delete()  # pylint: disable=no-member
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Return the singleton instance, create it if it doesn't exist yet"""
        obj, _ = cls.objects.get_or_create(pk=1)  # pylint: disable=no-member
        return obj
    
    def __str__(self):
        return "General Event Information"
    
    class Meta:
        verbose_name = "General Event Information"
        verbose_name_plural = "General Event Information"

class Event(models.Model):
    """Model to store event information"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    couchsurfing_link = models.URLField(blank=True, help_text="Link to couchsurfing event")
    main_image = models.ImageField(upload_to='events/images/')
    event_story = models.TextField(help_text="Enter in markdown format", blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    town_name = models.CharField(max_length=200)
    house_name = models.CharField(max_length=200)
    location_desc = models.TextField(help_text="Enter in markdown format")
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    googlemaps_embed = models.TextField(blank=True, help_text="Google Maps embed code")
    how_to_get_there = models.TextField(help_text="Enter in markdown format", blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fee_desc = models.TextField(help_text="Enter in markdown format", blank=True)
    house_desc = models.TextField(help_text="Enter in markdown format", blank=True)
    registration_state = models.CharField(
        max_length=30, 
        choices=[
            ('soon', 'Registrations opening soon'),
            ('open', 'Registrations are open'),
            ('closed', 'Registrations closed'),
        ],
        default='soon',
        help_text="Current state of event registration"
    )
    activity_ideas = models.TextField(help_text="Enter in markdown format", blank=True)
    organizers = models.TextField(help_text="Enter in markdown format", blank=True)

    def __str__(self):
        return f"{self.title}"
    
class Coupon(models.Model):
    """Model for discount coupons"""
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, help_text="Internal notes about this coupon")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount to discount in CHF")
    expiry_date = models.DateField(help_text="Coupon expires at the end of this day")
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        """Check if coupon is still valid"""
        return self.is_active and self.expiry_date >= timezone.now().date()

    def __str__(self):
        return f"{self.code} - {self.discount_amount} CHF"

class Registration(models.Model):
    event = models.ForeignKey(Event, related_name='registrations', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, help_text="This will be public to other participants")
    last_name = models.CharField(max_length=200, help_text="This won't be shared on the website")
    email = models.EmailField(help_text="I will send you event related information to your email, make sure it works")
    address = models.TextField(max_length=200)
    country = CountryField()
    phone = PhoneNumberField(
        help_text="I might use this to call you for any question or organisational things. There will be a Signal group for the event for which you can sign up if you want, you will receive the link as an email.",
        region="CH"  # Default region, but will accept international formats
    )
    bring_a_friend = models.BooleanField(
        default=False,
        help_text="If you want to sign up together with a friend. It is recommended however that your friend fills the registration for themselves as well to get all relevant information."
    )
    friend_name = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Name of your friend if you're bringing someone"
    )
    special_diets = models.TextField(max_length=200, blank=True, help_text="Dietary restrictions or allergies we should know about")
    checkbox1 = models.BooleanField(default=False, verbose_name="I have read the entire event description and I agree to the format")
    checkbox2 = models.BooleanField(default=False, verbose_name="I am ready to help out with cooking, keeping the house clean, and other tasks")
    checkbox3 = models.BooleanField(default=False, verbose_name="I agree to be respectful and inclusive to all other participants")
    checkbox4 = models.BooleanField(default=False, verbose_name="I notice that some pictures of the event might be published on this website after the event and I will talk to the organizers if I don't agree")
    checkbox5 = models.BooleanField(default=False, verbose_name="I have understood that I have to forward all relevant information to the friend I signed up together with me")
    coupon = models.ForeignKey(
        Coupon, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="registrations"
    )
    coupon_code = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Enter a discount code if you have one"
    )
    potluck = models.TextField(max_length=200, help_text="What do you plan to bring for the Potluck / International Dinner?")
    activity_idea = models.TextField(max_length=200, blank=True, help_text="Do you have an activity idea that you would like to suggest for other participants that we should keep some time in the program for?")
    other_comments = models.TextField(max_length=500, blank=True, help_text="Any other comments or questions?")
    registered_at = models.DateTimeField(auto_now_add=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        # Set the original price based on the event's fee
        if self.event and self.event.fee and not self.original_price:  #pylint: disable=no-member
            self.original_price = self.event.fee  #pylint: disable=no-member
            self.final_price = self.event.fee  #pylint: disable=no-member
        
        # Apply coupon if provided and valid
        if self.coupon_code and not self.coupon:
            try:
                coupon = Coupon.objects.get(code=self.coupon_code, is_active=True)  #pylint: disable=no-member
                if coupon.is_valid():
                    self.coupon = coupon
                    if self.original_price:
                        self.final_price = max(0, self.original_price - coupon.discount_amount)
            except Coupon.DoesNotExist:  #pylint: disable=no-member
                # Invalid coupon code, ignore it
                pass
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.event.title}"  #pylint: disable=no-member

class GalleryImage(models.Model):
    """Model to store images related to an event"""
    event = models.ForeignKey(Event, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='events/images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.event.title if self.event else 'Event'} - {self.caption}"  #pylint: disable=no-member
    
    class Meta:
        ordering = ['order']

class EventProgram(models.Model):
    """Model to store the day-by-day program of an event"""
    event = models.ForeignKey(Event, related_name='program_days', on_delete=models.CASCADE)
    date = models.DateField()
    day_activity = models.TextField(help_text="Enter in markdown format", blank=True)
    evening_activity = models.TextField(help_text="Enter in markdown format", blank=True)

    def __str__(self):
        return f"{self.event.title if self.event else 'Event'} - {self.date}"  #pylint: disable=no-member
    class Meta:
        ordering = ['date']

class AccommodationImage(models.Model):
    """Model to store accommodation images related to an event"""
    event = models.ForeignKey(Event, related_name='accommodation_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='events/accommodations/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.event.title if self.event else 'Event'} - Accommodation - {self.caption}"  #pylint: disable=no-member

    class Meta:
        ordering = ['order']
        verbose_name = "Accommodation Image"
        verbose_name_plural = "Accommodation Images"

class SurroundingsImage(models.Model):
    """Model to store surroundings/location images related to an event"""
    event = models.ForeignKey(Event, related_name='surroundings_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='events/surroundings/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.event.title if self.event else 'Event'} - Surroundings - {self.caption}"  #pylint: disable=no-member

    class Meta:
        ordering = ['order']
        verbose_name = "Surroundings Image" 
        verbose_name_plural = "Surroundings Images"

from django.db import models
from django_countries.fields import CountryField

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
    registration_form = models.URLField(blank=True)
    registration_state = models.CharField(max_length=200, blank=True, help_text="State of the registration form")
    activity_ideas = models.TextField(help_text="Enter in markdown format", blank=True)
    organizers = models.TextField(help_text="Enter in markdown format", blank=True)

    def __str__(self):
        return f"{self.title}"
    
class Registration(models.Model):
    event = models.ForeignKey(Event, related_name='registrations', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.TextField(max_length=200)
    country = CountryField()
    phone = models.CharField(max_length=20)
    special_diets = models.TextField(max_length=200, blank=True, help_text="Dietary restrictions or allergies we should know about")
    checkbox1 = models.BooleanField(default=False, help_text="I have read the entire event description and I agree to the format")
    checkbox2 = models.BooleanField(default=False, help_text="I am ready to help out with cooking, keeping the house clean, and other tasks")
    checkbox3 = models.BooleanField(default=False, help_text="I agree to be respectful and inclusive to all other participants")
    checkbox4 = models.BooleanField(default=False, help_text="I notice that some pictures of the event might be published on this website after the event and I will talk to the organizers if I don't agree")
    potluck = models.TextField(max_length=200, help_text="What do you plan to bring for the Potluck / International Dinner?")
    activity_idea = models.TextField(max_length=200, blank=True, help_text="Do you have an activity idea that you would like to suggest for other participants that we should keep some time in the program for?")
    other_comments = models.TextField(max_length=500, blank=True, help_text="Any other comments or questions?")
    registered_at = models.DateTimeField(auto_now_add=True)
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

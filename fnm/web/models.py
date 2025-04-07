from django.db import models

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
    event_story = models.TextField(help_text="Enter in markdown format")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    town = models.CharField(max_length=200, blank=True)
    location_name = models.CharField(max_length=200)
    location_desc = models.TextField(help_text="Enter in markdown format")
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    googlemaps_embed = models.TextField(blank=True, help_text="Google Maps embed code")
    how_to_get_there = models.TextField(help_text="Enter in markdown format", blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fee_desc = models.TextField(help_text="Enter in markdown format", blank=True)
    house_desc = models.TextField(help_text="Enter in markdown format", blank=True)
    registration_form = models.URLField(blank=True)
    activity_ideas = models.TextField(help_text="Enter in markdown format", blank=True)
    organizers = models.TextField(help_text="Enter in markdown format", blank=True)

    def __str__(self):
        return f"{self.title}"

class GalleryImage(models.Model):
    """Model to store images related to an event"""
    event = models.ForeignKey(Event, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='events/images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.event.title if self.event else "Event"} - {self.caption}"  #pylint: disable=no-member
    
    class Meta:
        ordering = ['order']

class EventProgram(models.Model):
    """Model to store the day-by-day program of an event"""
    event = models.ForeignKey(Event, related_name='program_days', on_delete=models.CASCADE)
    date = models.DateField()
    day_activity = models.TextField(help_text="Enter in markdown format", blank=True)
    evening_activity = models.TextField(help_text="Enter in markdown format", blank=True)

    def __str__(self):
        return f"{self.event.title if self.event else "Event"} - {self.date}"  #pylint: disable=no-member
    class Meta:
        ordering = ['date']

from django.contrib import admin
from .models import GeneralEventInfo, Event, GalleryImage, EventProgram, AccommodationImage, SurroundingsImage

# Register your models here.

admin.site.register(GeneralEventInfo)
admin.site.register(Event)
admin.site.register(GalleryImage)
admin.site.register(AccommodationImage)
admin.site.register(SurroundingsImage)
admin.site.register(EventProgram)

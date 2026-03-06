from django.db import models
from api.options import EventStatus
from api.models.utils import event_image_upload_path
from PIL import Image
import os
from fightoracle_api import settings


class Event(models.Model):
    # UFCStats tracking
    ufcstats_event_id = models.CharField(
        max_length=50, unique=True, db_index=True, null=True, blank=True,
        help_text="UFCStats.com event ID for tracking source data"
    )
    
    name = models.CharField(max_length=255)
    promotion = models.ForeignKey("api.Promotion", on_delete=models.PROTECT)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    venue = models.CharField(max_length=255)
    status = models.CharField(
        max_length=255, choices=EventStatus.choices, default=EventStatus.SCHEDULED
    )
    date = models.DateTimeField()
    banner_image = models.ImageField(
        upload_to=event_image_upload_path, null=True, blank=True
    )

    def __str__(self):
        return f"id: {self.id},promotion: {self.promotion}, name: {self.name}, date: {self.date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.banner_image:
            image_path = os.path.join(settings.MEDIA_ROOT, self.banner_image.name)
            img = Image.open(image_path)

            max_size = (512, 512)
            img.thumbnail(max_size)
            img.save(image_path)

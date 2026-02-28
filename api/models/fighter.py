from django.db import models
from django_countries.fields import CountryField
from api.options import WeightClass
from django.conf import settings as django_conf_settings
from fightoracle_api import settings
from PIL import Image
from api.models.utils import sanitize_filename

import os


def fighter_image_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    new_filename = f"{instance.fname}_{instance.sname}.{extension}"
    safe_filename = sanitize_filename(new_filename)
    return f"fighters/{instance.id}/{safe_filename}"


class Fighter(models.Model):
    # UFCStats tracking
    ufcstats_fighter_id = models.CharField(
        max_length=50, unique=True, db_index=True, null=True, blank=True,
        help_text="UFCStats.com fighter ID for tracking source data"
    )
    
    # Basic info
    fname = models.CharField(max_length=255)
    sname = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    promotion = models.ForeignKey("api.Promotion", on_delete=models.PROTECT)
    weight_class = models.CharField(max_length=255, choices=WeightClass.choices)
    dob = models.DateField()
    stance = models.CharField(max_length=50, blank=True, null=True)
    
    # Physical attributes
    height = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    reach = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    country = CountryField(
        blank=True, null=True, countries=django_conf_settings.COUNTRIES
    )
    
    # Record
    wins = models.PositiveSmallIntegerField(default=0)
    losses = models.PositiveSmallIntegerField(default=0)
    draws = models.PositiveSmallIntegerField(default=0)
    no_contests = models.PositiveSmallIntegerField(default=0)
    dqs = models.PositiveSmallIntegerField(default=0)
    
    # Career statistics
    slpm = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        help_text="Significant Strikes Landed per Minute"
    )
    str_acc = models.PositiveSmallIntegerField(
        blank=True, null=True,
        help_text="Striking Accuracy %"
    )
    sapm = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        help_text="Significant Strikes Absorbed per Minute"
    )
    str_def = models.PositiveSmallIntegerField(
        blank=True, null=True,
        help_text="Strike Defense %"
    )
    td_avg = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        help_text="Takedown Average per 15min"
    )
    td_acc = models.PositiveSmallIntegerField(
        blank=True, null=True,
        help_text="Takedown Accuracy %"
    )
    td_def = models.PositiveSmallIntegerField(
        blank=True, null=True,
        help_text="Takedown Defense %"
    )
    sub_avg = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        help_text="Submission Average per 15min"
    )
    
    # Media
    avatar = models.ImageField(
        upload_to=fighter_image_upload_path, null=True, blank=True
    )

    @property
    def name(self):
        return f"{self.fname} {self.sname}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.avatar:
            image_path = os.path.join(settings.MEDIA_ROOT, self.avatar.name)
            img = Image.open(image_path)

            # Resize image to max 512x512 for fighters
            max_size = (512, 512)
            img.thumbnail(max_size)
            img.save(image_path)

    def __str__(self):
        return f"id: {self.id}, name: {self.fname} {self.sname}"


def get_record_object(fighter):
    return {
        "wins": fighter.wins,
        "losses": fighter.losses,
        "draws": fighter.draws,
        "no_contests": fighter.no_contests,
        "dqs": fighter.dqs,
    }

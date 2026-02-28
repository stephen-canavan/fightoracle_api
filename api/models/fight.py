from django.db import models
from api.options import FightStatus, WeightClass, Method, CardTier
from api.models.fighter import get_record_object


class Fight(models.Model):
    # UFCStats tracking
    ufcstats_fight_id = models.CharField(
        max_length=50, unique=True, db_index=True, null=True, blank=True,
        help_text="UFCStats.com fight ID for tracking source data"
    )
    
    # Relationships
    event = models.ForeignKey("api.Event", on_delete=models.PROTECT)
    fighter_red = models.ForeignKey(
        "api.Fighter", related_name="red_corner", on_delete=models.PROTECT
    )
    fighter_blue = models.ForeignKey(
        "api.Fighter", related_name="blue_corner", on_delete=models.PROTECT
    )
    fighter_red_record = models.JSONField(max_length=50, blank=True, null=True)
    fighter_blue_record = models.JSONField(max_length=50, blank=True, null=True)
    
    # Fight details
    weight_class = models.CharField(max_length=255, choices=WeightClass.choices)
    scheduled_rounds = models.PositiveSmallIntegerField(default=3)
    is_title_fight = models.BooleanField(default=False)
    is_main_event = models.BooleanField(default=False)
    card_position = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Fight order on card (1=main event, 2=co-main, etc.)"
    )
    card_tier = models.CharField(
        max_length=255, choices=CardTier.choices, default=CardTier.MAIN_CARD
    )
    status = models.CharField(
        max_length=255, choices=FightStatus.choices, default=FightStatus.SCHEDULED
    )

    # Result
    winner = models.ForeignKey(
        "api.Fighter", blank=True, null=True, on_delete=models.PROTECT
    )
    winning_method = models.CharField(
        max_length=255, choices=Method.choices, blank=True, null=True
    )
    winning_round = models.IntegerField(blank=True, null=True)
    
    # UFCStats additional data
    method_details = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Detailed method description (e.g., 'Punches to Head')"
    )
    fight_time = models.CharField(
        max_length=10, blank=True, null=True,
        help_text="Time of finish (e.g., '2:23')"
    )
    referee = models.CharField(max_length=255, blank=True, null=True)
    
    # Comprehensive fight statistics
    fighter_red_stats = models.JSONField(
        blank=True, null=True,
        help_text="Complete statistics for red corner fighter"
    )
    fighter_blue_stats = models.JSONField(
        blank=True, null=True,
        help_text="Complete statistics for blue corner fighter"
    )

    def __str__(self):
        return f"{self.fighter_red.name} vs {self.fighter_blue.name}"

    @property
    def get_fighter_red_with_record(self):
        # Provide the nested data dynamically
        self.fighter_red.fighter_record = self.fighter_red_record
        return self.fighter_red

    @property
    def get_fighter_blue_with_record(self):
        self.fighter_blue.fighter_record = self.fighter_blue_record
        return self.fighter_blue

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            if self.fighter_red and self.fighter_red_record is None:
                self.fighter_red_record = get_record_object(self.fighter_red)

            if self.fighter_blue and self.fighter_blue_record is None:
                self.fighter_blue_record = get_record_object(self.fighter_blue)

        super().save(*args, **kwargs)

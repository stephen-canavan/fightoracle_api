from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import Promotion, Event, Fight, Fighter, Prediction, User, UserStats
from api.services.events import complete_event
from api.forms import CustomUserCreationForm, CustomUserChangeForm

admin.site.register(Promotion)
admin.site.register(UserStats)
admin.site.register(Prediction)


@admin.register(Fight)
class FightAdmin(admin.ModelAdmin):
    list_display = ("id", "matchup", "event", "card_position", "winning_method", "status")
    search_fields = ("fighter_red__fname", "fighter_red__sname", "fighter_blue__fname", "fighter_blue__sname", "event__name")
    list_filter = ("status", "card_tier", "is_title_fight", "weight_class", "winning_method")
    
    def matchup(self, obj):
        return f"{obj.fighter_red.name} vs {obj.fighter_blue.name}"
    
    matchup.short_description = "Matchup"


@admin.action(description="Complete selected events")
def complete_selected_events(modeladmin, request, queryset):
    for event in queryset:
        complete_event(event.id)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "date", "status")
    search_fields = ("name", "city", "country", "venue")
    list_filter = ("status", "promotion")
    actions = [complete_selected_events]
    fields = ("name", "promotion", "country", "city", "venue", "status", "date", "banner_image")


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    # Fields shown when CREATING a user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "avatar",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # Fields shown when EDITING a user
    fieldsets = UserAdmin.fieldsets + (("Profile", {"fields": ["avatar"]}),)


@admin.register(Fighter)
class FighterAdmin(admin.ModelAdmin):
    list_display = ("name", "weight_class", "country", "country_flag", "record_display")
    search_fields = ("fname", "sname", "nickname", "ufcstats_fighter_id")
    list_filter = ("weight_class", "promotion", "country")

    def record_display(self, obj):
        return f"{obj.wins}-{obj.losses}-{obj.draws}"
    
    record_display.short_description = "Record"

    def country_flag(self, obj):
        if obj.country:
            return format_html('<img src="{}" width="20" />', obj.country.flag)
        return "-"

    country_flag.short_description = "Flag"

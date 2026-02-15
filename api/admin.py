from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import Promotion, Event, Fight, Fighter, Prediction, User, UserStats
from api.services.events import complete_event
from api.forms import CustomUserCreationForm, CustomUserChangeForm

admin.site.register(Promotion)
admin.site.register(Fight)

admin.site.register(UserStats)
admin.site.register(Prediction)


@admin.action(description="Complete selected events")
def complete_selected_events(modeladmin, request, queryset):
    for event in queryset:
        complete_event(event.id)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status")
    actions = [complete_selected_events]


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
    list_display = ("name", "country", "country_flag")

    def country_flag(self, obj):
        if obj.country:
            return format_html('<img src="{}" width="20" />', obj.country.flag)
        return "-"

    country_flag.short_description = "Flag"

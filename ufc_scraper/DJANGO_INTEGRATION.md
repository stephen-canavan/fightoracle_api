# Django Integration Guide - Option A

## Overview

This guide explains how to integrate the UFC scraper with your Django backend using **UFCStats ID fields** for tracking and updating records.

## How Option A Works

### **Step 1: Add UFCStats ID Fields to Models**

These fields act as **unique identifiers** that link your Django records to the source data from UFCStats.com.

**Why?**
- Prevents duplicate records when re-scraping
- Allows updates to existing records
- Maintains traceability to source data
- Enables incremental updates

### **Step 2: Scraper Outputs JSON with UFCStats IDs**

The scraper already outputs normalized JSON with these IDs:
```json
{
  "ufcstats_fighter_id": "0d8011111be000b2",
  "fname": "Sean",
  "sname": "Strickland",
  ...
}
```

### **Step 3: Conversion Script Maps JSON → Django**

The conversion script:
1. Reads JSON files from `ufc_scraper/data/`
2. Uses `get_or_create(ufcstats_*_id=...)` to find existing records
3. Updates all fields with latest scraped data
4. Handles FK relationships by looking up related objects

**Example:**
```python
# First time: Creates new fighter
fighter, created = Fighter.objects.get_or_create(
    ufcstats_fighter_id="0d8011111be000b2",
    defaults={'fname': 'Sean', 'sname': 'Strickland', ...}
)
# created = True

# Second time: Finds existing fighter and updates
fighter, created = Fighter.objects.get_or_create(
    ufcstats_fighter_id="0d8011111be000b2",
    defaults={'fname': 'Sean', 'sname': 'Strickland', ...}
)
# created = False
# Then update: fighter.height = new_height; fighter.save()
```

---

## Required Model Changes

### **1. Fighter Model** (`api/models/fighter.py`)

Add these fields:

```python
class Fighter(models.Model):
    # ADD THESE FIELDS:
    ufcstats_fighter_id = models.CharField(
        max_length=50, unique=True, db_index=True, null=True, blank=True,
        help_text="UFCStats.com fighter ID for tracking source data"
    )
    stance = models.CharField(max_length=50, blank=True, null=True)
    
    # Career statistics (new fields)
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
    
    # EXISTING FIELDS (no changes):
    fname = models.CharField(max_length=255)
    sname = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    promotion = models.ForeignKey("api.Promotion", on_delete=models.PROTECT)
    weight_class = models.CharField(max_length=255, choices=WeightClass.choices)
    dob = models.DateField()
    height = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    reach = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    wins = models.PositiveSmallIntegerField(default=0)
    losses = models.PositiveSmallIntegerField(default=0)
    draws = models.PositiveSmallIntegerField(default=0)
    no_contests = models.PositiveSmallIntegerField(default=0)
    dqs = models.PositiveSmallIntegerField(default=0)
    country = CountryField(blank=True, null=True)
    avatar = models.ImageField(upload_to=fighter_image_upload_path, null=True, blank=True)
```

### **2. Event Model** (`api/models/event.py`)

Add this field:

```python
class Event(models.Model):
    # ADD THIS FIELD:
    ufcstats_event_id = models.CharField(
        max_length=50, unique=True, db_index=True, null=True, blank=True,
        help_text="UFCStats.com event ID for tracking source data"
    )
    
    # EXISTING FIELDS (no changes):
    name = models.CharField(max_length=255)
    promotion = models.ForeignKey("api.Promotion", on_delete=models.PROTECT)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    venue = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=EventStatus.choices)
    date = models.DateTimeField()
```

### **3. Fight Model** (`api/models/fight.py`)

Add these fields:

```python
class Fight(models.Model):
    # ADD THESE FIELDS:
    ufcstats_fight_id = models.CharField(
        max_length=50, unique=True, db_index=True, null=True, blank=True,
        help_text="UFCStats.com fight ID for tracking source data"
    )
    method_details = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Detailed method description (e.g., 'Punches to Head')"
    )
    fight_time = models.CharField(
        max_length=10, blank=True, null=True,
        help_text="Time of finish (e.g., '2:23')"
    )
    referee = models.CharField(max_length=255, blank=True, null=True)
    
    # Comprehensive fight statistics from UFCStats
    fighter_red_stats = models.JSONField(
        blank=True, null=True,
        help_text="Complete statistics for red corner fighter"
    )
    fighter_blue_stats = models.JSONField(
        blank=True, null=True,
        help_text="Complete statistics for blue corner fighter"
    )
    
    # EXISTING FIELDS (no changes):
    event = models.ForeignKey("api.Event", on_delete=models.PROTECT)
    fighter_red = models.ForeignKey("api.Fighter", related_name="red_corner", on_delete=models.PROTECT)
    fighter_blue = models.ForeignKey("api.Fighter", related_name="blue_corner", on_delete=models.PROTECT)
    fighter_red_record = models.JSONField(max_length=50, blank=True, null=True)
    fighter_blue_record = models.JSONField(max_length=50, blank=True, null=True)
    weight_class = models.CharField(max_length=255, choices=WeightClass.choices)
    scheduled_rounds = models.PositiveSmallIntegerField(default=3)
    is_title_fight = models.BooleanField(default=False)
    is_main_event = models.BooleanField(default=False)
    card_tier = models.CharField(max_length=255, choices=CardTier.choices)
    status = models.CharField(max_length=255, choices=FightStatus.choices)
    winner = models.ForeignKey("api.Fighter", blank=True, null=True, on_delete=models.PROTECT)
    winning_method = models.CharField(max_length=255, choices=Method.choices, blank=True, null=True)
    winning_round = models.IntegerField(blank=True, null=True)
```

---

## Workflow Example

### **Complete Flow:**

```bash
# 1. Scrape data from UFCStats.com
cd /home/etnseca/git/fightoracle_api
python ufc_scraper/main.py --update-recent 7

# 2. Import scraped data into Django
python manage.py import_ufcstats

# 3. Verify in Django shell
python manage.py shell
>>> from api.models import Fighter, Fight, Event
>>> Fighter.objects.filter(ufcstats_fighter_id__isnull=False).count()
>>> Fight.objects.filter(ufcstats_fight_id__isnull=False).count()
```

### **How Import Works:**

```python
# Pseudo-code for import_ufcstats command

# Import fighters
for fighter_file in 'ufc_scraper/data/fighters/*.json':
    data = load_json(fighter_file)
    
    fighter, created = Fighter.objects.get_or_create(
        ufcstats_fighter_id=data['ufcstats_fighter_id'],
        defaults={
            'fname': data['fname'],
            'sname': data['sname'],
            'promotion': get_ufc_promotion(),  # Lookup UFC promotion
            'height': data['height_cm'],
            'reach': data['reach_cm'],
            'slpm': data['career_stats']['slpm'],
            # ... all other fields
        }
    )
    
    if not created:
        # Update existing record with latest data
        fighter.height = data['height_cm']
        fighter.slpm = data['career_stats']['slpm']
        # ... update all fields
        fighter.save()
    
    print(f"{'Created' if created else 'Updated'} fighter: {fighter.name}")

# Import events
for event in load_json('ufc_scraper/data/events.json')['events']:
    event_obj, created = Event.objects.get_or_create(
        ufcstats_event_id=event['ufcstats_event_id'],
        defaults={
            'name': event['name'],
            'date': event['date'],
            'promotion': get_ufc_promotion(),
            # ... all other fields
        }
    )

# Import fights (with FK lookups)
for fight_file in 'ufc_scraper/data/fights/*.json':
    data = load_json(fight_file)
    
    # Lookup related objects by their UFCStats IDs
    event = Event.objects.get(ufcstats_event_id=data['ufcstats_event_id'])
    fighter_red = Fighter.objects.get(ufcstats_fighter_id=data['ufcstats_fighter_red_id'])
    fighter_blue = Fighter.objects.get(ufcstats_fighter_id=data['ufcstats_fighter_blue_id'])
    winner = Fighter.objects.get(ufcstats_fighter_id=data['ufcstats_winner_id'])
    
    fight, created = Fight.objects.get_or_create(
        ufcstats_fight_id=data['ufcstats_fight_id'],
        defaults={
            'event': event,
            'fighter_red': fighter_red,
            'fighter_blue': fighter_blue,
            'winner': winner,
            'weight_class': map_weight_class(data['weight_class']),
            'winning_method': map_method(data['method']),
            'winning_round': data['round'],
            'fight_time': data['time'],
            'referee': data['referee'],
            'fighter_red_stats': data['fighter_red_stats'],
            'fighter_blue_stats': data['fighter_blue_stats'],
        }
    )
```

---

## Benefits

1. **No Duplicates**: `ufcstats_fighter_id` is unique - can't create duplicate fighters
2. **Updates Work**: Re-running import updates existing records with latest stats
3. **Traceability**: Can always trace Django record back to UFCStats source
4. **Incremental**: Only new fighters/fights are created, existing ones are updated
5. **Data Integrity**: FK relationships maintained through UFCStats ID lookups

---

## Next Steps

**Ready to proceed with:**

1. ✅ Scraper moved to `/home/etnseca/git/fightoracle_api/ufc_scraper/`

2. **Create model migrations** - Add the new fields to your models

3. **Create `import_ufcstats` management command** - Handles JSON → Django conversion

4. **Create mapping functions** - Map UFCStats weight classes/methods to your choices

**Should I create these files now?**

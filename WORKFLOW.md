# Complete Django Integration Workflow

## ✅ What Was Done

1. ✅ Moved scraper to `/home/etnseca/git/fightoracle_api/ufc_scraper/`
2. ✅ Updated Django models with UFCStats ID fields and career stats
3. ✅ Created mapping utilities for weight classes and methods
4. ✅ Created `import_ufcstats` management command
5. ✅ Created `scrape_ufcstats` management command

---

## 🚀 Complete Workflow

### **Step 1: Create and Run Migrations**

```bash
cd /home/etnseca/git/fightoracle_api

# Create migration for new fields
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

This adds:
- `Fighter`: `ufcstats_fighter_id`, `stance`, `slpm`, `str_acc`, `sapm`, `str_def`, `td_avg`, `td_acc`, `td_def`, `sub_avg`
- `Event`: `ufcstats_event_id`
- `Fight`: `ufcstats_fight_id`, `method_details`, `fight_time`, `referee`, `fighter_red_stats`, `fighter_blue_stats`

### **Step 2: Scrape Data**

**Option A: Using Django management command**
```bash
# Scrape recent events (last 7 days)
python manage.py scrape_ufcstats --recent 7

# Scrape specific fighter
python manage.py scrape_ufcstats --fighter "Sean Strickland"

# Scrape specific event
python manage.py scrape_ufcstats --event "UFC 326"
```

**Option B: Using scraper directly**
```bash
python ufc_scraper/main.py --update-recent 7
python ufc_scraper/main.py --fighter "Sean Strickland"
python ufc_scraper/main.py --event "UFC 326"
```

### **Step 3: Import to Django Database**

```bash
# Import all scraped data
python manage.py import_ufcstats --all

# Or import selectively
python manage.py import_ufcstats --events
python manage.py import_ufcstats --fighters
python manage.py import_ufcstats --fights
```

**What happens:**
- **First run**: Creates new records in database
- **Subsequent runs**: Updates existing records (no duplicates)
- **FK relationships**: Automatically linked via UFCStats IDs

### **Step 4: Verify Data**

```bash
python manage.py shell
```

```python
from api.models import Fighter, Event, Fight

# Check imported fighters
Fighter.objects.filter(ufcstats_fighter_id__isnull=False).count()
sean = Fighter.objects.get(ufcstats_fighter_id='0d8011111be000b2')
print(f"{sean.name}: {sean.wins}-{sean.losses}-{sean.draws}")
print(f"SLpM: {sean.slpm}, Str Acc: {sean.str_acc}%")

# Check imported events
Event.objects.filter(ufcstats_event_id__isnull=False).count()

# Check imported fights
Fight.objects.filter(ufcstats_fight_id__isnull=False).count()
fight = Fight.objects.get(ufcstats_fight_id='8d740c844353ae0e')
print(f"{fight.fighter_red.name} vs {fight.fighter_blue.name}")
print(f"Winner: {fight.winner.name} by {fight.winning_method}")
print(f"Red corner sig strikes: {fight.fighter_red_stats['sig_strikes']}")
```

---

## 🔄 Daily Update Workflow

### **Automated Daily Updates (Recommended)**

**Option 1: Cron Job**
```bash
# Edit crontab
crontab -e

# Add daily update at 3 AM
0 3 * * * cd /home/etnseca/git/fightoracle_api && /home/etnseca/raptor_env/bin/python manage.py scrape_ufcstats --recent 7 && /home/etnseca/raptor_env/bin/python manage.py import_ufcstats --all >> /var/log/ufc_import.log 2>&1
```

**Option 2: Celery Task**
```python
# api/tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def update_ufc_stats():
    """Daily task to scrape and import UFC stats."""
    call_command('scrape_ufcstats', '--recent', 7)
    call_command('import_ufcstats', '--all')
```

---

## 📊 Data Flow Diagram

```
UFCStats.com
     ↓
[Scraper] → JSON files (ufc_scraper/data/)
     ↓
[import_ufcstats] → Django ORM
     ↓
Postgres Database
     ↓
Django REST API
     ↓
Frontend
```

---

## 🔍 How UFCStats IDs Work

### **Example: Updating Sean Strickland**

**First Scrape (Feb 21, 2026):**
```bash
python manage.py scrape_ufcstats --fighter "Sean Strickland"
python manage.py import_ufcstats --fighters
```

Database:
```
Fighter(id=1, ufcstats_fighter_id='0d8011111be000b2', fname='Sean', sname='Strickland', wins=29, losses=7)
```

**Second Scrape (Feb 28, 2026 - after new fight):**
```bash
python manage.py scrape_ufcstats --fighter "Sean Strickland"
python manage.py import_ufcstats --fighters
```

Database:
```
Fighter(id=1, ufcstats_fighter_id='0d8011111be000b2', fname='Sean', sname='Strickland', wins=30, losses=7)
                                                                                          ↑ UPDATED
```

**Key Point:** Same `id=1` in database, just updated fields. No duplicate created!

---

## 🔗 FK Relationship Example

**Importing a Fight:**

```python
# Scraped JSON
{
  "ufcstats_fight_id": "8d740c844353ae0e",
  "ufcstats_event_id": "79ab17db3b40831a",
  "ufcstats_fighter_red_id": "0d8011111be000b2",
  "ufcstats_fighter_blue_id": "093e1f5bb73850be",
  "ufcstats_winner_id": "0d8011111be000b2"
}

# Import process
event = Event.objects.get(ufcstats_event_id='79ab17db3b40831a')  # Finds event by UFCStats ID
fighter_red = Fighter.objects.get(ufcstats_fighter_id='0d8011111be000b2')  # Finds Sean
fighter_blue = Fighter.objects.get(ufcstats_fighter_id='093e1f5bb73850be')  # Finds Anthony
winner = fighter_red  # Same as red corner

Fight.objects.create(
    ufcstats_fight_id='8d740c844353ae0e',
    event=event,           # Django FK to Event(id=5)
    fighter_red=fighter_red,  # Django FK to Fighter(id=1)
    fighter_blue=fighter_blue,  # Django FK to Fighter(id=2)
    winner=winner          # Django FK to Fighter(id=1)
)

# Result in database:
# Fight(id=10, ufcstats_fight_id='8d740c844353ae0e', event_id=5, fighter_red_id=1, fighter_blue_id=2, winner_id=1)
```

---

## 🎯 Next Steps

1. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Test with sample data:**
   ```bash
   python manage.py scrape_ufcstats --recent 1
   python manage.py import_ufcstats --all
   ```

3. **Verify in Django admin or shell**

4. **Set up daily cron job**

---

## ⚠️ Important Notes

- **Promotion**: Import assumes UFC promotion exists in database
- **Weight Class**: Fighters default to 'MW' - may need manual adjustment
- **Order matters**: Import events → fighters → fights (due to FK dependencies)
- **First import**: Run `--events` and `--fighters` before `--fights`

**Ready to run migrations?**

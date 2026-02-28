# UFC Scraper - Complete Guide

## 🎯 What Was Built

A production-ready Python web scraper that extracts comprehensive UFC data from ufcstats.com with:
- **Modular architecture** for maintainability
- **Normalized JSON output** matching your Postgres schema
- **CLI interface** with advanced filtering
- **Robust error handling** with exponential backoff
- **Rate limiting** to respect server resources

## 📁 Project Structure

```
ufc_scraper/
├── config.py                    # Configuration constants
├── main.py                      # Entry point
├── cli.py                       # CLI interface
├── requirements.txt             # Dependencies
├── README.md                    # Full documentation
├── IMPLEMENTATION.md            # Implementation summary
├── quickstart.sh                # Quick start guide
├── demo.py                      # Demo script
├── ingest_to_postgres.py        # Postgres ingestion example
│
├── scrapers/
│   ├── base.py                  # Base scraper with retry logic
│   ├── events.py                # Event scraper
│   ├── fights.py                # Fight scraper
│   └── fighters.py              # Fighter scraper
│
├── parsers/
│   ├── fight_parser.py          # Fight HTML parser
│   └── fighter_parser.py        # Fighter HTML parser
│
├── storage/
│   └── json_store.py            # JSON file management
│
└── data/
    ├── events.json              # All events
    ├── fights/                  # Individual fight files
    │   └── {fight_id}.json
    └── fighters/                # Individual fighter files
        └── {fighter_id}_{fname}_{sname}.json
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd /home/etnseca/ufc_scraper
/home/etnseca/raptor_env/bin/python -m pip install -r requirements.txt
```

### 2. Run Demo
```bash
/home/etnseca/raptor_env/bin/python demo.py
```

This will scrape:
- Sean Strickland's fighter profile
- Strickland vs Hernandez fight with full statistics
- All upcoming UFC events

### 3. View Results
```bash
# View fighter data
cat data/fighters/0d8011111be000b2_sean_strickland.json | python3 -m json.tool

# View fight data
cat data/fights/8d740c844353ae0e.json | python3 -m json.tool

# View events
cat data/events.json | python3 -m json.tool
```

## 📖 Usage Examples

### Scrape Specific Data

```bash
# Scrape a specific fighter
/home/etnseca/raptor_env/bin/python main.py --fighter "Conor McGregor"

# Scrape a specific event and all its fights
/home/etnseca/raptor_env/bin/python main.py --event "UFC 300"

# Scrape a specific fight by ID
/home/etnseca/raptor_env/bin/python main.py --fight-id abc123def456
```

### Bulk Updates

```bash
# Update all events (completed + upcoming)
/home/etnseca/raptor_env/bin/python main.py --update-events

# Update all fighters (WARNING: This will take hours - 3000+ fighters)
/home/etnseca/raptor_env/bin/python main.py --update-fighters

# Update only recent events (last 7 days) - RECOMMENDED for daily cron
/home/etnseca/raptor_env/bin/python main.py --update-recent 7
```

### Filtering

```bash
# Filter events by date range
/home/etnseca/raptor_env/bin/python main.py --date-from 2024-01-01 --date-to 2024-12-31

# Check scraping status
/home/etnseca/raptor_env/bin/python main.py --status
```

## 🔗 Django Integration

### Option 1: Cron Job (Recommended)

```bash
# Edit crontab
crontab -e

# Add daily update at 3 AM
0 3 * * * cd /home/etnseca/ufc_scraper && /home/etnseca/raptor_env/bin/python main.py --update-recent 7 >> /var/log/ufc_scraper.log 2>&1
```

### Option 2: Django Management Command

Create `yourapp/management/commands/scrape_ufc.py`:

```python
from django.core.management.base import BaseCommand
import subprocess

class Command(BaseCommand):
    help = 'Scrape UFC stats'
    
    def add_arguments(self, parser):
        parser.add_argument('--recent', type=int, default=7)
        parser.add_argument('--fighter', type=str)
        parser.add_argument('--event', type=str)
    
    def handle(self, *args, **options):
        cmd = ['/home/etnseca/raptor_env/bin/python', '/home/etnseca/ufc_scraper/main.py']
        
        if options['recent']:
            cmd.extend(['--update-recent', str(options['recent'])])
        elif options['fighter']:
            cmd.extend(['--fighter', options['fighter']])
        elif options['event']:
            cmd.extend(['--event', options['event']])
        
        subprocess.run(cmd)
```

Run with:
```bash
python manage.py scrape_ufc --recent 7
python manage.py scrape_ufc --fighter "Sean Strickland"
```

### Option 3: Celery Task

```python
from celery import shared_task
import subprocess

@shared_task
def scrape_recent_ufc_data(days=7):
    """Celery task to scrape recent UFC data."""
    subprocess.run([
        '/home/etnseca/raptor_env/bin/python',
        '/home/etnseca/ufc_scraper/main.py',
        '--update-recent', str(days)
    ])
```

## 💾 Postgres Ingestion

Use the provided `ingest_to_postgres.py` script as a template:

```bash
# Update script with your DB credentials
nano ingest_to_postgres.py

# Run ingestion
python ingest_to_postgres.py
```

The script handles:
- Upserts (INSERT ... ON CONFLICT DO UPDATE)
- Proper FK relationships
- Batch processing

## 📊 Data Schema

### Foreign Key Relationships

```
Events (ufcstats_event_id)
  ↑
Fights (ufcstats_event_id) → Events
  ↓
Fighters (ufcstats_fighter_id) ← Fights (ufcstats_fighter_red_id, ufcstats_fighter_blue_id, ufcstats_winner_id)
```

### Key Fields

**Events:**
- `ufcstats_event_id` (PK)
- `name`, `date`, `country`, `city`, `venue`

**Fighters:**
- `ufcstats_fighter_id` (PK)
- `fname`, `sname`, `nickname`
- `height_cm`, `weight_lbs`, `reach_cm` (numeric for calculations)
- `stance`, `dob`
- `record`: wins, losses, draws, no_contests, dqs
- `career_stats`: slpm, str_acc, sapm, str_def, td_avg, td_acc, td_def, sub_avg

**Fights:**
- `ufcstats_fight_id` (PK)
- `ufcstats_event_id` (FK → events)
- `ufcstats_fighter_red_id` (FK → fighters)
- `ufcstats_fighter_blue_id` (FK → fighters)
- `ufcstats_winner_id` (FK → fighters)
- `weight_class`, `method`, `method_details`, `round`, `time`, `referee`
- `fighter_red_stats`, `fighter_blue_stats` (comprehensive statistics)

## ⚙️ Configuration

Edit `config.py` to adjust:

```python
REQUEST_DELAY = 1.5              # Seconds between requests
RETRY_MAX_ATTEMPTS = 5           # Max retry attempts
RETRY_INITIAL_DELAY = 2          # Initial retry delay
RETRY_MAX_DELAY = 60             # Max retry delay
```

## 🐛 Troubleshooting

**Issue: Module not found**
```bash
# Ensure dependencies are installed
/home/etnseca/raptor_env/bin/python -m pip install -r requirements.txt
```

**Issue: Rate limiting / 429 errors**
```bash
# Increase REQUEST_DELAY in config.py
REQUEST_DELAY = 3.0
```

**Issue: Timeout errors**
```bash
# Check internet connection
# Increase RETRY_MAX_ATTEMPTS in config.py
```

## 📈 Performance Notes

- **Single fighter**: ~2 seconds
- **Single fight**: ~2 seconds
- **Single event (10 fights)**: ~20 seconds
- **All events**: ~5 seconds
- **All fighters (3000+)**: ~2-3 hours (with rate limiting)
- **Recent update (7 days, ~3 events)**: ~1-2 minutes

## ✅ Verification

Run the demo to verify everything works:

```bash
/home/etnseca/raptor_env/bin/python demo.py
```

Expected output:
```
=== UFC Scraper Demo ===

1. Scraping fighter: Sean Strickland
   ✓ Saved: Sean Strickland
   Record: 30-7-0
   Height: 185.4 cm, Reach: 193.0 cm

2. Scraping fight: Strickland vs Hernandez
   ✓ Saved fight 8d740c844353ae0e
   Method: KO/TKO - Punches to Head On Ground
   Round 3 at 2:23
   Red corner strikes: 110/241
   Blue corner strikes: 55/122

3. Scraping upcoming events
   ✓ Saved 9 upcoming events
   Next event: UFC Fight Night: Moreno vs. Kavanagh on 2026-02-28

=== Demo Complete ===
```

## 🎓 Next Steps

1. **Test with your data**: Run `--update-recent 7` to get last week's events
2. **Set up cron job**: Schedule daily updates
3. **Ingest to Postgres**: Use `ingest_to_postgres.py` as template
4. **Integrate with Django**: Create management command or Celery task
5. **Monitor logs**: Check `ufc_scraper.log` for any issues

## 📞 Support

For issues or enhancements, check:
- `README.md` - Full documentation
- `IMPLEMENTATION.md` - Technical details
- `ufc_scraper.log` - Error logs

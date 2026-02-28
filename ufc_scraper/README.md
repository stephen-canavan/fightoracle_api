# UFC Stats Scraper

A modular Python web scraper for extracting comprehensive UFC fight and fighter data from ufcstats.com. Designed for integration with Django backends and Postgres databases.

## Features

- Scrape comprehensive fight statistics (strikes by target/position, control time, per-round breakdowns)
- Scrape full fighter profiles (physical attributes, career stats, fight history)
- Normalized JSON output ready for Postgres ingestion
- CLI interface with advanced filtering
- Retry logic with exponential backoff
- Rate limiting to respect server resources
- Metadata tracking for incremental updates

## Installation

```bash
cd ufc_scraper
pip install -r requirements.txt
```

## Usage

### Basic Commands

**Update all events:**
```bash
python main.py --update-events
```

**Update all fighters:**
```bash
python main.py --update-fighters
```

**Update recent events (last 30 days):**
```bash
python main.py --update-recent 30
```

### Query Specific Data

**Fetch specific fighter:**
```bash
python main.py --fighter "Sean Strickland"
```

**Fetch specific event and all its fights:**
```bash
python main.py --event "UFC 300"
```

**Fetch specific fight by ID:**
```bash
python main.py --fight-id 8d740c844353ae0e
```

### Advanced Filtering

**Filter events by date range:**
```bash
python main.py --date-from 2024-01-01 --date-to 2024-12-31
```

**Filter by weight class:**
```bash
python main.py --weight-class Middleweight
```

### Options

**Verbose logging:**
```bash
python main.py --update-events --verbose
```

**Show last update status:**
```bash
python main.py --status
```

## Data Structure

### Events (`data/events.json`)
```json
{
  "events": [
    {
      "ufcstats_event_id": "79ab17db3b40831a",
      "name": "UFC Fight Night: Strickland vs. Hernandez",
      "date": "2026-02-21",
      "location": "Houston, Texas, USA",
      "country": "United States",
      "city": "Houston",
      "venue": "Toyota Centre"
    }
  ]
}
```

### Fights (`data/fights/{fight_id}.json`)
```json
{
  "ufcstats_fight_id": "8d740c844353ae0e",
  "ufcstats_event_id": "79ab17db3b40831a",
  "ufcstats_fighter_red_id": "0d8011111be000b2",
  "ufcstats_fighter_blue_id": "093e1f5bb73850be",
  "ufcstats_winner_id": "0d8011111be000b2",
  "weight_class": "Middleweight",
  "method": "KO/TKO",
  "method_details": "Punches",
  "round": 3,
  "time": "2:23",
  "referee": "Herb Dean",
  "fighter_red_stats": {
    "knockdowns": 1,
    "sig_strikes": {"landed": 110, "attempted": 241},
    "sig_strikes_pct": 45,
    "total_strikes": {"landed": 111, "attempted": 242},
    "takedowns": {"landed": 0, "attempted": 0},
    "takedown_pct": 0,
    "submission_attempts": 0,
    "reversals": 0,
    "control_time": "0:18",
    "sig_strikes_breakdown": {
      "head": {"landed": 93, "attempted": 219},
      "body": {"landed": 9, "attempted": 14},
      "leg": {"landed": 8, "attempted": 8},
      "distance": {"landed": 101, "attempted": 230},
      "clinch": {"landed": 2, "attempted": 3},
      "ground": {"landed": 7, "attempted": 8}
    }
  },
  "fighter_blue_stats": { ... },
  "per_round_stats": [
    {
      "round": 1,
      "fighter_red": { ... },
      "fighter_blue": { ... }
    }
  ]
}
```

### Fighters (`data/fighters/{fighter_id}_{fname}_{sname}.json`)
```json
{
  "ufcstats_fighter_id": "0d8011111be000b2",
  "fname": "Sean",
  "sname": "Strickland",
  "nickname": "",
  "height_cm": 185.4,
  "weight_lbs": 185,
  "reach_cm": 193.0,
  "stance": "Orthodox",
  "dob": "1991-02-27",
  "record": {
    "wins": 30,
    "losses": 7,
    "draws": 0,
    "no_contests": 0,
    "dqs": 0
  },
  "career_stats": {
    "slpm": 6.04,
    "str_acc": 42,
    "sapm": 4.57,
    "str_def": 60,
    "td_avg": 0.71,
    "td_acc": 64,
    "td_def": 76,
    "sub_avg": 0.2
  }
}
```

## Foreign Key Relationships

The JSON structure uses normalized foreign keys for Postgres ingestion:

- **Fights → Events**: `ufcstats_event_id` references `events.ufcstats_event_id`
- **Fights → Fighters**: `ufcstats_fighter_red_id` and `ufcstats_fighter_blue_id` reference `fighters.ufcstats_fighter_id`
- **Fights → Winner**: `ufcstats_winner_id` references `fighters.ufcstats_fighter_id`

All UFCStats IDs are prefixed with `ufcstats_` to distinguish them from your database's auto-increment IDs.

## Integration with Django Backend

### Scheduled Updates with Cron

Create a cron job to run daily updates:

```bash
# Edit crontab
crontab -e

# Add daily update at 3 AM
0 3 * * * cd /path/to/ufc_scraper && python main.py --update-recent 7 >> /var/log/ufc_scraper.log 2>&1
```

### Django Management Command

Create a Django management command to trigger scraping:

```python
# yourapp/management/commands/scrape_ufc.py
from django.core.management.base import BaseCommand
import subprocess

class Command(BaseCommand):
    help = 'Scrape UFC stats'
    
    def add_arguments(self, parser):
        parser.add_argument('--recent', type=int, default=7)
    
    def handle(self, *args, **options):
        days = options['recent']
        subprocess.run([
            'python', '/path/to/ufc_scraper/main.py',
            '--update-recent', str(days)
        ])
```

Run with: `python manage.py scrape_ufc --recent 7`

### Ingesting JSON into Postgres

Example Python script to load JSON into your database:

```python
import json
import psycopg2

# Load events
with open('data/events.json') as f:
    events = json.load(f)['events']

conn = psycopg2.connect("dbname=yourdb user=youruser")
cur = conn.cursor()

for event in events:
    cur.execute("""
        INSERT INTO events (ufcstats_event_id, name, date, country, city, venue)
        VALUES (%(ufcstats_event_id)s, %(name)s, %(date)s, %(country)s, %(city)s, %(venue)s)
        ON CONFLICT (ufcstats_event_id) DO UPDATE SET
            name = EXCLUDED.name,
            date = EXCLUDED.date
    """, event)

conn.commit()
```

## Architecture

```
ufc_scraper/
├── scrapers/
│   ├── base.py          # Base scraper with retry logic
│   ├── events.py        # Event listing scraper
│   ├── fights.py        # Fight details scraper
│   └── fighters.py      # Fighter details scraper
├── parsers/
│   ├── fight_parser.py  # Parse fight HTML to structured data
│   └── fighter_parser.py # Parse fighter HTML to structured data
├── storage/
│   └── json_store.py    # JSON file management
├── data/
│   ├── events.json      # All events
│   ├── fights/          # Individual fight files
│   ├── fighters/        # Individual fighter files
│   └── metadata.json    # Scraping metadata
├── cli.py               # CLI interface
├── config.py            # Configuration constants
├── main.py              # Entry point
└── requirements.txt     # Dependencies
```

## Configuration

Edit `config.py` to adjust:
- Request delays (default: 1.5s between requests)
- Retry settings (default: 5 attempts with exponential backoff)
- Data directory paths

## Logging

Logs are written to:
- Console (stdout)
- `ufc_scraper.log` file

Log levels:
- `--verbose`: DEBUG level
- Default: INFO level
- `--quiet`: WARNING level only

## Error Handling

The scraper includes:
- Exponential backoff retry (5 attempts, 2s → 60s delays)
- Graceful failure handling (logs errors, continues with remaining items)
- Request timeout protection (30s timeout)
- Rate limiting (1.5s between requests)

## Future Enhancements

Potential additions:
- Incremental updates (only fetch new/changed data)
- Parallel scraping with thread pools
- Data validation and integrity checks
- Export to CSV format
- REST API wrapper
- Real-time monitoring dashboard

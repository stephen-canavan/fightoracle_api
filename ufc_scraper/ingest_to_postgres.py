"""Example script for ingesting UFC scraper JSON data into Postgres."""
import json
import psycopg2
from psycopg2.extras import execute_values

# Database connection (update with your credentials)
conn = psycopg2.connect(
    dbname="your_db",
    user="your_user",
    password="your_password",
    host="localhost"
)
cur = conn.cursor()


def ingest_events():
    """Ingest events from JSON to Postgres."""
    with open('data/events.json') as f:
        data = json.load(f)
    
    events = data['events']
    
    for event in events:
        cur.execute("""
            INSERT INTO events (ufcstats_event_id, name, date, country, city, venue)
            VALUES (%(ufcstats_event_id)s, %(name)s, %(date)s, %(country)s, %(city)s, %(venue)s)
            ON CONFLICT (ufcstats_event_id) DO UPDATE SET
                name = EXCLUDED.name,
                date = EXCLUDED.date,
                country = EXCLUDED.country,
                city = EXCLUDED.city,
                venue = EXCLUDED.venue
        """, event)
    
    conn.commit()
    print(f"Ingested {len(events)} events")


def ingest_fighters():
    """Ingest fighters from JSON to Postgres."""
    import os
    
    fighters_dir = 'data/fighters'
    count = 0
    
    for filename in os.listdir(fighters_dir):
        if not filename.endswith('.json'):
            continue
        
        with open(f'{fighters_dir}/{filename}') as f:
            fighter = json.load(f)
        
        cur.execute("""
            INSERT INTO fighters (
                ufcstats_fighter_id, fname, sname, nickname,
                height_cm, weight_lbs, reach_cm, stance, dob,
                wins, losses, draws, no_contests, dqs,
                slpm, str_acc, sapm, str_def, td_avg, td_acc, td_def, sub_avg
            ) VALUES (
                %(ufcstats_fighter_id)s, %(fname)s, %(sname)s, %(nickname)s,
                %(height_cm)s, %(weight_lbs)s, %(reach_cm)s, %(stance)s, %(dob)s,
                %(wins)s, %(losses)s, %(draws)s, %(no_contests)s, %(dqs)s,
                %(slpm)s, %(str_acc)s, %(sapm)s, %(str_def)s,
                %(td_avg)s, %(td_acc)s, %(td_def)s, %(sub_avg)s
            )
            ON CONFLICT (ufcstats_fighter_id) DO UPDATE SET
                fname = EXCLUDED.fname,
                sname = EXCLUDED.sname,
                height_cm = EXCLUDED.height_cm,
                weight_lbs = EXCLUDED.weight_lbs
        """, {
            **fighter,
            **fighter['record'],
            **fighter['career_stats']
        })
        
        count += 1
    
    conn.commit()
    print(f"Ingested {count} fighters")


def ingest_fights():
    """Ingest fights from JSON to Postgres."""
    import os
    
    fights_dir = 'data/fights'
    count = 0
    
    for filename in os.listdir(fights_dir):
        if not filename.endswith('.json'):
            continue
        
        with open(f'{fights_dir}/{filename}') as f:
            fight = json.load(f)
        
        # Insert basic fight data
        cur.execute("""
            INSERT INTO fights (
                ufcstats_fight_id, ufcstats_event_id,
                ufcstats_fighter_red_id, ufcstats_fighter_blue_id, ufcstats_winner_id,
                weight_class, method, method_details, round, time, referee
            ) VALUES (
                %(ufcstats_fight_id)s, %(ufcstats_event_id)s,
                %(ufcstats_fighter_red_id)s, %(ufcstats_fighter_blue_id)s, %(ufcstats_winner_id)s,
                %(weight_class)s, %(method)s, %(method_details)s, %(round)s, %(time)s, %(referee)s
            )
            ON CONFLICT (ufcstats_fight_id) DO UPDATE SET
                method = EXCLUDED.method,
                round = EXCLUDED.round
        """, fight)
        
        # Insert fight statistics (you may want a separate table for this)
        # Example: fight_stats table with fighter_id, fight_id, and all stats
        
        count += 1
    
    conn.commit()
    print(f"Ingested {count} fights")


if __name__ == '__main__':
    print("Ingesting UFC data into Postgres...")
    
    try:
        ingest_events()
        ingest_fighters()
        ingest_fights()
        print("\n✓ Ingestion complete!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

"""Django management command to import UFCStats scraped data."""
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Fighter, Event, Fight, Promotion
from api.management.commands.ufcstats_mappings import map_weight_class, map_method
import json
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Import scraped UFCStats data into Django database'

    def add_arguments(self, parser):
        parser.add_argument('--fighters', action='store_true', help='Import fighters only')
        parser.add_argument('--events', action='store_true', help='Import events only')
        parser.add_argument('--fights', action='store_true', help='Import fights only')
        parser.add_argument('--all', action='store_true', help='Import everything')

    def handle(self, *args, **options):
        base_path = 'ufc_scraper/data'
        
        if options['all'] or not any([options['fighters'], options['events'], options['fights']]):
            self.import_events(base_path)
            self.import_fighters(base_path)
            self.import_fights(base_path)
        else:
            if options['events']:
                self.import_events(base_path)
            if options['fighters']:
                self.import_fighters(base_path)
            if options['fights']:
                self.import_fights(base_path)
        
        self.stdout.write(self.style.SUCCESS('Import completed!'))

    def import_events(self, base_path):
        """Import events from JSON."""
        self.stdout.write('Importing events...')
        
        events_file = f'{base_path}/events.json'
        if not os.path.exists(events_file):
            self.stdout.write(self.style.WARNING(f'No events file found at {events_file}'))
            return
        
        with open(events_file) as f:
            data = json.load(f)
        
        ufc_promotion = Promotion.objects.get(name='UFC')
        created_count = 0
        updated_count = 0
        
        for event_data in data['events']:
            # Parse date to datetime
            date_str = event_data['date']
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            event, created = Event.objects.get_or_create(
                ufcstats_event_id=event_data['ufcstats_event_id'],
                defaults={
                    'name': event_data['name'],
                    'promotion': ufc_promotion,
                    'country': event_data.get('country', ''),
                    'city': event_data.get('city', ''),
                    'venue': event_data.get('venue', ''),
                    'date': date_obj,
                    'status': 'COMPLETED' if date_obj < datetime.now() else 'SCHEDULED'
                }
            )
            
            if not created:
                event.name = event_data['name']
                event.country = event_data.get('country', '')
                event.city = event_data.get('city', '')
                event.venue = event_data.get('venue', '')
                event.save()
                updated_count += 1
            else:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Events: {created_count} created, {updated_count} updated'
        ))

    def import_fighters(self, base_path):
        """Import fighters from JSON."""
        self.stdout.write('Importing fighters...')
        
        fighters_dir = f'{base_path}/fighters'
        if not os.path.exists(fighters_dir):
            self.stdout.write(self.style.WARNING(f'No fighters directory found at {fighters_dir}'))
            return
        
        ufc_promotion = Promotion.objects.get(name='UFC')
        created_count = 0
        updated_count = 0
        
        for filename in os.listdir(fighters_dir):
            if not filename.endswith('.json'):
                continue
            
            with open(f'{fighters_dir}/{filename}') as f:
                data = json.load(f)
            
            # Parse DOB
            dob = datetime.strptime(data['dob'], '%Y-%m-%d').date() if data.get('dob') else None
            
            fighter, created = Fighter.objects.get_or_create(
                ufcstats_fighter_id=data['ufcstats_fighter_id'],
                defaults={
                    'fname': data['fname'],
                    'sname': data['sname'],
                    'nickname': data.get('nickname', ''),
                    'promotion': ufc_promotion,
                    'weight_class': 'MW',  # Default, update manually if needed
                    'dob': dob,
                    'stance': data.get('stance'),
                    'height': data.get('height_cm'),
                    'reach': data.get('reach_cm'),
                    'wins': data['record']['wins'],
                    'losses': data['record']['losses'],
                    'draws': data['record']['draws'],
                    'no_contests': data['record'].get('no_contests', 0),
                    'dqs': data['record'].get('dqs', 0),
                    'slpm': data['career_stats'].get('slpm'),
                    'str_acc': data['career_stats'].get('str_acc'),
                    'sapm': data['career_stats'].get('sapm'),
                    'str_def': data['career_stats'].get('str_def'),
                    'td_avg': data['career_stats'].get('td_avg'),
                    'td_acc': data['career_stats'].get('td_acc'),
                    'td_def': data['career_stats'].get('td_def'),
                    'sub_avg': data['career_stats'].get('sub_avg'),
                }
            )
            
            if not created:
                # Update existing fighter
                fighter.height = data.get('height_cm')
                fighter.reach = data.get('reach_cm')
                fighter.wins = data['record']['wins']
                fighter.losses = data['record']['losses']
                fighter.draws = data['record']['draws']
                fighter.no_contests = data['record'].get('no_contests', 0)
                fighter.dqs = data['record'].get('dqs', 0)
                fighter.slpm = data['career_stats'].get('slpm')
                fighter.str_acc = data['career_stats'].get('str_acc')
                fighter.sapm = data['career_stats'].get('sapm')
                fighter.str_def = data['career_stats'].get('str_def')
                fighter.td_avg = data['career_stats'].get('td_avg')
                fighter.td_acc = data['career_stats'].get('td_acc')
                fighter.td_def = data['career_stats'].get('td_def')
                fighter.sub_avg = data['career_stats'].get('sub_avg')
                fighter.save()
                updated_count += 1
            else:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Fighters: {created_count} created, {updated_count} updated'
        ))

    def import_fights(self, base_path):
        """Import fights from JSON."""
        self.stdout.write('Importing fights...')
        
        fights_dir = f'{base_path}/fights'
        if not os.path.exists(fights_dir):
            self.stdout.write(self.style.WARNING(f'No fights directory found at {fights_dir}'))
            return
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for filename in os.listdir(fights_dir):
            if not filename.endswith('.json'):
                continue
            
            with open(f'{fights_dir}/{filename}') as f:
                data = json.load(f)
            
            # Lookup related objects
            try:
                event = Event.objects.get(ufcstats_event_id=data['ufcstats_event_id'])
                fighter_red = Fighter.objects.get(ufcstats_fighter_id=data['ufcstats_fighter_red_id'])
                fighter_blue = Fighter.objects.get(ufcstats_fighter_id=data['ufcstats_fighter_blue_id'])
                winner = Fighter.objects.get(ufcstats_fighter_id=data['ufcstats_winner_id']) if data.get('ufcstats_winner_id') else None
            except (Event.DoesNotExist, Fighter.DoesNotExist) as e:
                self.stdout.write(self.style.WARNING(
                    f"Skipping fight {data['ufcstats_fight_id']}: {e}"
                ))
                skipped_count += 1
                continue
            
            fight, created = Fight.objects.get_or_create(
                ufcstats_fight_id=data['ufcstats_fight_id'],
                defaults={
                    'event': event,
                    'fighter_red': fighter_red,
                    'fighter_blue': fighter_blue,
                    'winner': winner,
                    'weight_class': map_weight_class(data.get('weight_class')),
                    'winning_method': map_method(data.get('method')),
                    'winning_round': data.get('round'),
                    'method_details': data.get('method_details'),
                    'fight_time': data.get('time'),
                    'referee': data.get('referee'),
                    'fighter_red_stats': data.get('fighter_red_stats'),
                    'fighter_blue_stats': data.get('fighter_blue_stats'),
                    'status': 'COMPLETED',
                    'scheduled_rounds': 3,  # Default
                }
            )
            
            if not created:
                # Update existing fight
                fight.winner = winner
                fight.winning_method = map_method(data.get('method'))
                fight.winning_round = data.get('round')
                fight.method_details = data.get('method_details')
                fight.fight_time = data.get('time')
                fight.referee = data.get('referee')
                fight.fighter_red_stats = data.get('fighter_red_stats')
                fight.fighter_blue_stats = data.get('fighter_blue_stats')
                fight.save()
                updated_count += 1
            else:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Fights: {created_count} created, {updated_count} updated, {skipped_count} skipped'
        ))

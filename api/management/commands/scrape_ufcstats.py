"""Django management command to run UFC scraper."""
from django.core.management.base import BaseCommand
import subprocess
import sys


class Command(BaseCommand):
    help = 'Scrape UFC stats from ufcstats.com'

    def add_arguments(self, parser):
        parser.add_argument('--recent', type=int, help='Update events from last N days')
        parser.add_argument('--fighter', type=str, help='Scrape specific fighter by name')
        parser.add_argument('--event', type=str, help='Scrape specific event by name')
        parser.add_argument('--fight-id', type=str, help='Scrape specific fight by ID')
        parser.add_argument('--update-events', action='store_true', help='Update all events')
        parser.add_argument('--update-fighters', action='store_true', help='Update all fighters')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')

    def handle(self, *args, **options):
        cmd = [sys.executable, 'ufc_scraper/main.py']
        
        if options['recent']:
            cmd.extend(['--update-recent', str(options['recent'])])
        elif options['fighter']:
            cmd.extend(['--fighter', options['fighter']])
        elif options['event']:
            cmd.extend(['--event', options['event']])
        elif options['fight_id']:
            cmd.extend(['--fight-id', options['fight_id']])
        elif options['update_events']:
            cmd.append('--update-events')
        elif options['update_fighters']:
            cmd.append('--update-fighters')
        else:
            self.stdout.write(self.style.ERROR('No scraping option specified'))
            return
        
        if options['verbose']:
            cmd.append('--verbose')
        
        self.stdout.write(f'Running: {" ".join(cmd)}')
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            self.stdout.write(self.style.SUCCESS('Scraping completed!'))
        else:
            self.stdout.write(self.style.ERROR('Scraping failed'))

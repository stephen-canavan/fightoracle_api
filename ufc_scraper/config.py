"""Configuration constants for UFC scraper."""
import os

BASE_URL = "http://ufcstats.com"
REQUEST_DELAY = 1.5
RETRY_INITIAL_DELAY = 2
RETRY_MAX_DELAY = 60
RETRY_MAX_ATTEMPTS = 5
RETRY_BACKOFF_FACTOR = 2

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Use absolute path relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")
FIGHTS_DIR = os.path.join(DATA_DIR, "fights")
FIGHTERS_DIR = os.path.join(DATA_DIR, "fighters")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")
LOG_FILE = os.path.join(BASE_DIR, "ufc_scraper.log")

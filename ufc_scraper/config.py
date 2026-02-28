"""Configuration constants for UFC scraper."""

BASE_URL = "http://ufcstats.com"
REQUEST_DELAY = 1.5
RETRY_INITIAL_DELAY = 2
RETRY_MAX_DELAY = 60
RETRY_MAX_ATTEMPTS = 5
RETRY_BACKOFF_FACTOR = 2

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

DATA_DIR = "data"
EVENTS_FILE = f"{DATA_DIR}/events.json"
FIGHTS_DIR = f"{DATA_DIR}/fights"
FIGHTERS_DIR = f"{DATA_DIR}/fighters"
METADATA_FILE = f"{DATA_DIR}/metadata.json"
LOG_FILE = "ufc_scraper.log"

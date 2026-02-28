"""Base scraper with retry logic and request handling."""
import time
import logging
from functools import wraps
import requests
from bs4 import BeautifulSoup
from config import (
    BASE_URL, REQUEST_DELAY, RETRY_INITIAL_DELAY, RETRY_MAX_DELAY,
    RETRY_MAX_ATTEMPTS, RETRY_BACKOFF_FACTOR, USER_AGENT
)

logger = logging.getLogger(__name__)


def retry_with_backoff(func):
    """Decorator for exponential backoff retry logic."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        delay = RETRY_INITIAL_DELAY
        for attempt in range(RETRY_MAX_ATTEMPTS):
            try:
                return func(*args, **kwargs)
            except (requests.RequestException, requests.Timeout) as e:
                if attempt == RETRY_MAX_ATTEMPTS - 1:
                    logger.error(f"Failed after {RETRY_MAX_ATTEMPTS} attempts: {e}")
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay = min(delay * RETRY_BACKOFF_FACTOR, RETRY_MAX_DELAY)
        return None
    return wrapper


class BaseScraper:
    """Base scraper with common HTTP request functionality."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()
    
    @retry_with_backoff
    def fetch_page(self, url):
        """Fetch a page with retry logic and rate limiting."""
        self._rate_limit()
        logger.info(f"Fetching: {url}")
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'lxml')
    
    def build_url(self, path):
        """Build full URL from path."""
        return f"{BASE_URL}{path}"

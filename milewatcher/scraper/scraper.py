import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class Scraper(ABC):
    """
    Abstract class defining the contract for a scraper.
    All concrete implementations must inherit from this class
    and implement the 'extract_posts' and 'extract_post_content' methods.
    """

    def __init__(self, url: str, source_name: str):
        self._url = url
        self._source_name = source_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.logger = logging.getLogger(self.__class__.__name__)
        logger.debug(f"Scraper initialized for {self.source_name}")


    @property
    def source_name(self) -> str:
        """Read-only property for the source's name."""
        return self._source_name

    @abstractmethod
    def extract_posts(self) -> list[dict]:
        """
        Abstract method to extract posts from a specific source.
        Must be implemented by concrete classes.
        Returns a list of dictionaries, where each dictionary contains
        'title' and 'link' of the post.
        """
        pass

    @abstractmethod
    def extract_post_content(self, post_url: str) -> str:
        """
        Abstract method to extract the main textual content from a single post URL.
        Must be implemented by concrete classes.
        Returns the extracted content as a single string.
        """
        pass

    def _fetch_html_from_url(self, target_url: str) -> BeautifulSoup | None:
        """
        Helper method to make the HTTP request and parse the HTML from a given URL.
        """
        self.logger.debug(f"Accessing URL: {target_url}")
        try:
            response = requests.get(target_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP request error for {target_url}: {e}", exc_info=True)
            return None
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during HTML fetch from {target_url}: {e}", exc_info=True)
            return None

import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import logging

# Import the DatabaseManager from the separate file
from database_manager import DatabaseManager

# --- Logging Configuration ---
# Basic configuration for logging to console and a file
logging.basicConfig(
    level=logging.INFO, # Set the default logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(), # Log to console
        logging.FileHandler('app_log.log') # Log to a file
    ]
)

# Get a logger for the main module
logger = logging.getLogger(__name__)

class PostExtractor(ABC):
    """
    Abstract class defining the contract for post extractors.
    All concrete implementations must inherit from this class
    and implement the 'extract_posts' method.
    """

    def __init__(self, url: str):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.logger = logging.getLogger(self.__class__.__name__) # Logger for each extractor class

    @abstractmethod
    def extract_posts(self) -> list[dict]:
        """
        Abstract method to extract posts from a specific source.
        Must be implemented by concrete classes.
        Returns a list of dictionaries, where each dictionary contains
        'title' and 'link' of the post.
        """
        pass

    def _fetch_html(self) -> BeautifulSoup | None:
        """
        Helper method to make the HTTP request and parse the HTML.
        """
        self.logger.info(f"Accessing URL: {self.url}")
        try:
            response = requests.get(self.url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP request error for {self.url}: {e}", exc_info=True)
            return None
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during HTML fetch from {self.url}: {e}", exc_info=True)
            return None

class PassageiroDePrimeiraPostExtractor(PostExtractor):
    """
    Concrete implementation of PostExtractor for the Passageiro de Primeira website.
    Defines the specific logic to extract posts from the promotions section.
    """
    def __init__(self):
        super().__init__(url='https://passageirodeprimeira.com/categorias/promocoes/')
        self.source_name = "Passageiro de Primeira"
        self.base_url = "https://passageirodeprimeira.com" # Managed in the subclass

    def extract_posts(self) -> list[dict]:
        """
        Extracts titles and links of posts from the Passageiro de Primeira website.
        """
        self.logger.info("Starting post extraction for Passageiro de Primeira.")
        soup = self._fetch_html()
        if not soup:
            self.logger.error("Failed to fetch HTML content. Cannot extract posts.")
            return []

        posts = []
        promotions_section = soup.find('div', {'data-term': 'promocoes'})

        if not promotions_section:
            self.logger.warning("Section 'promocoes' (data-term=\"promocoes\") not found in HTML. Searching in the entire document.")
            target_scope = soup
        else:
            target_scope = promotions_section
            self.logger.info("Section 'promocoes' found. Searching for posts...")

        h1_titles = target_scope.find_all('h1', class_='article--title')

        if not h1_titles:
            self.logger.warning("No <h1 class=\"article--title\"> elements found. Please check the page structure.")
            return []

        for h1_tag in h1_titles:
            link_tag = h1_tag.find('a', href=True)

            if link_tag:
                link = link_tag.get('href')
                title = link_tag.get_text(strip=True)

                if link and not link.startswith(('http://', 'https://')):
                    link = self.base_url + link

                if title and title.strip() != '':
                    posts.append({'title': title, 'link': link})
        self.logger.info(f"Finished extraction for Passageiro de Primeira. Found {len(posts)} posts.")
        return posts

if __name__ == "__main__":
    # Instantiate the DatabaseManager
    db_manager = DatabaseManager()

    # Instantiate the Passageiro de Primeira extractor
    passageiro_de_primeira_extractor = PassageiroDePrimeiraPostExtractor()

    # Get or create the source ID for Passageiro de Primeira
    source_id = db_manager.get_or_create_source_id(
        passageiro_de_primeira_extractor.source_name,
        passageiro_de_primeira_extractor.base_url
    )

    if source_id != -1: # Proceed only if source ID was successfully obtained
        found_posts = passageiro_de_primeira_extractor.extract_posts()

        if found_posts:
            logger.info(f"Extracted {len(found_posts)} posts from {passageiro_de_primeira_extractor.source_name}. Attempting to save to DB.")
            # Display the found posts (optional, for debugging/verification)
            # for i, post in enumerate(found_posts):
            #     logger.debug(f"{i+1}. Title: {post['title']}\n    Link: {post['link']}")

            # Save the extracted posts to the database, associated with the source ID
            db_manager.insert_posts(source_id, found_posts)
        else:
            logger.info(f"No posts found from {passageiro_de_primeira_extractor.source_name} or an issue occurred during extraction.")
    else:
        logger.critical("Failed to get or create source ID. Cannot proceed with post insertion.")

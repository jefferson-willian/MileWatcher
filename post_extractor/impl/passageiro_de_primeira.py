import logging
import requests
from bs4 import BeautifulSoup

from ..post_extractor import PostExtractor

# Logger for this specific extractor
logger = logging.getLogger(__name__)

class PassageiroDePrimeiraPostExtractor(PostExtractor):
    """
    Concrete implementation of PostExtractor for the Passageiro de Primeira website.
    Defines the specific logic to extract posts from the promotions section.
    """
    def __init__(self):
        # Pass only url and source_name to the parent class constructor
        super().__init__(
            url='https://passageirodeprimeira.com/categorias/promocoes/',
            source_name="Passageiro de Primeira"
        )
        # self.base_url is now automatically inferred and available from the parent class.

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

                # Use self.base_url from the parent class (now inferred)
                if link and not link.startswith(('http://', 'https://')):
                    link = self.base_url + link

                if title and title.strip() != '':
                    posts.append({'title': title, 'link': link})
        self.logger.info(f"Finished extraction for Passageiro de Primeira. Found {len(posts)} posts.")
        return posts

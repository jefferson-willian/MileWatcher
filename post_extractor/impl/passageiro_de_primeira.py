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
        super().__init__(
            url='https://passageirodeprimeira.com/categorias/promocoes/',
            source_name="Passageiro de Primeira"
        )

    def extract_posts(self) -> list[dict]:
        """
        Extracts titles and links of posts from the Passageiro de Primeira website.
        """

        self.logger.info("Starting post extraction for Passageiro de Primeira.")

        soup = self._fetch_html_from_url(self._url)
        if not soup:
            self.logger.error("Failed to fetch HTML content. Cannot extract posts.")
            return []

        promotions_section = soup.find('div', {'data-term': 'promocoes'})

        if not promotions_section:
            self.logger.error("Section 'promocoes' (data-term=\"promocoes\") not found in HTML. Please check the page structure.")
            return []

        self.logger.info("Section 'promocoes' found. Searching for posts...")

        h1_titles = promotions_section.find_all('h1', class_='article--title')

        if not h1_titles:
            self.error.warning("No <h1 class=\"article--title\"> elements found. Please check the page structure.")
            return []

        posts = []
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

    def extract_post_content(self, post_url: str) -> str:
        """
        Extracts the main textual content from a single post URL on Passageiro de Primeira.
        Assumes the main content is within a <div> with class 'single-content'.
        """
        self.logger.info(f"Extracting content from post URL: {post_url}")
        soup = self._fetch_html_from_url(post_url) # Uses the new helper for specific post URL
        if not soup:
            self.logger.error(f"Failed to fetch HTML content for post URL: {post_url}. Cannot extract content.")
            return ""

        # Based on inspection, the main article content is often within a div with class 'single-content'
        content_div = soup.find('div', class_='single-content')

        if content_div:
            # Get all text, strip extra whitespace, and join paragraphs with newlines
            content_text = content_div.get_text(separator='\n', strip=True)
            self.logger.info(f"Successfully extracted content from {post_url} (length: {len(content_text)}).")
            return content_text
        else:
            self.logger.warning(f"Could not find main content div (class 'single-content') for {post_url}.")
            return ""

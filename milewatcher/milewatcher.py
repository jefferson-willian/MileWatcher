import logging
import sys

from milewatcher.common.logger import AppLogger
from milewatcher.database.database_manager import DatabaseManager
from milewatcher.scraper.sources.passageiro_de_primeira import PassageiroDePrimeiraScraper

# Configure the logger for the application
logger = AppLogger.get_logger(__name__)

class MileWatcher:
    """
    Main class to manage the process of extracting and analyzing
    promotion posts from various sources.
    """

    def __init__(self):
        """
        Initializes the MileWatcher application.
        """
        self._db_manager = DatabaseManager()
        self._scrapers = [PassageiroDePrimeiraScraper()]
        logger.info(f"MileWatcher initialized with {len(self._scrapers)} scraper(s)")

    def run_post_extraction_phase(self):
        """
        Executes the post extraction phase for all configured sources.
        """
        for scraper in self._scrapers:
            source_name = scraper.source_name
            logger.info(f"Starting post extraction for source: {source_name}")

            source_id = self._db_manager.get_or_create_source_id(source_name)

            if source_id == -1:
                logger.critical(f"Failed to get or create source ID for {source_name}")
                continue

            try:
                found_posts = scraper.extract_posts()

                if found_posts:
                    logger.info(f"Extracted {len(found_posts)} posts")
                    self._db_manager.insert_posts(source_id, found_posts)
                    logger.info(f"New posts saved to the database")
                else:
                    logger.warning(f"No posts found from {source_name}.")
            except Exception as e:
                logger.error(f"Error during post extraction for {source_name}: {e}", exc_info=True)

            logger.info("-" * 50) # Horizontal line
        logger.info("Post extraction completed for all sources.")

    def run_content_analysis_phase(self):
        """
        Executes the content extraction and analysis phase for each post to determine relevance.
        """
        logger.info("Starting content analysis phase.")
        # Define the generic promotion description for relevance check (if applicable in the future)
        # generic_promo_description = "a miles transfer promotion from Itaú bank to Latam"

        for scraper in self._scrapers:
            source_name = scraper.source_name
            logger.info(f"Starting content extraction and relevance analysis for posts from source: {source_name}")

            source_id = self._db_manager.get_or_create_source_id(source_name)
            if source_id == -1:
                logger.critical(f"Failed to get or create source ID for {source_name}. Skipping content analysis for this source.")
                continue

            try:
                # Get posts that need content processing and relevance assessment
                posts_for_processing = self._db_manager.get_posts_for_content_processing(source_id)

                if posts_for_processing:
                    logger.info(f"Found {len(posts_for_processing)} posts from {source_name} requiring content analysis.")

                    for post in posts_for_processing:
                        post_id = post['id']
                        post_url = post['link'] # Use 'link' as the URL for content extraction

                        logger.debug(f"Processing content for post ID: {post_id}, URL: {post_url}")

                        extracted_content = None
                        is_content_relevant = None # Initialize as None (unknown)

                        try:
                            # Extract the full content from the post's URL
                            extracted_content = scraper.extract_post_content(post_url)

                            if extracted_content:
                                logger.info(f"Content extracted for post ID: {post_id}. Now determining relevance.")
                                # TODO: Implement actual relevance analysis logic here
                                # For now, kept as False, as per the original.
                                is_content_relevant = False
                                logger.info(f"Post ID: {post_id} determined as relevant: {is_content_relevant}.")
                            else:
                                logger.error(f"Could not extract content for post ID: {post_id} from URL: {post_url}.")

                            # Update the database with relevance status
                            self._db_manager.update_post_relevance_status(post_id, is_content_relevant)
                            logger.info(f"Database updated for post ID: {post_id} with relevance: {is_content_relevant}.")

                        except Exception as e:
                            logger.error(f"Error during content extraction/relevance analysis for post ID {post_id} (URL: {post_url}): {e}", exc_info=True)
                            # In case of error, mark as not relevant
                            self._db_manager.update_post_relevance_status(post_id, False) # Mark as not relevant on error
                else:
                    logger.info(f"No posts found from {source_name} that require content analysis.")
            except Exception as e:
                logger.error(f"Error retrieving posts for content analysis for {source_name}: {e}", exc_info=True)

            logger.info(f"Finished content analysis for source: {source_name}")
            logger.info("-" * 50) # Horizontal line
        logger.info("Content analysis phase completed.")

    def run(self):
        """
        Executes all phases of the scraping and analysis process.
        """
        logger.info("Application started.")
        logger.info(f"Configured {len(self._scrapers)} scraper(s) to run.")

        self.run_post_extraction_phase()
        self.run_content_analysis_phase()
        
        logger.info("All scrapers processed. Application finished.")

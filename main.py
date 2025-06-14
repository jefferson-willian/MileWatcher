import logging

from database.database_manager import DatabaseManager
from scraper.sources.passageiro_de_primeira import PassageiroDePrimeiraScraper

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app_log.log')
    ]
)

logger = logging.getLogger(__name__)

def _run_post_extraction_phase(db_manager: DatabaseManager, scrapers: list):
    """
    Extracts promotion posts.
    """
    for scraper in scrapers:
        source_name = scraper.source_name
        logger.info(f"Starting post extraction for source: {source_name}")

        source_id = db_manager.get_or_create_source_id(source_name)

        if source_id == -1:
            logger.critical(f"Failed to get or create source ID for {source_name}. Cannot proceed with post insertion.")
            continue

        try:
            found_posts = scraper.extract_posts()

            if found_posts:
                logger.info(f"Extracted {len(found_posts)} posts from {source_name}. Attempting to save to DB.")
                db_manager.insert_posts(source_id, found_posts)
            else:
                logger.info(f"No new posts found from {source_name} or an issue occurred during extraction.")
        except Exception as e:
            logger.error(f"Error during post extraction for {source_name}: {e}", exc_info=True)

        logger.info(f"Finished metadata extraction for source: {source_name}")
        logger.info("-" * 50) # Horizontal line

def _run_content_analysis_phase(db_manager: DatabaseManager, scrapers: list):
    """
    Extracts and analyzes content of each post to determine relevance.
    """

    # Define the generic promotion description for relevance check
    generic_promo_description = "a miles transfer promotion from Itaú bank to Latam"

    for scraper in scrapers:
        source_name = scraper.source_name
        logger.info(f"Starting content extraction and relevance analysis for posts from source: {source_name}")

        source_id = db_manager.get_or_create_source_id(source_name)
        if source_id == -1:
            logger.critical(f"Failed to get or create source ID for {source_name}. Skipping content analysis for this source.")
            continue

        try:
            # Get posts that need content processing and relevance assessment
            posts_for_processing = db_manager.get_posts_for_content_processing(source_id)

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
                            is_content_relevant = False
                            logger.info(f"Post ID: {post_id} determined as relevant: {is_content_relevant}.")
                        else:
                            logger.error(f"Could not extract content for post ID: {post_id} from URL: {post_url}.")

                        # Update the database with relevance status and processed_at timestamp
                        db_manager.update_post_relevance_status(post_id, is_content_relevant)
                        logger.info(f"Database updated for post ID: {post_id} with relevance: {is_content_relevant}.")

                    except Exception as e:
                        logger.error(f"Error during content extraction/relevance analysis for post ID {post_id} (URL: {post_url}): {e}", exc_info=True)
                        # In case of error, mark as not relevant
                        db_manager.update_post_relevance_status(post_id, False) # Mark as not relevant on error
            else:
                logger.info(f"No posts found from {source_name} that require content analysis.")
        except Exception as e:
            logger.error(f"Error retrieving posts for content analysis for {source_name}: {e}", exc_info=True)

        logger.info(f"Finished content analysis for source: {source_name}")
        logger.info("-" * 50) # Horizontal line

if __name__ == "__main__":
    logger.info("Application started.")

    db_manager = DatabaseManager()

    scrapers = [
        PassageiroDePrimeiraScraper(),
    ]

    logger.info(f"Configured {len(scrapers)} scraper(s) to run.")

    _run_post_extraction_phase(db_manager, scrapers)
    _run_content_analysis_phase(db_manager, scrapers)
    
    logger.info("All scrapers processed. Application finished.")

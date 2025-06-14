import logging

from database_manager import DatabaseManager
from post_extractor_passageiro_de_primeira import PassageiroDePrimeiraPostExtractor

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app_log.log')
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Post extraction started.")

    db_manager = DatabaseManager()

    extractors = [
        PassageiroDePrimeiraPostExtractor(),
    ]

    logger.info(f"Configured {len(extractors)} extractor(s) to run.")

    for extractor in extractors:
        source_name = extractor.source_name
        
        logger.info(f"--- Starting processing for source: {source_name} ---")

        # Get or create the source ID for the current extractor
        source_id = db_manager.get_or_create_source_id(source_name)

        if source_id != -1:
            found_posts = extractor.extract_posts()

            if found_posts:
                logger.info(f"Extracted {len(found_posts)} posts from {source_name}. Attempting to save to DB.")
                db_manager.insert_posts(source_id, found_posts)
            else:
                logger.info(f"No new posts found from {source_name} or an issue occurred during extraction.")
        else:
            logger.critical(f"Failed to get or create source ID for {source_name}. Cannot proceed with post insertion.")
        
        logger.info(f"--- Finished processing for source: {source_name} ---")
        logger.info("-" * 50) # Horizontal line
    
    logger.info("All extractors processed. Post extraction finished.")

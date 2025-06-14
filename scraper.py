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
    logger.info("Application started.")

    db_manager = DatabaseManager()

    # Instantiate the Passageiro de Primeira extractor
    passageiro_de_primeira_extractor = PassageiroDePrimeiraPostExtractor()

    # The db_manager can still access source_name and base_url from the extractor's properties
    source_id = db_manager.get_or_create_source_id(
        passageiro_de_primeira_extractor.source_name, # Accessing the property
        passageiro_de_primeira_extractor.base_url    # Accessing the property
    )

    if source_id != -1:
        found_posts = passageiro_de_primeira_extractor.extract_posts()

        if found_posts:
            logger.info(f"Extracted {len(found_posts)} posts from {passageiro_de_primeira_extractor.source_name}. Attempting to save to DB.")
            db_manager.insert_posts(source_id, found_posts)
        else:
            logger.info(f"No posts found from {passageiro_de_primeira_extractor.source_name} or an issue occurred during extraction.")
    else:
        logger.critical("Failed to get or create source ID. Cannot proceed with post insertion.")
    
    logger.info("Application finished.")

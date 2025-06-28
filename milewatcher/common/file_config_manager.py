import logging
import os
import sqlite3
from datetime import datetime

# Configure logger for this module
logger = logging.getLogger(__name__)

# Define the package root directory location
# This PACKAGE_ROOT is still needed as a base for our file manager
PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class FileConfigManager:
    """
    Manages file paths within the configuration directory, ensuring parent
    directories exist before file operations.
    """
    def __init__(self):
        """
        Initializes the FileManager with a base directory.
        """
        self.base_dir = os.path.abspath(os.path.join(PACKAGE_ROOT, '.config'))
        self._ensure_base_directory_exists()
        logger.debug(f"FileManager initialized with base directory: '{self.base_dir}'")

    def _ensure_base_directory_exists(self):
        """
        Ensures that the base directory exists. Creates it if it does not.
        """
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)
            logger.info(f"Created base directory: '{self.base_dir}'")

    def get_file_path(self, relative_path: str) -> str:
        """
        Constructs the full, absolute path for a given relative file path,
        and ensures all necessary parent directories for that file exist.

        Args:
            relative_path (str): The path to the file relative to the base_dir.

        Returns:
            str: The full absolute path to the file.
        """
        full_path = os.path.join(self.base_dir, relative_path)
        # Ensure the parent directory for the specific file exists
        parent_dir = os.path.dirname(full_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            logger.debug(f"Created parent directory for file: '{parent_dir}'")
        return full_path

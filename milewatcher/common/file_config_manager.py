import logging
import os
import sqlite3
from datetime import datetime

# Configure logger for this module
logger = logging.getLogger(__name__)

# Define the package root directory location
PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class FileConfigManager:
    """
    Manages file paths within the configuration directory, ensuring parent
    directories exist before file operations.
    """
    def __init__(self):
        """
        Initializes the FileConfigManager with a base directory.
        """
        self._base_dir = os.path.abspath(os.path.join(PACKAGE_ROOT, '.config'))
        self._ensure_directory_exists(self._base_dir)
        logger.debug(f"ConfigFileManager initialized with base directory: '{self._base_dir}'")

    def _ensure_directory_exists(self, dir_path: str):
        """
        Ensures that the given directory exists. Creates it if it does not.

        Args:
            dir_path (str): The path to the directory.
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Created directory: '{dir_path}'")

    def get_file_path(self, relative_path: str) -> str:
        """
        Constructs the full, absolute path for a given relative file path,
        and ensures all necessary parent directories for that file exist.

        Args:
            relative_path (str): The path to the file relative to the base_dir.

        Returns:
            str: The full absolute path to the file.
        """
        full_path = os.path.join(self._base_dir, relative_path)
        # Ensure the parent directory for the specific file exists
        self._ensure_directory_exists(os.path.dirname(full_path))
        return full_path

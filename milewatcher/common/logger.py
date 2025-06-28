import logging
import sys

class AppLogger:
    """
    A class to encapsulate the logging configuration for the application.
    """
    _logger_instance = None # To hold the configured logger

    # Define the common base formatter string here
    # This is the part that both console and file formatters will share.
    _BASE_FORMAT_STRING = '%(asctime)s [%(levelname)s] [%(name)s] %(message)s'

    @classmethod
    def setup_logging(cls):
        """
        Configures the root logger with specific handlers and formatters.
        Sets up:
        - StreamHandler (console) for INFO level and above.
        - FileHandler (app_log.log) for DEBUG level and above.
        """
        if cls._logger_instance is not None:
            # Logger already configured, return existing instance
            return cls._logger_instance

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG) # Lowest level for the logger to process all messages

        if logger.hasHandlers():
            logger.handlers.clear()

        # --- Define Formatters ---
        console_formatter = logging.Formatter(cls._BASE_FORMAT_STRING)
        file_formatter = logging.Formatter(cls._BASE_FORMAT_STRING)


        # --- Configure Console Handler ---
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO) # Console shows INFO, WARNING, ERROR, CRITICAL
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # --- Configure File Handler ---
        file_handler = logging.FileHandler('/tmp/milewatcher.log')
        file_handler.setLevel(logging.DEBUG) # File captures all levels (DEBUG, INFO, etc.)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        cls._logger_instance = logger # Store the configured logger

        return logger

    @classmethod
    def get_logger(cls, name=None):
        """
        Returns a logger instance. Call setup_logging() first to configure.
        If setup_logging() hasn't been called, it will call it.
        """
        if cls._logger_instance is None:
            cls.setup_logging()
        return logging.getLogger(name)

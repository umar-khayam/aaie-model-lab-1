"""Logging configuration for the application."""
import logging
import logging.handlers
import os
from datetime import datetime
import sys

def setup_logging():
    """Configure logging for the application."""
    try:
        # Create logs directory if it doesn't exist
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        log_dir = os.path.join(current_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)

        # Generate log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"api_{timestamp}.log")

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | aaie-api | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set up file handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(logging.INFO)

        # Set up console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(detailed_formatter)
        console_handler.setLevel(logging.INFO)

        # Create application logger
        logger = logging.getLogger("aaie-api")
        logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        logger.handlers.clear()
        
        # Add our handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Prevent log propagation to avoid duplicate logs
        logger.propagate = False

        # Log the initialization
        logger.info(f"Logging initialized. Writing to: {log_file}")
        
        return logger
    except Exception as e:
        # If something goes wrong, make sure we at least have console output
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | aaie-api | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logger = logging.getLogger("aaie-api")
        logger.error(f"Failed to initialize file logging: {str(e)}", exc_info=True)
        return logger

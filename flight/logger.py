"""
Logger Module

This module defines a singleton Logger class that provides a unified logging interface across
different modules within flight software. The logger can ensure all logging messages, regardless 
of the source module, are directed to the same output locations, both console and file.
The logger supports configurable logging levels and can direct logs to both the console and a specified
log file in append mode. 

Example Usage:
    from flight import Logger
    logger = Logger.get_logger()
    logger.info("This is an info message")
"""
import logging
import os

class Logger:
    _instance = None
    logger = None
    log_file_path = None

    @classmethod
    def _get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Private initializer to prevent multiple instances."""
        if self.__class__._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__class__._instance = self

    @classmethod
    def configure(cls, log_file='log/demo_system.log', log_level=logging.INFO):
        """Configures the class logger with specific handlers and levels."""
        cls.log_file_path = os.path.join(os.getcwd(), log_file)
        # Create directory for log file if it does not exist
        if not os.path.exists(os.path.dirname(cls.log_file_path)):
            os.makedirs(os.path.dirname(cls.log_file_path))

        # Set up the logger
        cls.logger = logging.getLogger("AppLogger")
        cls.logger.setLevel(log_level)  # Set the overall minimum logging level
        cls.logger.handlers = []  # Clear existing handlers

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(cls.log_file_path, mode='a')  # Append mode
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(log_level)

        # Create formatters and add them to handlers
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        cls.logger.addHandler(c_handler)
        cls.logger.addHandler(f_handler)

    @classmethod
    def get_logger(cls):
        """Returns the configured logger instance."""
        if cls.logger is None:
            cls.configure()
        return cls.logger

    @classmethod
    def clear_log(cls):
        """Clears all log entries by truncating the log file."""
        try:
            with open(cls.log_file_path, 'w') as file:
                pass
            cls.logger.info("Log file initialized.")
        except Exception as e:
            cls.logger.error(f"Failed to clear log file: {e}")

# Default configuration upon module load (can be reconfigured elsewhere in the code)
Logger.configure(log_file='log/demo_system.log', log_level=logging.DEBUG)

"""
Logger Module

This module defines a singleton Logger class that provides a unified logging interface across
different modules within flight software. The logger can ensure all logging messages, regardless 
of the source module, are directed to the same output locations, both console and file.
The logger supports configurable logging levels and can direct logs to both the console and a specified
log file in append mode. 

Example Usage:
    from flight import logger_instance
    logger = logger_instance.get_logger()
    logger.info("This is an info message")
"""

import logging
import os

class SingletonType(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger:
    def __init__(self, log_file='error.log', log_level=logging.INFO):
        self.log_file_path = log_file
        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(log_level)  # Set the overall minimum logging level
        self.configure(log_file, log_level)

    def configure(self, log_file, log_level):
        """Configures the logger with specific handlers and levels."""
        # Creates directory for log file 
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(log_file, mode='a')  # Append mode
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(log_level)  

        # Create formatters and add them to handlers
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)

    def get_logger(self):
        """Returns the configured logger."""
        return self.logger
    
    def clear_log(self):
        """Clears all log entries by truncating the log file."""
        try:
            with open(self.log_file_path, 'w') as file:
                pass
            self.logger.info("Log file initialized.")
        except Exception as e:
            self.logger.error(f"Failed to clear log file: {e}")

# Instance to be imported
logger_instance = Logger(log_file='log/demo_system.log', log_level=logging.DEBUG) # for demo
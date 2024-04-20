import logging
import os

class Logger:
    def __init__(self, log_file='error.log', log_level=logging.INFO):
        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(log_level)  # Set the overall minimum logging level
        self.configure(log_file, log_level)

    def configure(self, log_file, log_level):
        """Configures the logger with specific handlers and levels."""
        # Ensure the directory for the log file exists
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(log_file, mode='a')  # Append mode
        c_handler.setLevel(logging.INFO)  # Console handler level
        f_handler.setLevel(log_level)  # File handler level, as specified

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
import os
import sys
from loguru import logger

# The logger is imported by other modules, but not configured until setup_logger() is called.
# We remove the default handler immediately to prevent any logging before configuration.
logger.remove()

def setup_logger():
    """Configures the loguru logger for the application."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except OSError as e:
            print(f"Error creating log directory: {e}", file=sys.stderr)

    # Add console handler (stderr) with color
    # logger.add(
    #     sys.stderr, 
    #     format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    # )

    # Add file handler, wiping the file on each new session (mode="w")
    log_file_path = os.path.join(log_dir, "hopon.log")
    logger.add(
        log_file_path, 
        level="INFO", 
        mode="w", # "w" for write, truncates the file at startup.
        format="{time} | {level} | {name}:{function}:{line} - {message}" # Simpler format for file
    )
    
    logger.info("Logger has been configured for the new session.")

# Other modules will import this logger instance
__all__ = ["logger", "setup_logger"]

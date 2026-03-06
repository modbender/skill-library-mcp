"""NIMA logging configuration - singleton logger with file + console handlers."""

import logging
import os
import sys
from pathlib import Path
from threading import Lock


class NIMALogger:
    """Singleton logger class that provides loggers with file and console handlers."""
    
    _instance = None
    _lock = Lock()
    _loggers = {}  # Cache of loggers by name
    
    def __init__(self):
        raise RuntimeError("Use get_instance() to get NIMALogger singleton")
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of NIMALogger."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls.__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the logger configuration."""
        # Determine log directory
        nima_data_dir = os.environ.get('NIMA_DATA_DIR')
        if nima_data_dir:
            log_dir = Path(nima_data_dir) / 'logs'
        else:
            log_dir = Path.home() / '.nima' / 'logs'
        
        # Create log directory if it doesn't exist
        log_dir.mkdir(parents=True, exist_ok=True)
        
        self._log_dir = log_dir
        self._loggers = {}
        
        # Get log level from environment variable
        default_level = os.environ.get('NIMA_LOG_LEVEL', 'INFO').upper()
        self._default_level = getattr(logging, default_level, logging.INFO)
    
    def get_logger(self, name: str, level: str = None) -> logging.Logger:
        """
        Returns a logger that writes to ~/.nima/logs/{name}.log and console.
        
        Args:
            name: The name of the logger (also used as log filename)
            level: Optional log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
        Returns:
            A configured logger instance
        """
        # Return cached logger if exists
        if name in self._loggers:
            logger = self._loggers[name]
            if level:
                logger.setLevel(getattr(logging, level.upper(), logging.INFO))
            return logger
        
        # Create new logger
        logger = logging.getLogger(name)
        
        # Set level
        if level:
            logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        else:
            logger.setLevel(self._default_level)
        
        # Avoid duplicate handlers
        if logger.handlers:
            self._loggers[name] = logger
            return logger
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # File handler
        log_file = self._log_dir / f'{name}.log'
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except (OSError, IOError) as e:
            # If we can't create file handler, continue with console only but warn user
            print(f"WARNING: Could not create log file handler for {log_file}: {e}", file=sys.stderr)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Cache the logger
        self._loggers[name] = logger
        
        return logger


# Module-level convenience function
def get_logger(name: str, level: str = None) -> logging.Logger:
    """
    Get a logger instance that writes to file and console.
    
    Args:
        name: The name of the logger
        level: Optional log level override
    
    Returns:
        A configured logger instance
    """
    instance = NIMALogger.get_instance()
    return instance.get_logger(name, level)

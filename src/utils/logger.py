import logging

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger for the given module name.
    
    Args:
        name: Name of the module (typically __name__)
        
    Returns:
        A logging instance configured to output to the console.
    """
    logger = logging.getLogger(name)
    
    # Only configure if no handlers are present to avoid duplicate logs
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        
        logger.addHandler(ch)
        
    return logger

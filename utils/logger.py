# logger.py
import logging  # This is Python's built-in logging module

# Create a logger object with a specific name (helps identify logs from our project)
logger = logging.getLogger("PlaywrightAutomation")

# Set the logging level
# This tells Python: "Only show logs that are this level or higher"
# DEBUG < INFO < WARNING < ERROR < CRITICAL
logger.setLevel(logging.DEBUG)

# Create a file handler to write logs into a file
# 'a' means append mode — so logs get added at the end, not overwrite old logs
file_handler = logging.FileHandler("automation.log", mode="a")

# Create a log format (how each log line will look)
# Example output: 2025-08-14 10:30:15 - PlaywrightAutomation - INFO - Browser started
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Apply the formatter to our file handler
file_handler.setFormatter(formatter)

# Add the file handler to our logger so it knows where to write
logger.addHandler(file_handler)

# Also add a console handler so logs appear in the terminal too
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

import logging
from datetime import datetime
import sqlite3
import os

# Ensure the directory for the database and log files exists
BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(BASE_DIR, 'database.db')

class Logger:
    LOGGER_NAME = 'BeaconSimulatorLogger'
    LOG_FILE = os.path.join(BASE_DIR, 'BeaconSimulator.log')

    _instance = None  # Holds the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self, level=logging.INFO):
        if not hasattr(self, '_initialized') or not self._initialized:
            self.logger = logging.getLogger(self.LOGGER_NAME)
            self.logger.setLevel(level)

            # Check if the log file exists and delete it
            if os.path.exists(self.LOG_FILE):
                os.remove(self.LOG_FILE)

            # Setup the file handler
            file_handler = logging.FileHandler(self.LOG_FILE)
            file_handler.setLevel(level)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            self._setup_db()
            self._initialized = True

    def _setup_db(self):
        with self.get_db_connection() as conn:
            cursor = conn.cursor()

            # Drop the logs table to erase log history and recreate it
            cursor.execute('''DROP TABLE IF EXISTS logs''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                level TEXT,
                message TEXT)''')
            conn.commit()

    def get_db_connection(self):
        return sqlite3.connect(DATABASE, check_same_thread=False)

    def log_to_db(self, level, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Logging to db: {timestamp} - {level} - {message}")
        
        with self.get_db_connection() as conn:
            conn.execute('INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?)',
                         (timestamp, level, message))
            conn.commit()

    def debug(self, message):
        self.logger.debug(message)
        self.log_to_db('DEBUG', message)

    def info(self, message):
        self.logger.info(message)
        self.log_to_db('INFO', message)

    def warning(self, message):
        self.logger.warning(message)
        self.log_to_db('WARNING', message)

    def error(self, message):
        self.logger.error(message)
        self.log_to_db('ERROR', message)

    def critical(self, message):
        self.logger.critical(message)
        self.log_to_db('CRITICAL', message)
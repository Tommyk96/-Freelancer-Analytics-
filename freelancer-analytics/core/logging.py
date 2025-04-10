import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

LOG_DIR = Path("logs")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

class QueryLogger:
    def __init__(self):
        LOG_DIR.mkdir(exist_ok=True)
        log_file = LOG_DIR / f"queries_{datetime.now().strftime('%Y%m%d')}.log"
        
        self.logger = logging.getLogger("freelancer_analytics")
        self.logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        self.logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        self.logger.addHandler(console_handler)
    
    def log_query(self, query: str, response: str, metadata: Dict[str, Any]) -> None:
        """Логирует запрос и ответ"""
        log_entry = {
            "query": query,
            "response": response,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(f"Query: {query}")
        self.logger.info(f"Response: {response[:200]}...")

    def log(self, query: str, status: str, message: str = None) -> None:
        """Логирует запрос с указанным статусом и опциональным сообщением"""
        log_message = f"Query: {query} | Status: {status}"
        if message:
            log_message += f" | Message: {message}"
        if status == "error":
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)
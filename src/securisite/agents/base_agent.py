"""
Base agent class for SecuriSite-IA multi-agent system
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseSecuriSiteAgent(ABC):
    """Base class for all security analysis agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        pass
    
    def log_info(self, message: str):
        self.logger.info(f"{self.name}: {message}")
    
    def log_error(self, message: str):
        self.logger.error(f"{self.name}: {message}")
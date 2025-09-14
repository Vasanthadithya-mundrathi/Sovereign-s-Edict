"""
Base classes for modular components in Sovereign's Edict
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

class BaseModule(ABC):
    """
    Abstract base class for all modules
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the module
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """
        Process data through the module
        Args:
            data: Input data to process
        Returns:
            Processed data
        """
        pass
    
    def cleanup(self) -> None:
        """
        Cleanup resources used by the module
        """
        pass

class IngestorModule(BaseModule):
    """
    Base class for data ingestor modules
    """
    @abstractmethod
    def can_handle(self, source_type: str) -> bool:
        """
        Check if this ingestor can handle the given source type
        Args:
            source_type: Type of data source (e.g., 'youtube', 'csv', 'pdf')
        Returns:
            bool: True if can handle, False otherwise
        """
        pass
    
    @abstractmethod
    def ingest(self, source: Any) -> List[Dict]:
        """
        Ingest data from source
        Args:
            source: Data source (URL, file path, etc.)
        Returns:
            List of ingested data items
        """
        pass

class ProcessorModule(BaseModule):
    """
    Base class for data processor modules
    """
    @abstractmethod
    def can_process(self, data_type: str) -> bool:
        """
        Check if this processor can handle the given data type
        Args:
            data_type: Type of data to process
        Returns:
            bool: True if can process, False otherwise
        """
        pass
    
    @abstractmethod
    def process_data(self, data: List[Dict]) -> List[Dict]:
        """
        Process data
        Args:
            data: Data to process
        Returns:
            Processed data
        """
        pass

class ExporterModule(BaseModule):
    """
    Base class for data exporter modules
    """
    @abstractmethod
    def can_export(self, format_type: str) -> bool:
        """
        Check if this exporter can handle the given format type
        Args:
            format_type: Export format type (e.g., 'pdf', 'csv', 'json')
        Returns:
            bool: True if can export, False otherwise
        """
        pass
    
    @abstractmethod
    def export(self, data: Any, output_path: str) -> bool:
        """
        Export data to specified format
        Args:
            data: Data to export
            output_path: Path to export to
        Returns:
            bool: True if successful, False otherwise
        """
        pass

# Plugin registry
class ModuleRegistry:
    """
    Registry for managing modules and plugins
    """
    def __init__(self):
        self.ingestors = {}
        self.processors = {}
        self.exporters = {}
        self.analyzers = {}
    
    def register_ingestor(self, name: str, ingestor: IngestorModule) -> None:
        """Register an ingestor module"""
        self.ingestors[name] = ingestor
    
    def register_processor(self, name: str, processor: ProcessorModule) -> None:
        """Register a processor module"""
        self.processors[name] = processor
    
    def register_exporter(self, name: str, exporter: ExporterModule) -> None:
        """Register an exporter module"""
        self.exporters[name] = exporter
    
    def get_ingestor(self, name: str) -> Optional[IngestorModule]:
        """Get registered ingestor by name"""
        return self.ingestors.get(name)
    
    def get_processor(self, name: str) -> Optional[ProcessorModule]:
        """Get registered processor by name"""
        return self.processors.get(name)
    
    def get_exporter(self, name: str) -> Optional[ExporterModule]:
        """Get registered exporter by name"""
        return self.exporters.get(name)
    
    def get_all_ingestors(self) -> Dict[str, IngestorModule]:
        """Get all registered ingestors"""
        return self.ingestors.copy()
    
    def get_all_processors(self) -> Dict[str, ProcessorModule]:
        """Get all registered processors"""
        return self.processors.copy()
    
    def get_all_exporters(self) -> Dict[str, ExporterModule]:
        """Get all registered exporters"""
        return self.exporters.copy()

# Global module registry
module_registry = ModuleRegistry()
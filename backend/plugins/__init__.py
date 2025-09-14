"""
Plugin system for Sovereign's Edict
"""
import os
import importlib
import logging
import sys
import os
from typing import Dict, List, Optional, Type

# Add the parent directory to the path to enable absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Use absolute imports
from backend.modules.base import BaseModule, IngestorModule, ProcessorModule, ExporterModule, ModuleRegistry

logger = logging.getLogger(__name__)

class PluginManager:
    """
    Manages loading and registering plugins
    """
    
    def __init__(self, plugins_dir: str = None):
        # Set the correct plugins directory path
        if plugins_dir is None:
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.realpath(__file__))
            # Go up one level to backend, then into plugins
            self.plugins_dir = os.path.join(os.path.dirname(current_dir), "plugins")
        else:
            self.plugins_dir = plugins_dir
            
        self.loaded_plugins = {}
        self.module_registry = ModuleRegistry()
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in the plugins directory
        Returns:
            List of plugin module names
        """
        plugins = []
        print(f"Looking for plugins in: {self.plugins_dir}")
        print(f"Plugins directory exists: {os.path.exists(self.plugins_dir)}")
        
        if os.path.exists(self.plugins_dir):
            for item in os.listdir(self.plugins_dir):
                plugin_path = os.path.join(self.plugins_dir, item)
                if os.path.isdir(plugin_path) and not item.startswith('__'):
                    plugins.append(item)
                elif item.endswith('.py') and not item.startswith('__'):
                    plugins.append(item[:-3])  # Remove .py extension
        return plugins
    
    def load_plugin(self, plugin_name: str) -> Optional[BaseModule]:
        """
        Load a plugin by name
        Args:
            plugin_name: Name of the plugin to load
        Returns:
            Loaded plugin module or None if failed
        """
        try:
            print(f"Trying to load plugin: {plugin_name}")
            
            # Try to import the plugin
            plugin_module = importlib.import_module(f"backend.plugins.{plugin_name}")
            
            # Look for plugin class
            plugin_class = None
            for attr_name in dir(plugin_module):
                attr = getattr(plugin_module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseModule) and attr != BaseModule:
                    # Also check for specific module types
                    if issubclass(attr, IngestorModule) or issubclass(attr, ProcessorModule) or issubclass(attr, ExporterModule):
                        plugin_class = attr
                        break
                    # Fallback to BaseModule check
                    plugin_class = attr
                    break
            
            if plugin_class:
                # Instantiate plugin
                plugin_instance = plugin_class()
                
                # Initialize plugin
                if plugin_instance.initialize():
                    self.loaded_plugins[plugin_name] = plugin_instance
                    
                    # Register the plugin with the module registry
                    if hasattr(plugin_instance, 'can_handle'):
                        # It's likely an ingestor, register it
                        self.module_registry.register_ingestor(plugin_name, plugin_instance)
                    elif hasattr(plugin_instance, 'can_process'):
                        # It's likely a processor, register it
                        self.module_registry.register_processor(plugin_name, plugin_instance)
                    elif hasattr(plugin_instance, 'can_export'):
                        # It's likely an exporter, register it
                        self.module_registry.register_exporter(plugin_name, plugin_instance)
                    
                    logger.info(f"Successfully loaded plugin: {plugin_name}")
                    return plugin_instance
                else:
                    logger.error(f"Failed to initialize plugin: {plugin_name}")
            else:
                logger.error(f"No valid plugin class found in: {plugin_name}")
                
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def load_all_plugins(self) -> Dict[str, BaseModule]:
        """
        Load all available plugins
        Returns:
            Dictionary of loaded plugins
        """
        plugin_names = self.discover_plugins()
        loaded_plugins = {}
        
        for plugin_name in plugin_names:
            plugin = self.load_plugin(plugin_name)
            if plugin:
                loaded_plugins[plugin_name] = plugin
        
        return loaded_plugins
    
    def register_plugin_module(self, plugin_name: str, module_type: str, module: BaseModule) -> None:
        """
        Register a plugin module with the module registry
        Args:
            plugin_name: Name of the plugin
            module_type: Type of module ('ingestor', 'processor', 'exporter', 'analyzer')
            module: Module instance to register
        """
        if module_type == 'ingestor':
            self.module_registry.register_ingestor(plugin_name, module)
        elif module_type == 'processor':
            self.module_registry.register_processor(plugin_name, module)
        elif module_type == 'exporter':
            self.module_registry.register_exporter(plugin_name, module)
        elif module_type == 'analyzer':
            self.module_registry.analyzers[plugin_name] = module
        else:
            logger.warning(f"Unknown module type: {module_type}")

# Global plugin manager
plugin_manager = PluginManager()

def initialize_plugins() -> None:
    """
    Initialize all plugins at application startup
    """
    logger.info("Initializing plugins...")
    loaded_plugins = plugin_manager.load_all_plugins()
    logger.info(f"Loaded {len(loaded_plugins)} plugins")

# Plugin development utilities
def create_plugin_template(plugin_name: str, plugin_type: str) -> str:
    """
    Create a template for a new plugin
    Args:
        plugin_name: Name for the new plugin
        plugin_type: Type of plugin ('ingestor', 'processor', 'exporter', 'analyzer')
    Returns:
        Template code as string
    """
    templates = {
        'ingestor': f'''
"""
{plugin_name.title()} Ingestor Plugin
"""
from modules.base import IngestorModule
from typing import List, Dict

class {plugin_name.title()}Ingestor(IngestorModule):
    """
    Ingestor for {plugin_name} data sources
    """
    
    def initialize(self) -> bool:
        """
        Initialize the {plugin_name} ingestor
        """
        # Add initialization code here
        return True
    
    def can_handle(self, source_type: str) -> bool:
        """
        Check if this ingestor can handle the given source type
        """
        return source_type.lower() == "{plugin_name}"
    
    def ingest(self, source: str) -> List[Dict]:
        """
        Ingest data from {plugin_name} source
        """
        # Add ingestion logic here
        return []

# Register the plugin
from modules import module_registry
module_registry.register_ingestor("{plugin_name}", {plugin_name.title()}Ingestor())
''',
        'processor': f'''
"""
{plugin_name.title()} Processor Plugin
"""
from modules.base import ProcessorModule
from typing import List, Dict

class {plugin_name.title()}Processor(ProcessorModule):
    """
    Processor for {plugin_name} data
    """
    
    def initialize(self) -> bool:
        """
        Initialize the {plugin_name} processor
        """
        # Add initialization code here
        return True
    
    def can_process(self, data_type: str) -> bool:
        """
        Check if this processor can handle the given data type
        """
        return data_type.lower() == "{plugin_name}"
    
    def process_data(self, data: List[Dict]) -> List[Dict]:
        """
        Process {plugin_name} data
        """
        # Add processing logic here
        return data

# Register the plugin
from modules import module_registry
module_registry.register_processor("{plugin_name}", {plugin_name.title()}Processor())
''',
        'exporter': f'''
"""
{plugin_name.title()} Exporter Plugin
"""
from modules.base import ExporterModule
from typing import Any

class {plugin_name.title()}Exporter(ExporterModule):
    """
    Exporter for {plugin_name} format
    """
    
    def initialize(self) -> bool:
        """
        Initialize the {plugin_name} exporter
        """
        # Add initialization code here
        return True
    
    def can_export(self, format_type: str) -> bool:
        """
        Check if this exporter can handle the given format type
        """
        return format_type.lower() == "{plugin_name}"
    
    def export(self, data: Any, output_path: str) -> bool:
        """
        Export data to {plugin_name} format
        """
        # Add export logic here
        return True

# Register the plugin
from modules import module_registry
module_registry.register_exporter("{plugin_name}", {plugin_name.title()}Exporter())
'''
    }
    
    return templates.get(plugin_type, f"# Unknown plugin type: {plugin_type}")

# Plugin API endpoints
def get_available_plugins() -> Dict[str, str]:
    """
    Get list of available plugins
    """
    plugin_names = plugin_manager.discover_plugins()
    return {name: "Available" for name in plugin_names}

def get_loaded_plugins() -> Dict[str, str]:
    """
    Get list of loaded plugins
    """
    return {name: type(plugin).__name__ for name, plugin in plugin_manager.loaded_plugins.items()}
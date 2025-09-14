#!/usr/bin/env python3
"""
Debug script for Sovereign's Edict plugins
"""
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

def debug_plugin_loading():
    """Debug plugin loading issues"""
    try:
        # Import the plugin manager
        from backend.plugins import plugin_manager
        
        print("Debugging plugin loading...")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Plugins directory: {plugin_manager.plugins_dir}")
        print(f"Plugins directory exists: {os.path.exists(plugin_manager.plugins_dir)}")
        
        if os.path.exists(plugin_manager.plugins_dir):
            print("Contents of plugins directory:")
            for item in os.listdir(plugin_manager.plugins_dir):
                print(f"  - {item}")
                
                # Check if it's a directory
                item_path = os.path.join(plugin_manager.plugins_dir, item)
                if os.path.isdir(item_path):
                    print(f"    Is directory: True")
                    if os.path.exists(os.path.join(item_path, '__init__.py')):
                        print(f"    Has __init__.py: True")
                    else:
                        print(f"    Has __init__.py: False")
                else:
                    print(f"    Is directory: False")
        
        # Try to discover plugins
        plugins = plugin_manager.discover_plugins()
        print(f"\nDiscovered plugins: {plugins}")
        
        # Try to load each plugin
        for plugin_name in plugins:
            if not plugin_name.startswith('__') and plugin_name != 'test_framework':
                print(f"\nTrying to load plugin: {plugin_name}")
                plugin = plugin_manager.load_plugin(plugin_name)
                if plugin:
                    print(f"  Successfully loaded: {type(plugin).__name__}")
                else:
                    print(f"  Failed to load plugin")
        
        # Check loaded plugins
        loaded_plugins = plugin_manager.loaded_plugins
        print(f"\nLoaded plugins: {len(loaded_plugins)}")
        for name, plugin in loaded_plugins.items():
            print(f"  - {name}: {type(plugin).__name__}")
            
        # Check module registry
        module_registry = plugin_manager.module_registry
        ingestors = module_registry.get_all_ingestors()
        print(f"\nRegistered ingestors: {len(ingestors)}")
        for name, ingestor in ingestors.items():
            print(f"  - {name}: {type(ingestor).__name__}")
        
    except Exception as e:
        print(f"Error debugging plugin loading: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_plugin_loading()
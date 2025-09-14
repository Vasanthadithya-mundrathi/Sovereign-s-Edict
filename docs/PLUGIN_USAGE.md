# Plugin Usage Guide for Sovereign's Edict

## Overview

Sovereign's Edict supports a plugin architecture that allows extending the platform's functionality without modifying the core codebase. This guide explains how to use the existing plugins and create new ones.

## Available Plugins

### Government Database Ingestor
This plugin can ingest data from government consultation databases.

**Usage via API:**
```bash
curl -X POST "http://localhost:8001/ingest/plugin/gov_database" \
     -H "Content-Type: application/json" \
     -d '{"source": "query_or_identifier"}'
```

### Instagram Ingestor
This plugin can ingest comments from Instagram posts. Note that it requires an Instagram API access token to function.

**Configuration:**
To use this plugin, you need to provide an Instagram API access token in the plugin configuration.

**Usage via API:**
```bash
curl -X POST "http://localhost:8001/ingest/plugin/instagram" \
     -H "Content-Type: application/json" \
     -d '{"source": "https://www.instagram.com/p/C1234567890/"}'
```

## API Endpoints

### List Available Plugins
```bash
curl -X GET "http://localhost:8001/plugins"
```

### Ingest Data Using a Plugin
```bash
curl -X POST "http://localhost:8001/ingest/plugin/{plugin_name}" \
     -H "Content-Type: application/json" \
     -d '{"source": "source_identifier"}'
```

## Plugin Development

For information on how to create new plugins, see [Plugin Development Guide](../backend/plugins/README.md).

## Configuration

Plugins can be configured by providing a configuration dictionary when initializing them. The configuration options vary by plugin.

For example, to configure the Instagram plugin with an access token:
```python
config = {
    "access_token": "your_instagram_access_token"
}
```

## Testing Plugins

To test if plugins are working correctly, you can run the provided test scripts:
```bash
python test_plugins.py
```

## Troubleshooting

### Plugin Not Found
If you get a "Plugin not found" error, make sure the plugin is correctly placed in the `backend/plugins/` directory and has the proper structure.

### Initialization Failed
If a plugin fails to initialize, check the plugin's specific requirements (such as API keys) and ensure they are properly configured.

### Import Errors
If you encounter import errors, make sure the plugin files are using absolute imports and that the Python path is correctly set.